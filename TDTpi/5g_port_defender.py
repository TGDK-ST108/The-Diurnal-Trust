#!/usr/bin/env python3
# TGDK :: 5G Port Defender v1.1
# BFE-TGDK-5GDEF-001 :: 5G Interface Monitor + Trideotaxis Port Entropy + OliviaAI Beacon

import os
import subprocess
import time
from datetime import datetime
import random

LOGFILE = "5g_port_defender.log"
THRESHOLD = 100

def log(msg):
    with open(LOGFILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(f"[5G Port Defender] {msg}")

def get_active_ports():
    try:
        out = subprocess.check_output(["ss", "-tuln"], stderr=subprocess.DEVNULL).decode()
        lines = out.strip().split("\n")[1:]
        ports = [line.split()[3] for line in lines if line]
        return ports
    except Exception as e:
        log(f"Error reading ports: {e}")
        return []

def phi_dex_fold(text):
    s = sum(ord(c) for c in text if c.isalnum())
    phi = s % 5
    dex = (s * phi + 3) % 6
    return f"Φ{phi}-Δ{dex}"

def trideotaxis_analysis(ports):
    unique = set()
    for p in ports:
        fold = phi_dex_fold(p)
        log(f"[Trideotaxis] {p} => {fold}")
        unique.add(fold)
    return unique

def monitor_ports():
    ports = get_active_ports()
    log(f"Active port count: {len(ports)}")
    if len(ports) > THRESHOLD:
        log(f"[ALERT] Port overload detected: {len(ports)} connections.")
        trideotaxis_analysis(ports)
        send_olivia_alert("Port overload: symbolic phase anomaly detected.")
    else:
        log("Port activity within safe range.")

def send_olivia_alert(message):
    try:
        # Stub for OliviaAI uplink
        log(f"[OliviaAI] ALERT UPLINK: {message}")
        # You could plug in a real request.post() here to TGDK/Olivia grid
    except Exception as e:
        log(f"[OliviaAI Uplink Error] {e}")

def run_loop():
    log("5G Port Defender Started :: Trideotaxis Mode Enabled")
    while True:
        monitor_ports()
        time.sleep(60)

if __name__ == "__main__":
    run_loop()