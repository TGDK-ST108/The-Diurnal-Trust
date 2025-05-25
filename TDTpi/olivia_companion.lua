-- OliviaAI Companion Module for TDT Sentinel
-- Copyright TGDK / Veyrunis Division

local os = require("os")
local socket = require("socket")

-- Thresholds
local HR_HIGH = 110
local HR_LOW  = 45
local BR_HIGH = 22
local BR_LOW  = 10

local function parse_biometrics(data)
    local br = tonumber(data:match("BR:(%d+)"))
    local hr = tonumber(data:match("HR:(%d+)"))
    return br, hr
end

local function check_anomalies(br, hr)
    local alerts = {}

    if not br or not hr then
        return { "Biometric data unreadable." }
    end

    if hr > HR_HIGH then table.insert(alerts, "ALERT: Heart rate elevated (" .. hr .. " bpm)") end
    if hr < HR_LOW  then table.insert(alerts, "ALERT: Heart rate dangerously low (" .. hr .. " bpm)") end
    if br > BR_HIGH then table.insert(alerts, "ALERT: Breathing rate elevated (" .. br .. " bpm)") end
    if br < BR_LOW  then table.insert(alerts, "ALERT: Breathing rate dangerously low (" .. br .. " bpm)") end

    return alerts
end

local function log_alerts(alerts)
    local log = io.open("olivia_alerts.log", "a")
    for _, alert in ipairs(alerts) do
        log:write(os.date("[%Y-%m-%d %H:%M:%S] ") .. alert .. "\n")
    end
    log:close()
end

local function send_beacon(alert)
    -- Termux beacon simulation via curl
    local url = "https://olivia-tgdk.com/api/tdt/beacon"
    local command = "curl -X POST -d \"alert=" .. alert .. "\" " .. url .. " > /dev/null 2>&1 &"
    os.execute(command)
end

local function fallback_sms(alert)
    -- Requires Termux SMS permission granted
    local command = 'termux-sms-send -n "+15551234567" "' .. alert .. '"'
    os.execute(command)
end

-- Entry function
local function process_biometric_line(data)
    local br, hr = parse_biometrics(data)
    local alerts = check_anomalies(br, hr)

    if #alerts > 0 then
        log_alerts(alerts)
        for _, alert in ipairs(alerts) do
            send_beacon(alert)
            fallback_sms(alert)
            print("[OliviaAI Alert] " .. alert)
        end
    end
end

-- Exported for sentinel integration
return {
    process = process_biometric_line
}