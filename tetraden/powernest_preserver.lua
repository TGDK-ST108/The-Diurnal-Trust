-- TGDK PowerNest Preserver
-- Version 1.0 :: BFE License Active :: Codename: PowerNest

local battery = "/sys/class/power_supply/battery/"
local function read_param(param)
    local file = io.open(battery .. param, "r")
    if not file then return nil end
    local value = file:read("*all")
    file:close()
    return tonumber(value)
end

local function adjust_charge()
    local capacity = read_param("capacity") or 0
    local temp = read_param("temp") or 0
    local voltage = read_param("voltage_now") or 0

    -- Safety checks
    if temp > 450 then  -- ~45.0°C
        os.execute("echo 0 > /sys/class/power_supply/battery/charging_enabled")
        print("[PowerNest] :: TEMP HIGH - Charging disabled.")
        return
    end

    -- Adaptive logic
    if capacity >= 80 and capacity < 90 then
        os.execute("echo 1 > /sys/class/power_supply/battery/charging_slow")
        print("[PowerNest] :: Slow Charging Mode.")
    elseif capacity >= 90 then
        os.execute("echo 0 > /sys/class/power_supply/battery/charging_enabled")
        print("[PowerNest] :: Battery sufficiently charged. Charging paused.")
    else
        os.execute("echo 1 > /sys/class/power_supply/battery/charging_enabled")
        print("[PowerNest] :: Standard Charging Mode.")
    end
end

while true do
    adjust_charge()
    os.execute("sleep 60")
end