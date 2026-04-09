using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using Crypto.Net.Solana.Models;
using Microsoft.Extensions.Options;

namespace Crypto.Net.Solana.Services;

public sealed class SolanaRpcClient
{
    private readonly HttpClient _httpClient;
    private readonly SolanaOptions _options;
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web)
    {
        PropertyNameCaseInsensitive = true,
        WriteIndented = false
    };

    public SolanaRpcClient(HttpClient httpClient, IOptions<SolanaOptions> options)
    {
        _httpClient = httpClient;
        _options = options.Value;
        _httpClient.BaseAddress = new Uri(_options.RpcUrl);
    }

    public async Task<LatestBlockhashResponse> GetLatestBlockhashAsync(CancellationToken ct = default)
    {
        var response = await PostAsync<LatestBlockhashResponse>(
            "getLatestBlockhash",
            new
            {
                commitment = _options.Commitment
            },
            ct);

        return response ?? throw new InvalidOperationException("Missing latest blockhash response.");
    }

    public async Task<SimulateTransactionResponse> SimulateTransactionAsync(
        string signedTransactionBase64,
        CancellationToken ct = default)
    {
        var response = await PostAsync<SimulateTransactionResponse>(
            "simulateTransaction",
            signedTransactionBase64,
            new
            {
                encoding = "base64",
                commitment = _options.Commitment,
                replaceRecentBlockhash = false,
                sigVerify = true
            },
            ct);

        return response ?? throw new InvalidOperationException("Missing simulation response.");
    }

    public async Task<string> SendTransactionAsync(
        string signedTransactionBase64,
        bool skipPreflight = false,
        CancellationToken ct = default)
    {
        var response = await PostAsync<string>(
            "sendTransaction",
            signedTransactionBase64,
            new
            {
                encoding = "base64",
                skipPreflight,
                preflightCommitment = _options.Commitment,
                maxRetries = 3
            },
            ct);

        return response ?? throw new InvalidOperationException("Missing transaction signature.");
    }

    public async Task<TransactionStatusResponse?> GetTransactionAsync(
        string signature,
        CancellationToken ct = default)
    {
        return await PostAsync<TransactionStatusResponse>(
            "getTransaction",
            signature,
            new
            {
                encoding = "json",
                commitment = _options.Commitment,
                maxSupportedTransactionVersion = 0
            },
            ct);
    }

    private async Task<T?> PostAsync<T>(string method, CancellationToken ct = default)
    {
        return await PostAsync<T>(method, Array.Empty<object?>(), ct);
    }

    private async Task<T?> PostAsync<T>(string method, object? param1, CancellationToken ct = default)
    {
        return await PostAsync<T>(method, new[] { param1 }, ct);
    }

    private async Task<T?> PostAsync<T>(string method, object? param1, object? param2, CancellationToken ct = default)
    {
        return await PostAsync<T>(method, new[] { param1, param2 }, ct);
    }

    private async Task<T?> PostAsync<T>(string method, object?[] parameters, CancellationToken ct = default)
    {
        var payload = new RpcRequest
        {
            Method = method,
            Params = parameters
        };

        using var request = new HttpRequestMessage(HttpMethod.Post, string.Empty)
        {
            Content = new StringContent(
                JsonSerializer.Serialize(payload, JsonOptions),
                Encoding.UTF8,
                "application/json")
        };

        using var response = await _httpClient.SendAsync(request, ct);
        response.EnsureSuccessStatusCode();

        var rpcResponse = await response.Content.ReadFromJsonAsync<RpcResponse<T>>(JsonOptions, ct);
        if (rpcResponse is null)
            throw new InvalidOperationException($"No RPC response returned for method '{method}'.");

        if (rpcResponse.Error is not null)
            throw new InvalidOperationException($"RPC error {rpcResponse.Error.Code}: {rpcResponse.Error.Message}");

        return rpcResponse.Result;
    }
}
