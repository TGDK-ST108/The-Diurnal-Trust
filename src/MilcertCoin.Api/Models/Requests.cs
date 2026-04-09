namespace Crypto.Net.Solana.Models;

public sealed class SignedTransactionRequest
{
    /// <summary>
    /// Fully signed Solana transaction in base64.
    /// </summary>
    public string SignedTransactionBase64 { get; set; } = string.Empty;

    /// <summary>
    /// If true, run simulateTransaction before sendTransaction.
    /// </summary>
    public bool SimulateFirst { get; set; } = true;
}

public sealed class SignedTransactionBatchRequest
{
    /// <summary>
    /// Fully signed Solana transactions in execution order.
    /// </summary>
    public List<string> SignedTransactionsBase64 { get; set; } = new();

    /// <summary>
    /// If true, simulate each transaction before broadcasting it.
    /// </summary>
    public bool SimulateFirst { get; set; } = true;

    /// <summary>
    /// If true, stop on first failed simulation or send.
    /// </summary>
    public bool HaltOnError { get; set; } = true;
}
