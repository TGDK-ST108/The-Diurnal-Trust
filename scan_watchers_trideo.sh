#!/data/data/com.termux/files/usr/bin/bash
# TGDK :: TrideoWatcher Enhanced Scan System
# Codename: scan_watchers_trideo.sh
# Status: TRIDEO-ENABLED · Ω-FUSE BOUND

echo "🛡️ Running TRIDEO Watcher Detection Protocol..."

# Phase 0 – OliviaAI Echo-Fold Perception Layer
echo "🧠 Engaging OliviaAI Fold Vector Perception..."
curl -s http://localhost:8754/olivia/fold_vector?depth=ϕ --data "mode=perceive" > ~/Vault/perception_echo.log
grep -E "mirror|echo|clone|resonance|permission|loop" ~/Vault/perception_echo.log | sort | uniq > ~/Vault/perception_tags.glyph

if grep -qi "mirror" ~/Vault/perception_tags.glyph; then
  echo "⚠️  Mirror vector detected — activating Ω-Fuse kill trigger!"
  ~/TGDKModules/fuse_hooks/kill_fuse_trigger.sh --source trideo_perceive
fi

# Phase 1 – Process Watcher Check
echo "🔍 Scanning for suspicious processes..."
ps -A | grep -Ei "camera|mic|record|trace|spy|inject|monitor|keylog|overlay" || echo "✔️ No suspicious processes found."

# Phase 2 – Microphone / Camera Tap Check
echo "🎤🎥 Checking access to mic, camera, and sensors..."
lsof | grep -Ei "/dev/(audio|snd|video|camera)" || echo "✔️ No active mic/cam taps."

# Phase 3 – Logcat Pattern Scan
echo "📓 Scanning logcat for echo/trap phrases..."
logcat -d | grep -Ei "permission|access|injected|mirror|clone" | tail -n 20 || echo "✔️ No redflag log entries found."

# Phase 4 – Network Listener Check
echo "🌐 Network socket scan..."
ss -ltnp || echo "✔️ No exposed sockets or suspicious connections."

# Phase 5 – Sensor Scan (correct usage)
echo "📡 Sensor sweep (accelerometer, light, gyro, mag)..."
termux-sensor -s accelerometer,light,gyroscope,magnetometer | head -n 8

# Phase 6 – SIM/Router Integrity
echo "📶 SIM/RIL path integrity check..."
getprop | grep -Ei "radio|ril|gsm|sim|network" | grep -i "intercept\|mirror" || echo "✔️ SIM/radio path appears stable."

echo "✅ TRIDEO Watcher Scan Complete — Logs sealed to ~/Vault/perception_tags.glyph"