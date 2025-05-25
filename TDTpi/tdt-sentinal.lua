-- TDT Sentinel :: Lua Edition + Bluetooth Biometric Integration
-- Copyright TGDK / Veyrunis Division

local socket = require("socket")
local os = require("os")

-- Read biometric data from serial stream (adjust path for your device)
local function read_biometric()
    local dev_path = "/dev/ttyUSB0"  -- Adjust as needed (could be /dev/rfcomm0)
    local f = io.open(dev_path, "r")
    if not f then return "Biometrics: [Unavailable]" end

    local data = f:read("*l") or ""
    f:close()

    -- Parse format like: BR:15 HR:72
    local br = data:match("BR:(%d+)")
    local hr = data:match("HR:(%d+)")
    if br and hr then
        return "Breath Rate: " .. br .. " bpm | Heart Rate: " .. hr .. " bpm"
    else
        return "Biometrics: [Invalid data stream]"
    end
end

local function get_location()
    local pipe = io.popen("termux-location")
    if not pipe then return "Location: [Unavailable]" end
    local output = pipe:read("*a")
    pipe:close()
    return "Location Data: " .. output:gsub("\n", "")
end

local function heartbeat()
    print("[TDT-SENTINEL] :: Heartbeat ping at " .. os.date("%Y-%m-%d %H:%M:%S"))
end

local function anomaly_log(message)
    local log = io.open("sentinel_log.txt", "a")
    log:write(os.date("[%Y-%m-%d %H:%M:%S] ") .. message .. "\n")
    log:close()
end

local function run()
    while true do
        heartbeat()

        local loc = get_location()
        local bio = read_biometric()

        anomaly_log("System check OK.")
        anomaly_log(loc)
        anomaly_log(bio)

        print(loc)
        print(bio)

        socket.sleep(60)
    end
end

print("[TDT-SENTINEL] :: Secure loop initialized with biometrics.")
run()