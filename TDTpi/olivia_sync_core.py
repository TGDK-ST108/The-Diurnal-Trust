#!/usr/bin/env python3
# TGDK :: OliviaAI Sync & Command Core
# BFE-TGDK-OLIVIA-CORE-001 :: NLP Interface + Beacon Router + Remote Trigger

import requests
import json
import time
from datetime import datetime
import random
import string
import os

LOGFILE = "olivia_sync.log"
API_ENDPOINT = "https://olivia-tgdk.com/api/sync"

def log(msg):
    with open(LOGFILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(f"[OliviaAI-Core] {msg}")

def beacon_id():
    return ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=12))

def send_sync(message, agent="Veyrunis.Unit", trigger=False):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "unit": agent,
        "message": message,
        "beacon": beacon_id(),
        "trigger": trigger
    }

    try:
        headers = {'Content-Type': 'application/json'}
        r = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            log(f"SYNC OK :: {data.get('response', '[no message]')}")
            return data.get("response")
        else:
            log(f"SYNC FAIL :: HTTP {r.status_code}")
    except Exception as e:
        log(f"SYNC EXCEPTION: {e}")
    return None

def receive_commands():
    log("Polling remote for instructions...")
    try:
        r = requests.get(f"{API_ENDPOINT}/commands", timeout=5)
        if r.status_code == 200:
            cmds = r.json().get("commands", [])
            for cmd in cmds:
                log(f"[CMD RECEIVED] :: {cmd}")
    except Exception as e:
        log(f"COMMAND RETRIEVE ERROR: {e}")

def interactive():
    log("OliviaAI Command Core Started (Interactive Mode)")
    while True:
        try:
            msg = input("You> ")
            if msg.strip().lower() in ["exit", "quit"]:
                break
            send_sync(msg, trigger=True)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    interactive()