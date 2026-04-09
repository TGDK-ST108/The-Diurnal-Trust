namespace MilcertCoin.Api.Services;

public static class PmzMath
{
    // F = (D * PMZ / (I + O)) - S + C
    public static decimal ComputeReturnRatio(
        decimal d,
        decimal pmz,
        decimal intro,
        decimal outro,
        decimal dualState,
        decimal centroid)
    {
        var channelSum = intro + outro;
        if (channelSum == 0m)
            throw new DivideByZeroException("Intro + Outro cannot be zero.");

        return (d * pmz / channelSum) - dualState + centroid;
    }

    // PMZ = ((target + S - C) * (I + O)) / D
    public static decimal SolvePmzForTarget(
        decimal target,
        decimal d,
        decimal intro,
        decimal outro,
        decimal dualState,
        decimal centroid)
    {
        if (d == 0m)
            throw new DivideByZeroException("D cannot be zero.");

        return ((target + dualState - centroid) * (intro + outro)) / d;
    }

    public static bool IsMintableWindow(decimal output)
    {
        // example policy window: permit mint if output is within 3.4 ± 0.05
        return output >= 3.35m && output <= 3.45m;
    }
}
