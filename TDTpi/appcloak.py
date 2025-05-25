#!/usr/bin/env python3
# TGDK :: App Optimization + Cloak Module
# BFE-TGDK-APPCLOAK-001 :: Behavior Cloak + Background Service Kill

import os
import subprocess
import time
from datetime import datetime

LOGFILE = "appcloak.log"
APP_LIST_FILE = "cloak_targets.txt"

def log(msg):
    with open(LOGFILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(f"[AppCloak] {msg}")

def load_target_apps():
    if not os.path.exists(APP_LIST_FILE):
        with open(APP_LIST_FILE, "w") as f:
            f.write("com.facebook.katana\ncom.instagram.android\ncom.tiktok.android\n")
        log("Initialized default app cloak list.")
    with open(APP_LIST_FILE, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def kill_background_services(package):
    try:
        subprocess.run(["am", "force-stop", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log(f"Force-stopped: {package}")
    except Exception as e:
        log(f"Error stopping {package}: {e}")

def check_app_behavior(package):
    try:
        output = subprocess.check_output(["dumpsys", "package", package], stderr=subprocess.DEVNULL).decode()
        if "running" in output or "started" in output:
            log(f"[CLOAK] {package} behavior ACTIVE — initiating shutdown.")
            kill_background_services(package)
        else:
            log(f"{package} inactive.")
    except Exception as e:
        log(f"[ERROR] Cannot query {package}: {e}")

def run_loop():
    log("AppCloak Optimization Engine started.")
    targets = load_target_apps()
    while True:
        for pkg in targets:
            check_app_behavior(pkg)
        time.sleep(90)

if __name__ == "__main__":
    run_loop()