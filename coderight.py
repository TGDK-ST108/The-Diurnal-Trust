import psutil
import re
import subprocess
import os

# Define suspicious patterns commonly used by keyloggers and clipboard monitors
SUSPICIOUS_PATTERNS = [
    "keylogger",
    "clipboard",
    "clipgrab",
    "hook",
    "record",
    "logger",
    "spy",
    "track",
    "capture",
    "keylog",
    "keystroke",
    "steal",
]

# Function to check running processes
def check_processes():
    flagged = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name'].lower() if proc.info['name'] else ''
            cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
            process_info = f"{name} {cmdline}"
            if any(re.search(pattern, process_info) for pattern in SUSPICIOUS_PATTERNS):
                flagged.append((proc.info['pid'], proc.info['name'], cmdline))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return flagged

# Function to check clipboard targets (only works if clipboard access is allowed)
def check_clipboard_access():
    suspicious_clipboard_access = []
    try:
        output = subprocess.check_output(['dumpsys', 'clipboard']).decode('utf-8').lower()
        if any(pattern in output for pattern in SUSPICIOUS_PATTERNS):
            suspicious_clipboard_access.append(output)
    except Exception as e:
        suspicious_clipboard_access.append(f"Clipboard access not permitted or failed: {str(e)}")
    return suspicious_clipboard_access

# Network connection checker
def check_network_connections():
    suspicious_connections = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'ESTABLISHED':
            remote_ip = conn.raddr.ip if conn.raddr else ''
            remote_port = conn.raddr.port if conn.raddr else ''
            local_port = conn.laddr.port
            pid = conn.pid
            try:
                proc_name = psutil.Process(pid).name() if pid else "Unknown"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                proc_name = "Unknown"
            connection_info = f"{proc_name} ({pid}) connected to {remote_ip}:{remote_port} from local port {local_port}"
            if remote_port in [21, 22, 23, 25, 110, 443, 465, 993, 995, 8080, 8443]:
                suspicious_connections.append(connection_info)
    return suspicious_connections

# Main scan function
def run_opsec_scan():
    print("\n[+] Checking for suspicious processes (Keyloggers & Clipboard Monitors)...")
    flagged_processes = check_processes()
    if flagged_processes:
        for pid, name, cmdline in flagged_processes:
            print(f"[!] Suspicious Process: PID {pid}, Name '{name}', Cmd '{cmdline}'")
    else:
        print("[✓] No suspicious processes found.")

    print("\n[+] Checking clipboard hooks and targets...")
    clipboard_issues = check_clipboard_access()
    if clipboard_issues:
        for issue in clipboard_issues:
            print(f"[!] Clipboard Issue: {issue}")
    else:
        print("[✓] No suspicious clipboard activity detected.")

    print("\n[+] Checking active network connections for suspicious activity...")
    network_issues = check_network_connections()
    if network_issues:
        for conn in network_issues:
            print(f"[!] Suspicious Connection: {conn}")
    else:
        print("[✓] No suspicious network connections detected.")

if __name__ == "__main__":
    run_opsec_scan()