using System.Text.Json.Serialization;

namespace Crypto.Net.Solana.Models;

public sealed class RpcRequest
{
    [JsonPropertyName("jsonrpc")]
    public string JsonRpc { get; set; } = "2.0";

    [JsonPropertyName("id")]
    public int Id { get; set; } = 1;

    [JsonPropertyName("method")]
    public string Method { get; set; } = string.Empty;

    [JsonPropertyName("params")]
    public object?[] Params { get; set; } = Array.Empty<object?>();
}

public sealed class RpcResponse<T>
{
    [JsonPropertyName("jsonrpc")]
    public string? JsonRpc { get; set; }

    [JsonPropertyName("result")]
    public T? Result { get; set; }

    [JsonPropertyName("error")]
    public RpcError? Error { get; set; }

    [JsonPropertyName("id")]
    public int Id { get; set; }
}

public sealed class RpcError
{
    [JsonPropertyName("code")]
    public int Code { get; set; }

    [JsonPropertyName("message")]
    public string Message { get; set; } = string.Empty;

    [JsonPropertyName("data")]
    public object? Data { get; set; }
}

public sealed class LatestBlockhashResponse
{
    [JsonPropertyName("context")]
    public RpcContext? Context { get; set; }

    [JsonPropertyName("value")]
    public LatestBlockhashValue? Value { get; set; }
}

public sealed class RpcContext
{
    [JsonPropertyName("slot")]
    public long Slot { get; set; }
}

public sealed class LatestBlockhashValue
{
    [JsonPropertyName("blockhash")]
    public string Blockhash { get; set; } = string.Empty;

    [JsonPropertyName("lastValidBlockHeight")]
    public long LastValidBlockHeight { get; set; }
}

public sealed class SimulateTransactionResponse
{
    [JsonPropertyName("context")]
    public RpcContext? Context { get; set; }

    [JsonPropertyName("value")]
    public SimulateTransactionValue? Value { get; set; }
}

public sealed class SimulateTransactionValue
{
    [JsonPropertyName("err")]
    public object? Err { get; set; }

    [JsonPropertyName("logs")]
    public List<string>? Logs { get; set; }

    [JsonPropertyName("unitsConsumed")]
    public long? UnitsConsumed { get; set; }

    [JsonPropertyName("returnData")]
    public object? ReturnData { get; set; }
}

public sealed class TransactionStatusResponse
{
    [JsonPropertyName("slot")]
    public long Slot { get; set; }

    [JsonPropertyName("blockTime")]
    public long? BlockTime { get; set; }

    [JsonPropertyName("meta")]
    public TransactionMeta? Meta { get; set; }

    [JsonPropertyName("transaction")]
    public object? Transaction { get; set; }

    [JsonPropertyName("version")]
    public object? Version { get; set; }
}

public sealed class TransactionMeta
{
    [JsonPropertyName("err")]
    public object? Err { get; set; }

    [JsonPropertyName("fee")]
    public long Fee { get; set; }

    [JsonPropertyName("logMessages")]
    public List<string>? LogMessages { get; set; }

    [JsonPropertyName("computeUnitsConsumed")]
    public long? ComputeUnitsConsumed { get; set; }
}

public sealed class BroadcastResult
{
    public bool Simulated { get; set; }
    public bool SimulationPassed { get; set; }
    public object? SimulationError { get; set; }
    public List<string> SimulationLogs { get; set; } = new();
    public long? UnitsConsumed { get; set; }
    public string? Signature { get; set; }
    public string? Error { get; set; }
}

public sealed class BatchBroadcastResult
{
    public List<BroadcastResult> Results { get; set; } = new();
    public bool AllSucceeded => Results.All(x => string.IsNullOrWhiteSpace(x.Error) && (x.Signature is not null));
}
