namespace MilcertCoin.Api.Models;

public sealed class PmzRequest
{
    public decimal D { get; set; } = 3.001288910744936m;
    public decimal Pmz { get; set; }
    public decimal Intro { get; set; }
    public decimal Outro { get; set; }
    public decimal DualState { get; set; }
    public decimal Centroid { get; set; } = 0.8888m;
}
