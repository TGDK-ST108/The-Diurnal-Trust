#!/usr/bin/env python3
# TGDK :: BatteryOps & Charger Optimization v1.0
# BFE-TGDK-BATTOPS-001 :: Battery Monitor + Thermal Profiling + Veyrunis Efficiency

import os
import time
import json
import subprocess
from datetime import datetime

LOGFILE = "batteryops.log"

def log(msg):
    with open(LOGFILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(f"[BatteryOps] {msg}")

def get_battery_info():
    try:
        raw = subprocess.check_output(["termux-battery-status"]).decode()
        data = json.loads(raw)
        return data
    except Exception as e:
        log(f"Error reading battery: {e}")
        return {}

def suggest_action(status, level, temperature=None):
    if status == "DISCHARGING" and level < 20:
        return "ALERT: Battery low. Consider charging soon."
    if status == "CHARGING" and level > 90:
        return "TIP: Unplug soon to preserve battery health."
    if temperature and temperature > 42:
        return "WARNING: Device overheating. Disconnect power and cool."
    return "Battery status nominal."

def get_temperature():
    try:
        paths = ["/sys/class/thermal/thermal_zone0/temp"]
        for path in paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    raw = f.read().strip()
                    return int(raw) / 1000
    except:
        return None
    return None

def run_loop():
    log("BatteryOps Monitor Started :: Charger Efficiency Mode Enabled")
    while True:
        info = get_battery_info()
        temp = get_temperature()

        level = info.get("percentage", 0)
        status = info.get("status", "UNKNOWN")
        power = info.get("power_save_enabled", False)

        log(f"Battery: {level}% | Status: {status} | Saver: {power} | Temp: {temp or 'N/A'}°C")
        action = suggest_action(status, level, temp)
        log(f"=> {action}")

        time.sleep(120)

if __name__ == "__main__":
    run_loop()