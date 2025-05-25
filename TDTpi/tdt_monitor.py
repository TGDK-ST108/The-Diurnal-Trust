#!/usr/bin/env python3
import os
import sys
import time
import shutil
import psutil
from datetime import timedelta

# ANSI Color Codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"

def clear():
    print("\033[H\033[J", end="")

def colorize_bar(percent):
    if percent < 0.5:
        return COLOR_GREEN
    elif percent < 0.8:
        return COLOR_YELLOW
    else:
        return COLOR_RED

def draw_bar(label, percent, width=40):
    filled = int(width * percent)
    color = colorize_bar(percent)
    bar = "[" + "#" * filled + "-" * (width - filled) + "]"
    return f"{label}: {color}{bar} {int(percent * 100)}%{COLOR_RESET}"

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

def get_temperature():
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return "N/A"
        for name, entries in temps.items():
            for entry in entries:
                if entry.current:
                    return f"{entry.label or name}: {entry.current}°C"
    except:
        return "Unavailable"
    return "Unknown"

def check_alerts(cpu, mem, battery):
    alerts = []
    if cpu > 0.9:
        alerts.append("[ALERT] CPU usage exceeds 90%")
    if mem > 0.9:
        alerts.append("[ALERT] Memory usage exceeds 90%")
    if battery and battery.percent < 20 and not battery.power_plugged:
        alerts.append("[ALERT] Battery critically low")
    return alerts

def run_monitor():
    term_width = shutil.get_terminal_size().columns
    while True:
        clear()
        print(f"{COLOR_CYAN}== TDT SYSTEM MONITOR :: Veyrunis Unit =={COLOR_RESET}")

        cpu = psutil.cpu_percent(interval=0.2) / 100
        mem = psutil.virtual_memory().percent / 100
        battery = psutil.sensors_battery()
        uptime = timedelta(seconds=int(time.time() - psutil.boot_time()))
        rx, tx = net_speed()
        temperature = get_temperature()

        print(draw_bar("CPU Usage", cpu))
        print(draw_bar("Memory Use", mem))
        if battery:
            print(draw_bar("Battery", battery.percent / 100))
        else:
            print("Battery: N/A")

        print(f"Temperature: {temperature}")
        print(f"Uptime: {str(uptime)}")
        print(f"Net RX: {format_bytes(rx)}/s | TX: {format_bytes(tx)}/s")

        alerts = check_alerts(cpu, mem, battery)
        if alerts:
            print(f"\n{COLOR_RED}:: TDT ALERTS ::{COLOR_RESET}")
            for alert in alerts:
                print(f"{COLOR_RED}{alert}{COLOR_RESET}")

        print(f"\n[Press Ctrl+C to exit]")
        time.sleep(1)

try:
    run_monitor()
except KeyboardInterrupt:
    print("\nExiting TDT Monitor.")
    sys.exit(0)