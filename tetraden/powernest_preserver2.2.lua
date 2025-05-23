-- TGDK PowerNest Preserver v2.2
-- Codename: PowerNest :: INFQQUAp Enhanced
-- BFE License ID: BFE-TGDK-POWERNEST-INFQQUAP
-- Protected via SEPULCRUM-SEAL-VII :: XQUAp Cascade Authorized

local math = require("math")
local bit = require("bit")
math.randomseed(os.time())

local running = true

-- Handle Ctrl+C
local function shutdown()
    print("\n[PowerNest] :: Shutdown signal received. Exiting gracefully...")
    os.exit()
end

-- Wrap in protected call
local status, err = pcall(function()
    print("[PowerNest] :: INFQQUAp Telemetry Loop Active :: Ctrl+C to exit")

    while running do
        adjust_charge()
        print("[PowerNest] :: Cycle complete. Sleeping 60s...\n")
        os.execute("sleep 60")
    end
end)

if not status then shutdown() end

-- === Termux Fallback ===
local function read_termux_telemetry()
    local handle = io.popen("termux-battery-status")
    if not handle then return nil end
    local json = handle:read("*a")
    handle:close()

    local cap = json:match('"percentage"%s*:%s*(%d+)')
    local temp = json:match('"temperature"%s*:%s*(%d+)')
    local volt = json:match('"current"%s*:%s*(-?%d+)')

    return tonumber(cap), tonumber(temp), tonumber(volt or 0)
end

-- === Smart Read ===
local function smart_read_param(param)
    local value = read_param(param)
    if not value then
        print("[PowerNest] :: [WARN] Falling back to termux-battery-status...")
        local cap, temp, volt = read_termux_telemetry()
        if param == "capacity" then return cap
        elseif param == "temp" then return temp
        elseif param == "voltage_now" then return volt end
    end
    return value
end

-- === Battery SysFS Path ===
local battery = "/sys/class/power_supply/battery/"

-- === Helpers ===
local function read_param(param)
    local path = battery .. param
    local file = io.open(path, "r")
    if not file then
        print("[PowerNest] :: [ERROR] Cannot read: " .. path)
        return nil
    end
    local val = file:read("*all")
    file:close()
    return tonumber(val)
end

-- === Infinitizer Matrix Core ===
local function infinitizer_matrix(cap, temp, volt)
    return (cap * 17 + temp * 3 + volt * 0.0001) % 144001
end

-- === Trideon Cellular Signature Hash ===
local function trideon_signature(voltage)
    return (voltage * 31 + 17777) % 99991
end

-- === QQUAp Cascade Offload ===
local function qquap_offload(matrix_val)
    local cascade = bit.bxor(matrix_val, 0xAA55) % 104729
    return string.format("QQUAp::%05X", cascade)
end

-- === NLP Echo Feedback ===
local function olivia_feedback(state, value)
    local log = io.open(".powernest_nlp.log", "a")
    log:write(string.format("[OliviaAI] :: %s => %s @ %s\n", state, value, os.date()))
    log:close()
end

-- === Trident Forking (Cumulative Ratio Analysis) ===
local charge_history = {}
local function analyze_cumulative(cap)
    table.insert(charge_history, cap)
    if #charge_history > 30 then table.remove(charge_history, 1) end

    local sum = 0
    for _, v in ipairs(charge_history) do sum = sum + v end
    local avg = sum / #charge_history

    local trident_1 = (avg + cap) / 2
    local trident_2 = (avg * 1.1) % 100
    local trident_3 = ((cap - avg)^2) % 75

    return trident_1, trident_2, trident_3
end

-- === Charging Logic ===
local function adjust_charge()
    local capacity = smart_read_param("capacity")
    local temp = smart_read_param("temp")
    local voltage = smart_read_param("voltage_now")

    if not (capacity and temp and voltage) then
        print("[PowerNest] :: [FATAL] Missing telemetry. Skipping cycle.")
        return
    end

    -- INF-QQUAp Entropy Routing
    local inf_val = infinitizer_matrix(capacity, temp, voltage)
    local qquap_code = qquap_offload(inf_val)
    local sig = trideon_signature(voltage)
    olivia_feedback("QQUAp_Entropy", qquap_code)

    -- Trident Fork Analysis
    local t1, t2, t3 = analyze_cumulative(capacity)
    olivia_feedback("TridentFork", string.format("%.2f | %.2f | %.2f", t1, t2, t3))

    -- Charge Control Logic (root required for write ops)
    if temp > 450 then
        os.execute("echo 0 > /sys/class/power_supply/battery/charging_enabled")
        print("[PowerNest] :: TEMP HIGH - Charging disabled.")
        olivia_feedback("Charge", "DISABLED: Temp " .. temp)
        return
    end

    if capacity >= 90 then
        os.execute("echo 0 > /sys/class/power_supply/battery/charging_enabled")
        print("[PowerNest] :: Battery fully charged. Charging paused.")
        olivia_feedback("Charge", "PAUSED @ " .. capacity .. "%")
    elseif capacity >= 80 then
        os.execute("echo 1 > /sys/class/power_supply/battery/charging_slow")
        print("[PowerNest] :: Slow Charging Mode.")
        olivia_feedback("Charge", "SLOW @ " .. capacity .. "%")
    else
        os.execute("echo 1 > /sys/class/power_supply/battery/charging_enabled")
        print("[PowerNest] :: Standard Charging Mode.")
        olivia_feedback("Charge", "ACTIVE @ " .. capacity .. "%")
    end

    print(string.format(
        "[PowerNest] :: TrideonSig: %s | QQUAp: %s | Cap: %d%% | Temp: %.1f°C",
        sig, qquap_code, capacity, temp / 10
    ))
end

-- === Execution Loop ===
print("[PowerNest] :: INFQQUAp Telemetry Loop Active :: Locking T-Code Kernel Flow")
while true do
    adjust_charge()
    print("[PowerNest] :: Cycle complete. Sleeping 60s...\n")
    os.execute("sleep 60")
end