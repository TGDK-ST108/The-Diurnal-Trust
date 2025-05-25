-- TDT Sentinel :: Lua Edition v3.0
-- Trideotaxis + Gentoo Resonance + OliviaAI Integration
-- TGDK // Veyrunis // BFE License

local socket = require("socket")
local os = require("os")
local olivia = require("olivia_companion")

-- Simulate Gentoo feedback pulse (entropy tremor sampling)
local function gentoo_resonance()
    local drift = math.random(0, 1000) / 10.0
    local polarity = (drift > 500) and "+" or "-"
    return "Gentoo Field Drift: " .. polarity .. drift .. " | Vector: " .. math.floor(drift % 360) .. "°"
end

-- Apply Trideotaxis logic (symbolic fold analysis on HR/BR)
local function trideotaxis_analysis(hr, br)
    if not hr or not br then return "Trideotaxis: Insufficient Data" end
    local phi = (hr + br) % 5
    local dex = (hr * br) % 6
    local code = "Φ" .. phi .. "-Δ" .. dex
    return "Trideotaxis FoldCode: " .. code
end

-- Read biometric line from paired sensor (e.g., rfcomm0)
local function read_biometric()
    local dev_path = "/dev/rfcomm0"
    local f = io.open(dev_path, "r")
    if not f then return "BR:-- HR:--", nil, nil end

    local data = f:read("*l") or ""
    f:close()

    local br = tonumber(data:match("BR:(%d+)"))
    local hr = tonumber(data:match("HR:(%d+)"))
    return data, hr, br
end

-- Get Termux GPS data if available
local function get_location()
    local pipe = io.popen("termux-location")
    if not pipe then return "Location: [Unavailable]" end
    local output = pipe:read("*a")
    pipe:close()
    return "Location Data: " .. output:gsub("\n", "")
end

-- Log helper
local function anomaly_log(message)
    local log = io.open("sentinel_log.txt", "a")
    log:write(os.date("[%Y-%m-%d %H:%M:%S] ") .. message .. "\n")
    log:close()
end

-- Display + log
local function log_and_display(label, data)
    print(label .. ": " .. data)
    anomaly_log(label .. ": " .. data)
end

-- Main loop
local function run()
    print("[TDT-SENTINEL] :: Secure loop initialized :: Trideotaxis + Gentoo mode")

    while true do
        print("\n[" .. os.date("%H:%M:%S") .. "] System Heartbeat")
        anomaly_log("Heartbeat OK")

        local loc = get_location()
        log_and_display("Location", loc)

        local data, hr, br = read_biometric()
        log_and_display("Biometric Stream", data)

        local tricode = trideotaxis_analysis(hr, br)
        log_and_display("Trideotaxis", tricode)

        local gentoo = gentoo_resonance()
        log_and_display("Gentoo Field", gentoo)

        if hr and br then
            olivia.process(data)
        else
            anomaly_log("Biometric data unreadable")
        end

        socket.sleep(60)
    end
end

run()