using Crypto.Net.Solana.Models;
using Crypto.Net.Solana.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.Configure<SolanaOptions>(
    builder.Configuration.GetSection("Solana"));

builder.Services.AddHttpClient<SolanaRpcClient>();
builder.Services.AddScoped<SolanaProgramAdapter>();

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();

app.MapGet("/", () => Results.Ok(new
{
    ok = true,
    service = "crypto.net.solana",
    endpoints = new[]
    {
        "GET /rpc/blockhash",
        "POST /program/execute-signed",
        "POST /program/execute-batch",
        "GET /tx/{signature}"
    }
}));

app.MapGet("/rpc/blockhash", async (SolanaRpcClient rpc, CancellationToken ct) =>
{
    var blockhash = await rpc.GetLatestBlockhashAsync(ct);
    return Results.Ok(blockhash);
});

app.MapPost("/program/execute-signed", async (
    SignedTransactionRequest request,
    SolanaProgramAdapter adapter,
    CancellationToken ct) =>
{
    var result = await adapter.ExecuteSignedAsync(
        request.SignedTransactionBase64,
        request.SimulateFirst,
        ct);

    return string.IsNullOrWhiteSpace(result.Error)
        ? Results.Ok(result)
        : Results.BadRequest(result);
});

app.MapPost("/program/execute-batch", async (
    SignedTransactionBatchRequest request,
    SolanaProgramAdapter adapter,
    CancellationToken ct) =>
{
    if (request.SignedTransactionsBase64.Count == 0)
        return Results.BadRequest(new { error = "At least one signed transaction is required." });

    var result = await adapter.ExecuteSignedBatchAsync(
        request.SignedTransactionsBase64,
        request.SimulateFirst,
        request.HaltOnError,
        ct);

    return result.AllSucceeded
        ? Results.Ok(result)
        : Results.BadRequest(result);
});

app.MapGet("/tx/{signature}", async (
    string signature,
    SolanaRpcClient rpc,
    CancellationToken ct) =>
{
    var tx = await rpc.GetTransactionAsync(signature, ct);
    return tx is null ? Results.NotFound() : Results.Ok(tx);
});

app.Run();
