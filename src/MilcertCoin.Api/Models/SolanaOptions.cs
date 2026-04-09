namespace Crypto.Net.Solana.Models;

public sealed class SolanaOptions
{
    public string RpcUrl { get; set; } = "https://api.devnet.solana.com";
    public string Commitment { get; set; } = "confirmed";
}
