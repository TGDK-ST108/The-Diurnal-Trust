// Program.cs
// .NET 8 minimal API
//
// Defensive beacon integrity monitor.
// Purpose:
// - Detect suspected beacon suppression or tampering in systems you own/control
// - Preserve evidence
// - Recommend safe failover actions
// - Emit signed incident reports
//
// Run:
//   dotnet new web -n BeaconShield
//   Replace Program.cs with this file
//   set BEACON_HMAC_KEY=change-me
//   dotnet run
//
// Example POST:
// curl -X POST http://localhost:5000/telemetry \
//   -H "Content-Type: application/json" \
//   -d "{\"beaconId\":\"SAT-ALPHA-01\",\"timestampUtc\":\"2026-04-09T20:30:00Z\",\"sequence\":1001,\"rssiDbm\":-118.5,\"snrDb\":5.2,\"carrierPresent\":true,\"frameValid\":true,\"authenticated\":true,\"source\":\"ground-a\"}"

using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.AspNetCore.Http.HttpResults;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton<BeaconPolicy>();
builder.Services.AddSingleton<BeaconMonitor>();
builder.Services.AddEndpointsApiExplorer();

var app = builder.Build();

app.MapGet("/", () => Results.Ok(new
{
    service = "BeaconShield",
    mode = "defensive",
    version = "1.0.0",
    status = "ok"
}));

app.MapPost("/telemetry", (
    BeaconTelemetry telemetry,
    BeaconMonitor monitor,
    BeaconPolicy policy) =>
{
    var outcome = monitor.Ingest(telemetry, policy);
    return Results.Ok(outcome);
});

app.MapGet("/beacons/{beaconId}", (
    string beaconId,
    BeaconMonitor monitor) =>
{
    var state = monitor.GetState(beaconId);
    return state is null
        ? Results.NotFound(new { ok = false, error = "beacon_not_found" })
        : Results.Ok(state);
});

app.MapGet("/reports/latest/{beaconId}", (
    string beaconId,
    BeaconMonitor monitor) =>
{
    var report = monitor.GetLatestReport(beaconId);
    return report is null
        ? Results.NotFound(new { ok = false, error = "report_not_found" })
        : Results.Ok(report);
});

app.MapGet("/reports", (BeaconMonitor monitor) => Results.Ok(monitor.GetAllReports()));

app.Run();

public sealed class BeaconPolicy
{
    public TimeSpan MaxSilenceGap { get; init; } = TimeSpan.FromSeconds(20);
    public int WindowSize { get; init; } = 16;
    public double MaxInvalidFrameRate { get; init; } = 0.35;
    public double MaxUnauthenticatedRate { get; init; } = 0.10;
    public double MaxRssiDropDb { get; init; } = 18.0;
    public double MaxSnrDropDb { get; init; } = 8.0;
    public int MaxSequenceResets { get; init; } = 1;
    public int ConsecutiveCarrierLossThreshold { get; init; } = 4;
    public HashSet<string> ApprovedSources { get; init; } = new(StringComparer.OrdinalIgnoreCase)
    {
        "ground-a",
        "ground-b",
        "relay-1"
    };
}

public sealed record BeaconTelemetry(
    string BeaconId,
    DateTimeOffset TimestampUtc,
    long Sequence,
    double RssiDbm,
    double SnrDb,
    bool CarrierPresent,
    bool FrameValid,
    bool Authenticated,
    string Source,
    Dictionary<string, string>? Tags = null
);

public enum AlertSeverity
{
    Info,
    Warning,
    Critical
}

public enum AlertType
{
    SilenceGap,
    CarrierLossBurst,
    InvalidFrameBurst,
    AuthenticationFailureBurst,
    SequenceReset,
    UnauthorizedSource,
    SuddenSignalDegradation,
    SuspectedSuppression
}

public sealed record Alert(
    AlertType Type,
    AlertSeverity Severity,
    string Message,
    DateTimeOffset TimestampUtc,
    Dictionary<string, object>? Evidence = null
);

public sealed record ContainmentAction(
    string Action,
    string Reason,
    bool AutoExecutable
);

public sealed record IncidentReport(
    string ReportId,
    string BeaconId,
    DateTimeOffset GeneratedUtc,
    string Status,
    List<Alert> Alerts,
    List<ContainmentAction> RecommendedActions,
    Dictionary<string, object> Metrics,
    string SignatureHex
);

public sealed class BeaconState
{
    public string BeaconId { get; init; } = "";
    public List<BeaconTelemetry> Recent { get; init; } = new();
    public List<Alert> ActiveAlerts { get; init; } = new();
    public IncidentReport? LatestReport { get; set; }
    public bool FailoverRecommended { get; set; }
    public DateTimeOffset? LastSeenUtc { get; set; }
    public string Health { get; set; } = "unknown";
}

public sealed class BeaconMonitor
{
    private readonly ConcurrentDictionary<string, BeaconState> _states = new(StringComparer.OrdinalIgnoreCase);
    private readonly ConcurrentDictionary<string, IncidentReport> _reports = new(StringComparer.OrdinalIgnoreCase);
    private readonly JsonSerializerOptions _jsonOptions = new(JsonSerializerDefaults.Web)
    {
        WriteIndented = false
    };

    public object Ingest(BeaconTelemetry t, BeaconPolicy policy)
    {
        var state = _states.GetOrAdd(t.BeaconId, id => new BeaconState { BeaconId = id });
        lock (state)
        {
            var previous = state.Recent.Count > 0 ? state.Recent[^1] : null;

            state.Recent.Add(t);
            if (state.Recent.Count > policy.WindowSize)
            {
                state.Recent.RemoveAt(0);
            }

            state.LastSeenUtc = t.TimestampUtc;

            var alerts = Evaluate(state.Recent, previous, t, policy);
            state.ActiveAlerts.Clear();
            state.ActiveAlerts.AddRange(alerts);

            var health = ComputeHealth(alerts);
            state.Health = health;
            state.FailoverRecommended = alerts.Any(a => a.Severity == AlertSeverity.Critical);

            IncidentReport? report = null;
            if (alerts.Count > 0)
            {
                report = BuildReport(state, alerts);
                state.LatestReport = report;
                _reports[report.ReportId] = report;
            }

            return new
            {
                ok = true,
                beaconId = t.BeaconId,
                health,
                failoverRecommended = state.FailoverRecommended,
                alerts,
                reportId = report?.ReportId
            };
        }
    }

    public BeaconState? GetState(string beaconId)
    {
        return _states.TryGetValue(beaconId, out var state) ? state : null;
    }

    public IncidentReport? GetLatestReport(string beaconId)
    {
        if (_states.TryGetValue(beaconId, out var state))
        {
            return state.LatestReport;
        }

        return null;
    }

    public IEnumerable<IncidentReport> GetAllReports()
    {
        return _reports.Values.OrderByDescending(r => r.GeneratedUtc);
    }

    private List<Alert> Evaluate(
        List<BeaconTelemetry> window,
        BeaconTelemetry? previous,
        BeaconTelemetry current,
        BeaconPolicy policy)
    {
        var alerts = new List<Alert>();

        if (!policy.ApprovedSources.Contains(current.Source))
        {
            alerts.Add(new Alert(
                AlertType.UnauthorizedSource,
                AlertSeverity.Critical,
                $"Telemetry/control source '{current.Source}' is not approved.",
                current.TimestampUtc,
                new Dictionary<string, object> { ["source"] = current.Source }
            ));
        }

        if (previous is not null)
        {
            var gap = current.TimestampUtc - previous.TimestampUtc;
            if (gap > policy.MaxSilenceGap)
            {
                alerts.Add(new Alert(
                    AlertType.SilenceGap,
                    AlertSeverity.Warning,
                    $"Silence gap exceeded threshold: {gap.TotalSeconds:F1}s.",
                    current.TimestampUtc,
                    new Dictionary<string, object> { ["gapSeconds"] = gap.TotalSeconds }
                ));
            }

            if (current.Sequence < previous.Sequence)
            {
                alerts.Add(new Alert(
                    AlertType.SequenceReset,
                    AlertSeverity.Warning,
                    $"Sequence regressed from {previous.Sequence} to {current.Sequence}.",
                    current.TimestampUtc,
                    new Dictionary<string, object>
                    {
                        ["previousSequence"] = previous.Sequence,
                        ["currentSequence"] = current.Sequence
                    }
                ));
            }

            var rssiDrop = previous.RssiDbm - current.RssiDbm;
            var snrDrop = previous.SnrDb - current.SnrDb;
            if (rssiDrop
