#!/data/data/com.termux/files/usr/bin/bash
# TGDK :: TDT Unified Stack Launcher
# BFE-TGDK-TDT-LAUNCH-001 :: Veyrunis Unit Deployment Init

echo "[TDT] :: Initializing The Diurnal Trust Operative Stack..."
sleep 1

# Define all core modules
MODULES=(
  "tdt_monitor.py"
  "tdt-sentinel.lua"
  "bluetrace.py"
  "batteryops.py"
  "5g_port_defender.py"
  "appcloak.py"
  "ghost_protocol.py"
  "olivia_sync_core.py"
  "quomo_interface.lua"
  "blackmirror_scooty.lua"
)

# Launch Python modules
launch_python() {
  if [ -f "$1" ]; then
    echo "[LAUNCH] :: Python $1"
    nohup python "$1" > /dev/null 2>&1 &
  else
    echo "[SKIP] :: $1 not found"
  fi
}

# Launch Lua modules
launch_lua() {
  if [ -f "$1" ]; then
    echo "[LAUNCH] :: Lua $1"
    nohup lua "$1" > /dev/null 2>&1 &
  else
    echo "[SKIP] :: $1 not found"
  fi
}

# Launch all modules
for mod in "${MODULES[@]}"; do
  case "$mod" in
    *.py) launch_python "$mod" ;;
    *.lua) launch_lua "$mod" ;;
    *) echo "[UNKNOWN] :: $mod not supported" ;;
  esac
done

echo "[TDT] :: All modules deployed. OliviaAI now tracking."