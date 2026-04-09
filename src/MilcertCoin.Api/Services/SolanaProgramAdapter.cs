using Crypto.Net.Solana.Models;

namespace Crypto.Net.Solana.Services;

public sealed class SolanaProgramAdapter
{
    private readonly SolanaRpcClient _rpc;

    public SolanaProgramAdapter(SolanaRpcClient rpc)
    {
        _rpc = rpc;
    }

    public async Task<BroadcastResult> ExecuteSignedAsync(
        string signedTransactionBase64,
        bool simulateFirst = true,
        CancellationToken ct = default)
    {
        var result = new BroadcastResult();

        if (string.IsNullOrWhiteSpace(signedTransactionBase64))
        {
            result.Error = "SignedTransactionBase64 is required.";
            return result;
        }

        if (simulateFirst)
        {
            result.Simulated = true;

            try
            {
                var sim = await _rpc.SimulateTransactionAsync(signedTransactionBase64, ct);
                result.SimulationPassed = sim.Value?.Err is null;
                result.SimulationError = sim.Value?.Err;
                result.SimulationLogs = sim.Value?.Logs ?? new List<string>();
                result.UnitsConsumed = sim.Value?.UnitsConsumed;

                if (!result.SimulationPassed)
                {
                    result.Error = "Simulation failed.";
                    return result;
                }
            }
            catch (Exception ex)
            {
                result.Error = $"Simulation exception: {ex.Message}";
                return result;
            }
        }

        try
        {
            var signature = await _rpc.SendTransactionAsync(signedTransactionBase64, skipPreflight: false, ct);
            result.Signature = signature;
            return result;
        }
        catch (Exception ex)
        {
            result.Error = $"Broadcast exception: {ex.Message}";
            return result;
        }
    }

    public async Task<BatchBroadcastResult> ExecuteSignedBatchAsync(
        IEnumerable<string> signedTransactionsBase64,
        bool simulateFirst = true,
        bool haltOnError = true,
        CancellationToken ct = default)
    {
        var batch = new BatchBroadcastResult();

        foreach (var tx in signedTransactionsBase64)
        {
            var step = await ExecuteSignedAsync(tx, simulateFirst, ct);
            batch.Results.Add(step);

            if (haltOnError && (!string.IsNullOrWhiteSpace(step.Error) || string.IsNullOrWhiteSpace(step.Signature)))
                break;
        }

        return batch;
    }
}
