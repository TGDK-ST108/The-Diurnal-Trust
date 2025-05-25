#!/usr/bin/env python3
# TGDK Veyrunis Division :: BlueTrace Wireless Scanner (Enhanced)
# BFE-TGDK-BLUETRACE-001 | GPS | OliviaAI Sync | Quomo Beacon | Entropy-Aware

import subprocess
import time
import json
import os
from datetime import datetime

SCAN_INTERVAL = 60  # seconds
LOG_PATH = "bluetrace_log.txt"
BEACON_URL = "https://olivia-tgdk.com/api/quomo/bluetrace"

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_PATH, "a") as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")

def run_termux_api(cmd):
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return result.decode()
    except subprocess.CalledProcessError:
        return None

def get_location():
    raw = run_termux_api(["termux-location", "--provider", "gps", "--request", "once"])
    if not raw: return "GPS Unavailable"
    try:
        loc = json.loads(raw)
        return f"{loc['latitude']},{loc['longitude']}"
    except:
        return "GPS Parse Error"

def bluetooth_scan():
    log("[BlueTrace] Bluetooth scan started...")
    result = run_termux_api(["termux-bluetooth-scan"])
    if not result:
        log("[BlueTrace] Bluetooth scan failed.")
        return []

    try:
        devices = json.loads(result)
        for dev in devices:
            log(f"[BT] {dev.get('name','Unknown')} ({dev.get('address')}) RSSI={dev.get('rssi')}")
        return devices
    except:
        log("[BlueTrace] Failed to parse Bluetooth results.")
        return []

def wifi_scan():
    log("[BlueTrace] WiFi scan started...")
    result = run_termux_api(["termux-wifi-scaninfo"])
    if not result:
        log("[BlueTrace] WiFi scan failed.")
        return []

    try:
        networks = json.loads(result)
        for net in networks:
            log(f"[WiFi] {net['ssid']} ({net['bssid']}) CH={net['frequency']} RSSI={net['level']}")
        return networks
    except:
        log("[BlueTrace] Failed to parse WiFi results.")
        return []

def mac_entropy(mac):
    # Very basic entropy scoring: high repetition or predictable sequence
    unique = len(set(mac.replace(":", "")))
    return "LOW" if unique < 5 else "NORMAL"

def scan_and_uplink():
    log("== BlueTrace Scan Cycle ==")
    location = get_location()
    log(f"Location: {location}")

    bt = bluetooth_scan()
    wifi = wifi_scan()

    payload = {
        "timestamp": datetime.now().isoformat(),
        "location": location,
        "bluetooth": [],
        "wifi": []
    }

    for d in bt:
        mac = d.get("address", "00:00:00:00:00:00")
        entropy = mac_entropy(mac)
        if entropy == "LOW":
            log(f"[ALERT] LOW entropy MAC detected: {mac}")
        payload["bluetooth"].append({
            "mac": mac,
            "name": d.get("name", "Unknown"),
            "rssi": d.get("rssi"),
            "entropy": entropy
        })

    for n in wifi:
        mac = n.get("bssid", "00:00:00:00:00:00")
        entropy = mac_entropy(mac)
        if entropy == "LOW":
            log(f"[ALERT] LOW entropy WiFi BSSID detected: {mac}")
        payload["wifi"].append({
            "ssid": n.get("ssid", "Unknown"),
            "bssid": mac,
            "rssi": n.get("level"),
            "channel": n.get("frequency"),
            "entropy": entropy
        })

    send_beacon(payload)

def send_beacon(data):
    try:
        import requests
        headers = {'Content-Type': 'application/json'}
        r = requests.post(BEACON_URL, headers=headers, json=data, timeout=5)
        if r.status_code == 200:
            log("[BlueTrace] Beacon sent to Quomo + OliviaAI Grid.")
        else:
            log(f"[BlueTrace] Beacon failed: HTTP {r.status_code}")
    except Exception as e:
        log(f"[BlueTrace] Beacon exception: {e}")

def loop():
    log("== BlueTrace Operational Loop Initiated ==")
    while True:
        scan_and_uplink()
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    loop()