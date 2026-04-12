using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Security.Cryptography;
using System.Collections.Generic;

public sealed class FealtyEnsoStatement
{
    public string Shape { get; set; } = "Enso shaped like a Trident";
    public string Seal { get; set; } = "Onriyu paternaliser";
    public string Motion { get; set; } = "a fling on grooves";
    public string Blank { get; set; } = "reckon with";

    public string Render()
    {
        return $"With Fealty in accordance to an {Shape}, sealed to an {Seal}, it presents itself as {Motion} that exists for others to {Blank}.";
    }

    // X × 5 / 22 - 1 / 4  =>  (10X - 11) / 44
    public double Evaluate(double x)
    {
        return (x * 5.0 / 22.0) - 0.25;
    }

    public string EvaluateExact(double x)
    {
        return $"({10 * x:0.###} - 11) / 44";
    }
}

public static class Program
{
    public static void Main()
    {
        var fills = new List<string>
        {
            "witness",
            "reckon with",
            "inherit",
            "pass through",
            "be measured by"
        };

        var phrase = new FealtyEnsoStatement();

        Console.WriteLine("Variants:");
        Console.WriteLine();

        foreach (var fill in fills)
        {
            phrase.Blank = fill;
            Console.WriteLine(phrase.Render());
        }

        Console.WriteLine();
        Console.WriteLine("Formula:");
        double x = 5.0;
        phrase.Blank = "reckon with";
        Console.WriteLine($"X × 5 / 22 - 1 / 4, where X = {x}");
        Console.WriteLine($"Decimal: {phrase.Evaluate(x):0.######}");
        Console.WriteLine($"Exact form: {phrase.EvaluateExact(x)}");
    }
}

namespace TGDK.SafeProfile
{
    public enum PresentationMode
    {
        Neutral,
        Masculine,
        Feminine,
        Androgynous
    }

    

    public sealed class DandyRacoon
    {
        public string PublicAlias { get; private set; }
        public PresentationMode Mode { get; private set; }
        public double AuraRadiusFeet { get; private set; }
        public int AuraAngleDegrees { get; private set; }
        public bool BluetoothEnabled { get; private set; }
        public DateTimeOffset LastRotationUtc { get; private set; }

        private readonly byte[] _key;
        private readonly Dictionary<string, string> _localProfile = new();

        public DandyRacoon(
            string publicAlias = "dandy_racoon",
            PresentationMode mode = PresentationMode.Neutral,
            double auraRadiusFeet = 110.2,
            int auraAngleDegrees = 20,
            bool bluetoothEnabled = true)
        {
            PublicAlias = SanitizeAlias(publicAlias);
            Mode = mode;
            AuraRadiusFeet = Math.Clamp(auraRadiusFeet, 1.0, 150.0);
            AuraAngleDegrees = Math.Clamp(auraAngleDegrees, 1, 360);
            BluetoothEnabled = bluetoothEnabled;
            LastRotationUtc = DateTimeOffset.UtcNow;
            _key = RandomNumberGenerator.GetBytes(32);
        }

        public void SetPresentationMode(PresentationMode mode)
        {
            Mode = mode;
        }

        public void SetAlias(string alias)
        {
            PublicAlias = SanitizeAlias(alias);
        }

        public void SetAura(double radiusFeet, int angleDegrees)
        {
            AuraRadiusFeet = Math.Clamp(radiusFeet, 1.0, 150.0);
            AuraAngleDegrees = Math.Clamp(angleDegrees, 1, 360);
        }

        public void SetBluetooth(bool enabled)
        {
            BluetoothEnabled = enabled;
        }

        public string GetEphemeralBeaconId()
        {
            LastRotationUtc = DateTimeOffset.UtcNow;
            string seed = $"{PublicAlias}|{Mode}|{LastRotationUtc:yyyyMMddHHmm}";
            using var hmac = new HMACSHA256(_key);
            byte[] hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(seed));
            return Convert.ToHexString(hash)[..16].ToLowerInvariant();
        }

        public void SetProfileField(string key, string value)
        {
            if (string.IsNullOrWhiteSpace(key))
                throw new ArgumentException("Key cannot be empty.", nameof(key));

            _localProfile[key.Trim()] = value ?? string.Empty;
        }

        public string? GetProfileField(string key)
        {
            return _localProfile.TryGetValue(key, out var value) ? value : null;
        }

        public string ExportEncryptedProfile()
        {
            string json = System.Text.Json.JsonSerializer.Serialize(new
            {
                PublicAlias,
                Mode = Mode.ToString(),
                AuraRadiusFeet,
                AuraAngleDegrees,
                BluetoothEnabled,
                LastRotationUtc,
                Profile = _localProfile
            });

            byte[] plaintext = Encoding.UTF8.GetBytes(json);
            byte[] nonce = RandomNumberGenerator.GetBytes(12);
            byte[] ciphertext = new byte[plaintext.Length];
            byte[] tag = new byte[16];

            using var aes = new AesGcm(_key, 16);
            aes.Encrypt(nonce, plaintext, ciphertext, tag);

            return Convert.ToBase64String(Combine(nonce, tag, ciphertext));
        }

        public string DescribeSafeState()
        {
            return $"alias={PublicAlias}, mode={Mode}, aura={AuraAngleDegrees}deg/{AuraRadiusFeet:F1}ft, bluetooth={(BluetoothEnabled ? "on" : "off")}";
        }

        private static string SanitizeAlias(string alias)
        {
            if (string.IsNullOrWhiteSpace(alias))
                return "dandy_racoon";

            alias = alias.Trim();
            var sb = new StringBuilder();

            foreach (char c in alias)
            {
                if (char.IsLetterOrDigit(c) || c == '_' || c == '-')
                    sb.Append(c);
            }

            return sb.Length == 0 ? "dandy_racoon" : sb.ToString();
        }

        private static byte[] Combine(byte[] a, byte[] b, byte[] c)
        {
            byte[] output = new byte[a.Length + b.Length + c.Length];
            Buffer.BlockCopy(a, 0, output, 0, a.Length);
            Buffer.BlockCopy(b, 0, output, a.Length, b.Length);
            Buffer.BlockCopy(c, 0, output, a.Length + b.Length, c.Length);
            return output;
        }
    }

    public static class Program
    {
        public static void Main()
        {
            var dandy = new DandyRacoon(
                publicAlias: "dandy_racoon",
                mode: PresentationMode.Androgynous,
                auraRadiusFeet: 110.2,
                auraAngleDegrees: 20,
                bluetoothEnabled: true
            );

            dandy.SetProfileField("style", "stud");
            dandy.SetProfileField("privacy_mode", "high");

            Console.WriteLine(dandy.DescribeSafeState());
            Console.WriteLine($"ephemeral_beacon={dandy.GetEphemeralBeaconId()}");
            Console.WriteLine($"encrypted_profile={dandy.ExportEncryptedProfile()}");
        }
    }
}

namespace TGDK.VowVirtuation
{
    public static class VowVirtuationProtocol
    {
        public static readonly string[] Roots =
        {
            "ignorance",
            "attachment",
            "anger"
        };

        public static readonly string[] PolicyMixes =
        {
            "honor",
            "accord",
            "tolerance",
            "differential",
            "dexterity",
            "distrust",
            "metScore",
            "volume_shift"
        };

        public static readonly string[] Channels =
        {
            "truth",
            "restraint",
            "duty",
            "witness",
            "interpretation",
            "seat5_dexterity"
        };

        public const int TotalPrimaryVolumetrics = 144;
        public const int TotalSubtractionaryMixes = 66440;
        public const int TotalStateSpace = 84000;
        public const int TotalReserveBins = TotalStateSpace - TotalPrimaryVolumetrics - TotalSubtractionaryMixes;

        static VowVirtuationProtocol()
        {
            if (Roots.Length * PolicyMixes.Length * Channels.Length != TotalPrimaryVolumetrics)
            {
                throw new InvalidOperationException("Primary volumetric dimensions do not resolve to 144.");
            }
        }

        public static VowVirtuationResult Evaluate(
            double confidence,
            double ratio,
            double policyDifferential,
            double toxicExchangeRatio)
        {
            confidence = Clamp01(confidence);
            ratio = Clamp01(ratio);
            policyDifferential = Clamp01(policyDifferential);
            toxicExchangeRatio = Clamp01(toxicExchangeRatio);

            double metScore =
                Clamp01((confidence * 0.40) +
                        (ratio * 0.35) +
                        ((1.0 - policyDifferential) * 0.25));

            double volumeShift =
                Clamp01((toxicExchangeRatio * 0.50) +
                        (policyDifferential * 0.30) +
                        ((1.0 - ratio) * 0.20));

            double exactRedressPressure =
                Clamp01((policyDifferential * 0.55) +
                        (confidence * 0.20) +
                        (toxicExchangeRatio * 0.25));

            double overturnPressure =
                Clamp01((policyDifferential * 0.45) +
                        (volumeShift * 0.35) +
                        ((1.0 - metScore) * 0.20));

            double mirrorDuoPressure =
                Clamp01((ratio * 0.40) +
                        (confidence * 0.20) +
                        (policyDifferential * 0.40));

            List<MetaOutcome> nineMap = BuildNineMap(
                confidence,
                ratio,
                policyDifferential,
                metScore,
                volumeShift,
                exactRedressPressure,
                overturnPressure,
                mirrorDuoPressure
            );

            return new VowVirtuationResult
            {
                PrimaryCount = TotalPrimaryVolumetrics,
                SubtractionaryCount = TotalSubtractionaryMixes,
                ReserveCount = TotalReserveBins,
                MetScore = metScore,
                VolumeShift = volumeShift,
                ExactRedressPressure = exactRedressPressure,
                OverturnPressure = overturnPressure,
                MirrorDuoPressure = mirrorDuoPressure,
                NineMap = nineMap
            };
        }

        public static List<PrimaryVolumetric> BuildPrimaryVolumetrics()
        {
            var result = new List<PrimaryVolumetric>(TotalPrimaryVolumetrics);

            for (int r = 0; r < Roots.Length; r++)
            {
                for (int p = 0; p < PolicyMixes.Length; p++)
                {
                    for (int c = 0; c < Channels.Length; c++)
                    {
                        double baseValue = Clamp01(
                            0.30
                            + 0.12 * (r / Math.Max(1.0, Roots.Length - 1))
                            + 0.18 * (p / Math.Max(1.0, PolicyMixes.Length - 1))
                            + 0.10 * (c / Math.Max(1.0, Channels.Length - 1))
                        );

                        double tolerance = Clamp01(
                            0.20
                            + 0.15 * Math.Sin((p + 1) * 0.75)
                            + 0.10 * Math.Cos((c + 1) * 0.55)
                        );

                        double efficacy = Clamp01(
                            0.35
                            + 0.20 * (PolicyMixes[p] is "honor" or "accord" or "metScore" ? 1.0 : 0.0)
                            + 0.10 * (Channels[c] is "truth" or "restraint" or "duty" ? 1.0 : 0.0)
                            - 0.08 * (Roots[r] == "anger" ? 1.0 : 0.0)
                        );

                        result.Add(new PrimaryVolumetric
                        {
                            Root = Roots[r],
                            PolicyMix = PolicyMixes[p],
                            Channel = Channels[c],
                            BaseValue = baseValue,
                            Tolerance = tolerance,
                            Efficacy = efficacy
                        });
                    }
                }
            }

            return result;
        }

        public static List<SubtractionaryMix> BuildSubtractionaryMixes(IReadOnlyList<PrimaryVolumetric> primaries)
        {
            var result = new List<SubtractionaryMix>(TotalSubtractionaryMixes);
            double[] toleranceBands = { 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50 };

            for (int i = 0; i < primaries.Count; i++)
            {
                for (int j = i + 1; j < primaries.Count; j++)
                {
                    var left = primaries[i];
                    var right = primaries[j];

                    foreach (double band in toleranceBands)
                    {
                        double toleranceGap = Math.Abs(left.Tolerance - right.Tolerance);
                        double policyDifferential =
                            Math.Abs(left.BaseValue - right.BaseValue) +
                            Math.Abs(left.Efficacy - right.Efficacy);

                        double subtractionValue = Clamp01(
                            (policyDifferential * 0.60) +
                            (Math.Abs(toleranceGap - band) * 0.40)
                        );

                        result.Add(new SubtractionaryMix
                        {
                            LeftKey = left.Key,
                            RightKey = right.Key,
                            ToleranceGap = toleranceGap,
                            PolicyDifferential = Clamp01(policyDifferential / 2.0),
                            SubtractionValue = subtractionValue
                        });

                        if (result.Count >= TotalSubtractionaryMixes)
                        {
                            return result;
                        }
                    }
                }
            }

            return result;
        }

        private static List<MetaOutcome> BuildNineMap(
            double confidence,
            double ratio,
            double policyDifferential,
            double metScore,
            double volumeShift,
            double exactRedressPressure,
            double overturnPressure,
            double mirrorDuoPressure)
        {
            var raw = new List<MetaOutcome>
            {
                new MetaOutcome
                {
                    Name = "preserve",
                    Weight = Clamp01((metScore * 0.70) + ((1.0 - volumeShift) * 0.30)),
                    Confidence = confidence,
                    PolicyDifferential = policyDifferential,
                    Description = "retain current frame under coherent policy alignment"
                },
                new MetaOutcome
                {
                    Name = "review",
                    Weight = Clamp01((policyDifferential * 0.60) + ((1.0 - metScore) * 0.40)),
                    Confidence = confidence,
                    PolicyDifferential = policyDifferential,
                    Description = "exact review of mismatch between policy and efficacy"
                },
                new MetaOutcome
                {
                    Name = "rebalance",
                    Weight = Clamp01((ratio * 0.50) + (volumeShift * 0.50)),
                    Confidence = confidence,
                    PolicyDifferential = policyDifferential,
                    Description = "adjust tolerance and volume against differential pressure"
                },
                new MetaOutcome
                {
                    Name = "overturn",
                    Weight = overturnPressure,
                    Confidence = confidence,
                    PolicyDifferential = policyDifferential,
                    Description = "replace a failing frame with a corrected frame"
                },
                new MetaOutcome
                {
                    Name = "flip",
                    Weight = Clamp01((mirrorDuoPressure * 0.60) + (ratio * 0.40)),
                    Confidence = confidence,
                    PolicyDifferential = policyDifferential,
                    Description = "reverse orientation to test the inverse ratio"
                },
                new MetaOutcome
                {
                    Name = "mirror_duo",
                    Weight = mirrorDuoPressure,
                    Confidence = confidence,
                    PolicyDifferential = policyDifferential,
                    Description = "run the mirrored counterpart of the present state"
                },
                new MetaOutcome
                {
                    Name = "refract",
                    Weight = Clamp01((volumeShift * 0.40) + (policyDifferential * 0.30) + (confidence * 0.30)),
                    Confidence = confidence,
                    PolicyDifferential = policyDifferential,
                    Description = "split into multiple plausible outcome channels"
                },
                new MetaOutcome
                {
                    Name = "redress",
                    Weight = exactRedressPressure,
                    Confidence = confidence,
                    PolicyDifferential = policyDifferential,
                    Description = "apply exact remedy to the policy mismatch"
                },
                new MetaOutcome
                {
                    Name = "seal",
                    Weight = Clamp01((confidence * 0.40) + ((1.0 - policyDifferential) * 0.60)),
                    Confidence = confidence,
                    PolicyDifferential = policyDifferential,
                    Description = "stabilize and ward the resulting frame"
                }
            };

            double total = raw.Sum(x => x.Weight);
            if (total <= 0.0)
            {
                total = 1.0;
            }

            foreach (var item in raw)
            {
                item.Weight = Math.Round(item.Weight / total, 6);
            }

            raw.Sort((a, b) => b.Weight.CompareTo(a.Weight));
            return raw;
        }

        private static double Clamp01(double value)
        {
            if (value < 0.0) return 0.0;
            if (value > 1.0) return 1.0;
            return value;
        }
    }

    public sealed class PrimaryVolumetric
    {
        public string Root { get; set; } = "";
        public string PolicyMix { get; set; } = "";
        public string Channel { get; set; } = "";
        public double BaseValue { get; set; }
        public double Tolerance { get; set; }
        public double Efficacy { get; set; }

        public string Key => $"{Root}:{PolicyMix}:{Channel}";
    }

    public sealed class SubtractionaryMix
    {
        public string LeftKey { get; set; } = "";
        public string RightKey { get; set; } = "";
        public double ToleranceGap { get; set; }
        public double PolicyDifferential { get; set; }
        public double SubtractionValue { get; set; }
    }

    public sealed class MetaOutcome
    {
        public string Name { get; set; } = "";
        public double Weight { get; set; }
        public double Confidence { get; set; }
        public double PolicyDifferential { get; set; }
        public string Description { get; set; } = "";
    }

    public sealed class VowVirtuationResult
    {
        public int PrimaryCount { get; set; }
        public int SubtractionaryCount { get; set; }
        public int ReserveCount { get; set; }
        public double MetScore { get; set; }
        public double VolumeShift { get; set; }
        public double ExactRedressPressure { get; set; }
        public double OverturnPressure { get; set; }
        public double MirrorDuoPressure { get; set; }
        public List<MetaOutcome> NineMap { get; set; } = new();
    }

    public static class Program
    {
        public static void Main()
        {
            List<PrimaryVolumetric> primaries = VowVirtuationProtocol.BuildPrimaryVolumetrics();
            List<SubtractionaryMix> subtractionary = VowVirtuationProtocol.BuildSubtractionaryMixes(primaries);

            VowVirtuationResult result = VowVirtuationProtocol.Evaluate(
                confidence: 0.82,
                ratio: 0.74,
                policyDifferential: 0.41,
                toxicExchangeRatio: 0.33
            );

            Console.WriteLine($"PRIMARY: {primaries.Count}");
            Console.WriteLine($"SUBTRACTIONARY: {subtractionary.Count}");
            Console.WriteLine($"RESERVE: {VowVirtuationProtocol.TotalReserveBins}");
            Console.WriteLine($"metScore: {result.MetScore:F4}");
            Console.WriteLine($"volume_shift: {result.VolumeShift:F4}");
            Console.WriteLine($"exact_redress_pressure: {result.ExactRedressPressure:F4}");
            Console.WriteLine($"overturn_pressure: {result.OverturnPressure:F4}");
            Console.WriteLine($"mirror_duo_pressure: {result.MirrorDuoPressure:F4}");
            Console.WriteLine();

            Console.WriteLine(JsonSerializer.Serialize(result, new JsonSerializerOptions
            {
                WriteIndented = true
            }));
        }
    }
}

app.MapPost("/api/v1/staldwell/infrastructure/vow-virtuation/evaluate",
    async (VowVirtuationRequest request, IPrimaryStaldwellInfrastructure infra, CancellationToken ct) =>
    {
        var validation = request.Validate();
        if (validation.Count > 0)
            return Results.ValidationProblem(validation);

        return Results.Ok(await infra.EvaluateVowVirtuationAsync(request, ct));
    });

using System.Text.Json.Serialization;
using TGDK.Staldwell.Infrastructure;
using TGDK.VowVirtuation;

var builder = WebApplication.CreateBuilder(args);

builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.WriteIndented = true;
    options.SerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
});

builder.Services.AddSingleton<IPrimaryStaldwellInfrastructure, PrimaryStaldwellInfrastructure>();

var app = builder.Build();

app.MapGet("/health", () => Results.Ok(new
{
    ok = true,
    service = "staldwell-primary-infrastructure",
    utc = DateTimeOffset.UtcNow
}));

var staldwell = app.MapGroup("/api/v1/staldwell");
staldwell.WithTags("Staldwell");

staldwell.MapPost("/infrastructure/vow-virtuation/evaluate",
    async (VowVirtuationRequest request, IPrimaryStaldwellInfrastructure infra, CancellationToken ct) =>
    {
        var validation = request.Validate();
        if (validation.Count > 0)
        {
            return Results.ValidationProblem(validation);
        }

        var result = await infra.EvaluateVowVirtuationAsync(request, ct);
        return Results.Ok(result);
    })
    .WithName("EvaluateVowVirtuation")
    .WithSummary("Evaluates vow virtuation against primary Staldwell infrastructure.")
    .WithDescription("Returns metScore, volume shift, exact redress pressure, overturn pressure, mirror-duo pressure, and nine-map outcomes.");

staldwell.MapGet("/infrastructure/vow-virtuation/manifest",
    (IPrimaryStaldwellInfrastructure infra) =>
    {
        return Results.Ok(infra.GetManifest());
    })
    .WithName("GetVowVirtuationManifest")
    .WithSummary("Returns route manifest and protocol dimensions.");

using TGDK.VowVirtuation;

namespace TGDK.Staldwell.Infrastructure;

public interface IPrimaryStaldwellInfrastructure
{
    Task<StaldwellVowVirtuationResponse> EvaluateVowVirtuationAsync(
        VowVirtuationRequest request,
        CancellationToken cancellationToken = default);

    StaldwellManifest GetManifest();
}

public sealed class PrimaryStaldwellInfrastructure : IPrimaryStaldwellInfrastructure
{
    private readonly List<PrimaryVolumetric> _primaries;
    private readonly List<SubtractionaryMix> _subtractionary;

    public PrimaryStaldwellInfrastructure()
    {
        _primaries = VowVirtuationProtocol.BuildPrimaryVolumetrics();
        _subtractionary = VowVirtuationProtocol.BuildSubtractionaryMixes(_primaries);
    }

    public Task<StaldwellVowVirtuationResponse> EvaluateVowVirtuationAsync(
        VowVirtuationRequest request,
        CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();

        var result = VowVirtuationProtocol.Evaluate(
            confidence: request.Confidence,
            ratio: request.Ratio,
            policyDifferential: request.PolicyDifferential,
            toxicExchangeRatio: request.ToxicExchangeRatio
        );

        var envelope = new StaldwellVowVirtuationResponse
        {
            Ok = true,
            TraceId = string.IsNullOrWhiteSpace(request.TraceId)
                ? Guid.NewGuid().ToString("N")
                : request.TraceId,
            Mode = "vow_virtuation",
            Context = new StaldwellContextSummary
            {
                CaseId = request.CaseId,
                AssetId = request.AssetId,
                NodeId = request.NodeId,
                Source = request.Source,
                SubmittedAtUtc = DateTimeOffset.UtcNow
            },
            Dimensions = new StaldwellDimensions
            {
                PrimaryCount = _primaries.Count,
                SubtractionaryCount = _subtractionary.Count,
                ReserveCount = VowVirtuationProtocol.TotalReserveBins,
                TotalStateSpace = VowVirtuationProtocol.TotalStateSpace
            },
            Metrics = new StaldwellMetricBlock
            {
                MetScore = result.MetScore,
                VolumeShift = result.VolumeShift,
                ExactRedressPressure = result.ExactRedressPressure,
                OverturnPressure = result.OverturnPressure,
                MirrorDuoPressure = result.MirrorDuoPressure
            },
            NineMap = result.NineMap
                .Select(x => new StaldwellOutcome
                {
                    Name = x.Name,
                    Weight = x.Weight,
                    Confidence = x.Confidence,
                    PolicyDifferential = x.PolicyDifferential,
                    Description = x.Description
                })
                .ToList()
        };

        return Task.FromResult(envelope);
    }

    public StaldwellManifest GetManifest()
    {
        return new StaldwellManifest
        {
            Service = "staldwell-primary-infrastructure",
            Route = "/api/v1/staldwell/infrastructure/vow-virtuation/evaluate",
            Dimensions = new StaldwellDimensions
            {
                PrimaryCount = _primaries.Count,
                SubtractionaryCount = _subtractionary.Count,
                ReserveCount = VowVirtuationProtocol.TotalReserveBins,
                TotalStateSpace = VowVirtuationProtocol.TotalStateSpace
            },
            Roots = VowVirtuationProtocol.Roots,
            PolicyMixes = VowVirtuationProtocol.PolicyMixes,
            Channels = VowVirtuationProtocol.Channels
        };
    }
}

namespace TGDK.Staldwell.Infrastructure;

public sealed class VowVirtuationRequest
{
    public string? TraceId { get; set; }
    public string? CaseId { get; set; }
    public string? AssetId { get; set; }
    public string? NodeId { get; set; }
    public string? Source { get; set; }

    public double Confidence { get; set; }
    public double Ratio { get; set; }
    public double PolicyDifferential { get; set; }
    public double ToxicExchangeRatio { get; set; }

    public Dictionary<string, string[]> Validate()
    {
        var errors = new Dictionary<string, string[]>();

        if (Confidence < 0 || Confidence > 1)
            errors["confidence"] = new[] { "Confidence must be between 0 and 1." };

        if (Ratio < 0 || Ratio > 1)
            errors["ratio"] = new[] { "Ratio must be between 0 and 1." };

        if (PolicyDifferential < 0 || PolicyDifferential > 1)
            errors["policyDifferential"] = new[] { "PolicyDifferential must be between 0 and 1." };

        if (ToxicExchangeRatio < 0 || ToxicExchangeRatio > 1)
            errors["toxicExchangeRatio"] = new[] { "ToxicExchangeRatio must be between 0 and 1." };

        return errors;
    }
}

public sealed class StaldwellVowVirtuationResponse
{
    public bool Ok { get; set; }
    public string TraceId { get; set; } = "";
    public string Mode { get; set; } = "";
    public StaldwellContextSummary Context { get; set; } = new();
    public StaldwellDimensions Dimensions { get; set; } = new();
    public StaldwellMetricBlock Metrics { get; set; } = new();
    public List<StaldwellOutcome> NineMap { get; set; } = new();
}

public sealed class StaldwellContextSummary
{
    public string? CaseId { get; set; }
    public string? AssetId { get; set; }
    public string? NodeId { get; set; }
    public string? Source { get; set; }
    public DateTimeOffset SubmittedAtUtc { get; set; }
}

public sealed class StaldwellDimensions
{
    public int PrimaryCount { get; set; }
    public int SubtractionaryCount { get; set; }
    public int ReserveCount { get; set; }
    public int TotalStateSpace { get; set; }
}

public sealed class StaldwellMetricBlock
{
    public double MetScore { get; set; }
    public double VolumeShift { get; set; }
    public double ExactRedressPressure { get; set; }
    public double OverturnPressure { get; set; }
    public double MirrorDuoPressure { get; set; }
}

public sealed class StaldwellOutcome
{
    public string Name { get; set; } = "";
    public double Weight { get; set; }
    public double Confidence { get; set; }
    public double PolicyDifferential { get; set; }
    public string Description { get; set; } = "";
}

public sealed class StaldwellManifest
{
    public string Service { get; set; } = "";
    public string Route { get; set; } = "";
    public StaldwellDimensions Dimensions { get; set; } = new();
    public string[] Roots { get; set; } = Array.Empty<string>();
    public string[] PolicyMixes { get; set; } = Array.Empty<string>();
    public string[] Channels { get; set; } = Array.Empty<string

app.Run();
