namespace MilcertCoin.Api.Models;

public sealed class ChainOptions
{
    public string RpcUrl { get; set; } = "";
    public long ChainId { get; set; }
    public string ContractAddress { get; set; } = "";
    public string OwnerPrivateKey { get; set; } = "";
}
