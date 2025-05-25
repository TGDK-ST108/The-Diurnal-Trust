-- TGDK :: Quomo Satellite Network Ping Interface
-- BFE-TGDK-QUOMO-001 :: Lua Module :: Veyrunis Compatible

local socket = require("socket")
local http = require("socket.http")
local ltn12 = require("ltn12")
local os = require("os")

local function log(msg)
    local f = io.open("quomo_log.txt", "a")
    f:write("[" .. os.date("%Y-%m-%d %H:%M:%S") .. "] " .. msg .. "\\n")
    f:close()
    print("[Quomo] " .. msg)
end

local function phi_dex_fold(text)
    local sum = 0
    for i = 1, #text do
        local c = text:sub(i,i)
        if c:match("%w") then
            sum = sum + c:byte()
        end
    end
    local phi = sum % 5
    local dex = (sum * phi + 3) % 6
    return "Φ" .. phi .. "-Δ" .. dex
end

local function beacon_payload()
    local id = "VEY" .. math.random(100000, 999999)
    local fold = phi_dex_fold(id)
    return string.format('{"unit":"Veyrunis","id":"%s","fold":"%s","ts":"%s"}',
        id, fold, os.date("!%Y-%m-%dT%H:%M:%SZ"))
end

local function send_beacon()
    local response = {}
    local payload = beacon_payload()
    local result, status = http.request{
        url = "https://olivia-tgdk.com/api/quomo/ping",
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json",
            ["Content-Length"] = tostring(#payload)
        },
        source = ltn12.source.string(payload),
        sink = ltn12.sink.table(response)
    }

    if result and status == 200 then
        log("Ping successful. Fold beacon sent.")
    else
        log("Ping failed. Quomo satellite unreachable.")
    end
end

local function run_loop()
    log("Quomo Satellite Ping Interface Initialized")
    while true do
        send_beacon()
        socket.sleep(180)
    end
end

run_loop()