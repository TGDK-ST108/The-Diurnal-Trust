#!/usr/bin/env python3
import os
import sys
import time
import shutil
import psutil
from datetime import timedelta

def clear():
    print("\033[H\033[J", end="")

def draw_bar(label, percent, width=40):
    filled = int(width * percent)
    bar = "[" + "#" * filled + "-" * (width - filled) + "]"
    return f"{label}: {bar} {int(percent * 100)}%"

def format_bytes(n):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if n < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"

def net_speed(interface="wlan0"):
    io1 = psutil.net_io_counters(pernic=True).get(interface, None)
    if not io1:
        return (0, 0)
    time.sleep(1)
    io2 = psutil.net_io_counters(pernic=True).get(interface, None)
    rx = io2.bytes_recv - io1.bytes_recv
    tx = io2.bytes_sent - io1.bytes_sent
    return rx, tx

def run_monitor():
    term_width = shutil.get_terminal_size().columns
    while True:
        clear()
        print("== TDT SYSTEM MONITOR ==")

        cpu = psutil.cpu_percent(interval=0.2) / 100
        mem = psutil.virtual_memory().percent / 100
        battery = psutil.sensors_battery()
        uptime = timedelta(seconds=int(time.time() - psutil.boot_time()))
        rx, tx = net_speed()

        print(draw_bar("CPU Usage", cpu))
        print(draw_bar("Memory Use", mem))
        if battery:
            print(draw_bar("Battery", battery.percent / 100))
        else:
            print("Battery: N/A")

        print(f"Uptime: {str(uptime)}")
        print(f"Net RX: {format_bytes(rx)}/s | TX: {format_bytes(tx)}/s")

        print("\n[Press Ctrl+C to exit]")
        time.sleep(1)

try:
    run_monitor()
except KeyboardInterrupt:
    print("\nExiting TDT Monitor.")
    sys.exit(0)