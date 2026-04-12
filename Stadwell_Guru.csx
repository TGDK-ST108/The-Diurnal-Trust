using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

// ============================================================
// SAFE POLICY-COHERENCE ENGINE
// Scope:
// - owned systems, nodes, assets, and events
// - no profiling of private individuals
// - no unauthorized surveillance or targeting
// ============================================================

public enum EntityKind
{
    Asset,
    Node,
    Service,
    Dataset,
    Workflow
}

public enum EventKind
{
    Normal,
    Extraction,
    Indifference,
    Adjustment,
    Latitude,
    CoBarentFallacy,
    LatticeShift,
    Differential
}

public enum ForfeitureClass
{
    None,
    Review,
    Restricted,
    Isolate
}

public sealed class DexSignature
{
    public string Profile { get; }
    public string ObjectType { get; }
    public float Direction { get; }
    public float Delta { get; }
    public string Key { get; }
    public string Hash { get; }

    public DexSignature(string profile, string objectType, float direction, float delta, string key)
    {
        Profile = profile ?? throw new ArgumentNullException(nameof(profile));
        ObjectType = objectType ?? throw new ArgumentNullException(nameof(objectType));
        Direction = direction;
        Delta = delta;
        Key = key ?? throw new ArgumentNullException(nameof(key));
        Hash = ComputeHash();
    }

    private string ComputeHash()
    {
        string composite = $"{Profile}|{ObjectType}|{Direction:F4}|{Delta:F4}|{Key}";
        using SHA256 sha256 = SHA256.Create();
        byte[] hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(composite));
        return Convert.ToHexString(hashBytes).ToLowerInvariant();
    }
}

public sealed class AssetEntity
{
    public string Id { get; }
    public string Name { get; }
    public EntityKind Kind { get; }
    public DexSignature Signature { get; }

    public AssetEntity(string id, string name, EntityKind kind, DexSignature signature)
    {
        Id = id;
        Name = name;
        Kind = kind;
        Signature = signature;
    }
}

public sealed class PolicySignal
{
    public string EntityId { get; init; } = "";
    public EventKind Kind { get; init; }
    public float Magnitude { get; init; }
    public string Source { get; init; } = "local";
    public DateTimeOffset Timestamp { get; init; } = DateTimeOffset.UtcNow;
    public Dictionary<string, string> Tags { get; init; } = new();
}

public sealed class PolicyNode
{
    public string NodeId { get; }
    public string Name { get; }
    public float ExtractionWeight { get; private set; } = 0.85f;
    public float IndifferenceWeight { get; private set; } = 0.35f;
    public float AdjustmentWeight { get; private set; } = 0.55f;
    public float LatitudeWeight { get; private set; } = 0.40f;
    public float CoBarentFallacyWeight { get; private set; } = 0.90f;
    public float LatticeWeight { get; private set; } = 0.60f;
    public float DifferentialWeight { get; private set; } = 0.70f;

    public PolicyNode(string nodeId, string name)
    {
        NodeId = nodeId;
        Name = name;
    }

    public void ApplyTrustedShift(TrustedPolicyShift shift)
    {
        if (!shift.Verified)
        {
            throw new InvalidOperationException("Policy shift rejected: signature not verified.");
        }

        ExtractionWeight = Clamp01(shift.ExtractionWeight);
        IndifferenceWeight = Clamp01(shift.IndifferenceWeight);
        AdjustmentWeight = Clamp01(shift.AdjustmentWeight);
        LatitudeWeight = Clamp01(shift.LatitudeWeight);
        CoBarentFallacyWeight = Clamp01(shift.CoBarentFallacyWeight);
        LatticeWeight = Clamp01(shift.LatticeWeight);
        DifferentialWeight = Clamp01(shift.DifferentialWeight);
    }

    public float Score(EventKind kind, float magnitude)
    {
        float w = kind switch
        {
            EventKind.Extraction => ExtractionWeight,
            EventKind.Indifference => IndifferenceWeight,
            EventKind.Adjustment => AdjustmentWeight,
            EventKind.Latitude => LatitudeWeight,
            EventKind.CoBarentFallacy => CoBarentFallacyWeight,
            EventKind.LatticeShift => LatticeWeight,
            EventKind.Differential => DifferentialWeight,
            _ => 0.10f
        };

        return Clamp01(w * magnitude);
    }

    private static float Clamp01(float v) => MathF.Max(0f, MathF.Min(1f, v));
}

public sealed class TrustedPolicyShift
{
    public string Issuer { get; init; } = "internal";
    public DateTimeOffset Timestamp { get; init; } = DateTimeOffset.UtcNow;
    public bool Verified { get; init; }

    public float ExtractionWeight { get; init; }
    public float IndifferenceWeight { get; init; }
    public float AdjustmentWeight { get; init; }
    public float LatitudeWeight { get; init; }
    public float CoBarentFallacyWeight { get; init; }
    public float LatticeWeight { get; init; }
    public float DifferentialWeight { get; init; }
}

public sealed class WardSeal
{
    public string SealId { get; }
    public bool ThSealed { get; }
    public bool TriangulatedToVoid { get; }
    public bool TriangulatedToEmpty { get; }
    public bool TriangulatedToAbyssal { get; }

    public WardSeal(
        string sealId,
        bool thSealed = true,
        bool triangulatedToVoid = true,
        bool triangulatedToEmpty = true,
        bool triangulatedToAbyssal = true)
    {
        SealId = sealId;
        ThSealed = thSealed;
        TriangulatedToVoid = triangulatedToVoid;
        TriangulatedToEmpty = triangulatedToEmpty;
        TriangulatedToAbyssal = triangulatedToAbyssal;
    }

    public bool IsValid() =>
        ThSealed && TriangulatedToVoid && TriangulatedToEmpty && TriangulatedToAbyssal;
}

public sealed class TrajectoryVector
{
    public Vector2[,,] Vectors { get; }

    public TrajectoryVector(int a = 21, int b = 22, int c = 2)
    {
        Vectors = new Vector2[a, b, c];
        Random rand = new Random(1337);

        for (int i = 0; i < a; i++)
        {
            for (int j = 0; j < b; j++)
            {
                for (int k = 0; k < c; k++)
                {
                    Vectors[i, j, k] = new Vector2(rand.Next(0, 360), rand.Next(0, 36));
                }
            }
        }
    }
}

public sealed class DeltaTargeting
{
    private readonly float[,] _deltas = new float[36, 144];
    private readonly Random _rand = new Random(2468);

    public DeltaTargeting()
    {
        for (int i = 0; i < 36; i++)
        {
            for (int j = 0; j < 144; j++)
            {
                _deltas[i, j] = (float)_rand.NextDouble() * 36f;
            }
        }
    }

    public float GetDelta(int deltaIndex, int quadIndex)
    {
        Validate(deltaIndex, quadIndex);
        return _deltas[deltaIndex, quadIndex];
    }

    public void UpdateDelta(int deltaIndex, int quadIndex, float newValue)
    {
        Validate(deltaIndex, quadIndex);
        _deltas[deltaIndex, quadIndex] = newValue;
    }

    private static void Validate(int deltaIndex, int quadIndex)
    {
        if (deltaIndex < 0 || deltaIndex >= 36) throw new ArgumentOutOfRangeException(nameof(deltaIndex));
        if (quadIndex < 0 || quadIndex >= 144) throw new ArgumentOutOfRangeException(nameof(quadIndex));
    }
}

public sealed class CoherenceResult
{
    public string EntityId { get; init; } = "";
    public float MetScoreNormalized { get; init; }
    public int MetScoreForce { get; init; }
    public float PolicyDifferential { get; init; }
    public float TorqueRating { get; init; }
    public float ProPolicyRatio { get; init; }
    public float VowVirtuationEstimate { get; init; }
    public ForfeitureClass Forfeiture { get; init; }
    public List<string> Labels { get; init; } = new();
}

public sealed class ComplianceLogger
{
    public void Log(string level, string message)
    {
        Console.WriteLine($"{DateTimeOffset.UtcNow:o}|{level}|{message}");
    }

    public void LogResult(CoherenceResult result)
    {
        string line =
            $"{DateTimeOffset.UtcNow:o}|RESULT|" +
            $"entity={result.EntityId}|" +
            $"met={result.MetScoreNormalized:F3}|" +
            $"force={result.MetScoreForce}|" +
            $"policy_diff={result.PolicyDifferential:F3}|" +
            $"torque={result.TorqueRating:F3}|" +
            $"pro_policy={result.ProPolicyRatio:F3}|" +
            $"vow={result.VowVirtuationEstimate:F3}|" +
            $"forfeiture={result.Forfeiture}|" +
            $"labels={string.Join(",", result.Labels)}";

        Console.WriteLine(line);
    }
}

public sealed class SurveillanceSystem
{
    private readonly ConcurrentDictionary<string, AssetEntity> _entities = new();
    private readonly ConcurrentQueue<PolicySignal> _signals = new();
    private readonly TrajectoryVector _vectors = new();
    private readonly DeltaTargeting _deltaTargeting = new();
    private readonly ComplianceLogger _logger = new();
    private readonly CancellationTokenSource _cts = new();

    private readonly PolicyNode _policyNode;
    private readonly WardSeal _ward;

    private readonly float _reviewThreshold = 0.45f;
    private readonly float _restrictedThreshold = 0.70f;
    private readonly float _isolateThreshold = 0.88f;

    public SurveillanceSystem(PolicyNode policyNode, WardSeal ward)
    {
        _policyNode = policyNode;
        _ward = ward;
    }

    public void AddEntity(AssetEntity entity)
    {
        _entities[entity.Id] = entity;
    }

    public void EnqueueSignal(PolicySignal signal)
    {
        _signals.Enqueue(signal);
    }

    public void ApplyTrustedPolicyShift(TrustedPolicyShift shift)
    {
        _policyNode.ApplyTrustedShift(shift);
        _logger.Log("POLICY", $"Applied trusted shift from issuer={shift.Issuer}");
    }

    public async Task RunAsync()
    {
        if (!_ward.IsValid())
        {
            throw new InvalidOperationException("WardSeal invalid. Refusing to run.");
        }

        _logger.Log("INFO", "Coherence loop started.");

        while (!_cts.IsCancellationRequested)
        {
            while (_signals.TryDequeue(out var signal))
            {
                if (!_entities.TryGetValue(signal.EntityId, out var entity))
                {
                    _logger.Log("WARN", $"Unknown entity id={signal.EntityId}");
                    continue;
                }

                var trajectory = GetTrajectory(entity.Signature);
                var result = EvaluateEntity(entity, signal, trajectory);
                _logger.LogResult(result);
            }

            await Task.Delay(250, _cts.Token);
        }
    }

    public void Stop() => _cts.Cancel();

    private Vector2 GetTrajectory(DexSignature target)
    {
        int i = Math.Abs(target.Hash.GetHashCode()) % 21;
        int j = Math.Abs(target.Hash.GetHashCode()) % 22;
        return _vectors.Vectors[i, j, 0];
    }

    private CoherenceResult EvaluateEntity(AssetEntity entity, PolicySignal signal, Vector2 trajectory)
    {
        float policyScore = _policyNode.Score(signal.Kind, signal.Magnitude);
        float delta = _deltaTargeting.GetDelta(
            Math.Abs(entity.Signature.Hash.GetHashCode()) % 36,
            Math.Abs(entity.Signature.Hash.GetHashCode()) % 144);

        float met = ComputeMetScore(policyScore, trajectory, delta);
        int force = (int)MathF.Round(met * 10000f);

        float differential = ComputePolicyDifferential(policyScore, delta);
        float torque = ComputeTorqueRating(policyScore, trajectory, delta);
        float proPolicy = ComputeProPolicyRatio(policyScore, differential);
        float vow = ComputeVowVirtuationEstimate(entity.Kind, policyScore, differential, torque);

        var forfeiture = ClassifyForfeiture(met, differential, torque);
        var labels = BuildLabels(signal, met, differential, torque, vow);

        return new CoherenceResult
        {
            EntityId = entity.Id,
            MetScoreNormalized = met,
            MetScoreForce = force,
            PolicyDifferential = differential,
            TorqueRating = torque,
            ProPolicyRatio = proPolicy,
            VowVirtuationEstimate = vow,
            Forfeiture = forfeiture,
            Labels = labels
        };
    }

    private static float ComputeMetScore(float policyScore, Vector2 trajectory, float delta)
    {
        float directionComponent = MathF.Abs(MathF.Cos(trajectory.X * MathF.PI / 180f));
        float phaseComponent = 1f / (1f + MathF.Abs(delta - 8.2f));
        return Clamp01((policyScore * 0.50f) + (directionComponent * 0.25f) + (phaseComponent * 0.25f));
    }

    private static float ComputePolicyDifferential(float policyScore, float delta)
    {
        float baseline = 0.50f;
        float phaseBias = MathF.Abs(delta - 8.2f) / 10f;
        return Clamp01(MathF.Abs(policyScore - baseline) + phaseBias);
    }

    private static float ComputeTorqueRating(float policyScore, Vector2 trajectory, float delta)
    {
        float angular = MathF.Abs(MathF.Sin(trajectory.X * MathF.PI / 180f));
        float phase = MathF.Min(1f, delta / 36f);
        return Clamp01((policyScore * 0.40f) + (angular * 0.35f) + (phase * 0.25f));
    }

    private static float ComputeProPolicyRatio(float policyScore, float differential)
    {
        return Clamp01(policyScore / MathF.Max(0.05f, 1f + differential));
    }

    private static float ComputeVowVirtuationEstimate(EntityKind kind, float policyScore, float differential, float torque)
    {
        float kindModifier = kind switch
        {
            EntityKind.Node => 0.80f,
            EntityKind.Service => 0.75f,
            EntityKind.Asset => 0.70f,
            EntityKind.Dataset => 0.65f,
            _ => 0.60f
        };

        return Clamp01((policyScore * 0.50f) + (torque * 0.30f) + (kindModifier * 0.20f) - (differential * 0.35f));
    }

    private ForfeitureClass ClassifyForfeiture(float met, float differential, float torque)
    {
        float burden = Clamp01((1f - met) * 0.50f + differential * 0.35f + torque * 0.15f);

        if (burden >= _isolateThreshold) return ForfeitureClass.Isolate;
        if (burden >= _restrictedThreshold) return ForfeitureClass.Restricted;
        if (burden >= _reviewThreshold) return ForfeitureClass.Review;
        return ForfeitureClass.None;
    }

    private static List<string> BuildLabels(PolicySignal signal, float met, float differential, float torque, float vow)
    {
        var labels = new List<string> { signal.Kind.ToString() };

        if (met >= 0.80f) labels.Add("stable-ascendant");
        if (differential >= 0.60f) labels.Add("high-policy-differential");
        if (torque >= 0.70f) labels.Add("high-torque");
        if (vow >= 0.75f) labels.Add("ward-aligned");
        if (signal.Kind == EventKind.Extraction) labels.Add("extraction-path");
        if (signal.Kind == EventKind.Indifference) labels.Add("indifference-path");

        return labels;
    }

    private static float Clamp01(float v) => MathF.Max(0f, MathF.Min(1f, v));
}

public static class Program
{
    public static async Task Main(string[] args)
    {
        var policyNode = new PolicyNode("policy-01", "Primary Policy Node");
        var ward = new WardSeal("ward-th-void-empty-abyssal");

        var system = new SurveillanceSystem(policyNode, ward);

        system.AddEntity(new AssetEntity(
            id: "asset-001",
            name: "Primary Compute Node",
            kind: EntityKind.Node,
            signature: new DexSignature(
                profile: "Node_Alpha",
                objectType: "Compute",
                direction: 180f,
                delta: 8.2f,
                key: "a1b2c3"))));

        system.AddEntity(new AssetEntity(
            id: "asset-002",
            name: "Archive Dataset",
            kind: EntityKind.Dataset,
            signature: new DexSignature(
                profile: "Dataset_Beta",
                objectType: "Archive",
                direction: 90f,
                delta: 3.6f,
                key: "d4e5f6"))));

        system.ApplyTrustedPolicyShift(new TrustedPolicyShift
        {
            Issuer = "internal-trusted-authority",
            Verified = true,
            ExtractionWeight = 0.90f,
            IndifferenceWeight = 0.20f,
            AdjustmentWeight = 0.55f,
            LatitudeWeight = 0.35f,
            CoBarentFallacyWeight = 0.95f,
            LatticeWeight = 0.60f,
            DifferentialWeight = 0.75f
        });

        var runTask = system.RunAsync();

        system.EnqueueSignal(new PolicySignal
        {
            EntityId = "asset-001",
            Kind = EventKind.Extraction,
            Magnitude = 0.82f,
            Source = "sensor-west"
        });

        system.EnqueueSignal(new PolicySignal
        {
            EntityId = "asset-002",
            Kind = EventKind.Differential,
            Magnitude = 0.63f,
            Source = "sensor-east"
        });

        await Task.Delay(1500);
        system.Stop();
        await runTask;
    }
}
