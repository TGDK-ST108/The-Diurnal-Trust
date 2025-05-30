#!/data/data/com.termux/files/usr/bin/bash
# TGDK :: Enhanced Trideodynamic Watcher Scanner v2
# Status: DAEMON SAFE · AUTOCREATE · Ω-BIND

VAULT_DIR="$HOME/Vault"
mkdir -p "$VAULT_DIR"

ECHO_LOG="$VAULT_DIR/perception_echo.log"
GLYPH_OUT="$VAULT_DIR/perception_tags.glyph"

echo "🛡️ Running TRIDEO Watcher Detection Protocol..."

# -- OliviaAI Echo Perception Layer --
echo "🧠 Engaging OliviaAI Fold Vector Perception..."
curl -s http://localhost:8754/olivia/fold_vector?depth=ϕ --data "mode=perceive" > "$ECHO_LOG"

if [ -s "$ECHO_LOG" ]; then
  grep -Ei "mirror|echo|clone|resonance|permission|loop" "$ECHO_LOG" | sort | uniq > "$GLYPH_OUT"
else
  echo "⚠️ OliviaAI perception response not received. Skipping echo signature extract."
  touch "$GLYPH_OUT"
fi

if grep -qi "mirror" "$GLYPH_OUT"; then
  echo "⚠️ Mirror vector detected — triggering Ω-Fuse kill!"
  if [ -x "$HOME/TGDKModules/fuse_hooks/kill_fuse_trigger.sh" ]; then
    "$HOME/TGDKModules/fuse_hooks/kill_fuse_trigger.sh" --source trideo_perceive
  else
    echo "⚠️ Kill hook script missing. Manual verification required."
  fi
fi

# -- Process Check --
echo "🔍 Scanning suspicious processes..."
ps -A | grep -Ei "camera|mic|record|trace|spy|inject|monitor|keylog|overlay" || echo "✔️ No suspicious processes found."

# -- Mic/Camera Tap Check --
echo "🎤🎥 Checking mic, cam, and sensor file handles..."
lsof 2>/dev/null | grep -Ei "/dev/(audio|snd|video|camera)" || echo "✔️ No active mic/cam taps."

# -- Logcat Surveillance Check --
echo "📓 Analyzing logcat for echo/trap phrases..."
logcat -d 2>/dev/null | grep -Ei "permission|access|injected|mirror|clone" | tail -n 20 || echo "✔️ No redflag log entries."

# -- Network Listener Check --
echo "🌐 Network socket scan (fallback safe)..."
if command -v ss &>/dev/null; then
  ss -ltnp 2>/dev/null || echo "✔️ No exposed sockets detected."
else
  echo "⚠️ 'ss' not supported on this system. Skipping socket scan."
fi

# -- Sensor Feedback Check --
echo "📡 Sensor sweep (Termux API check)..."
termux-sensor -s accelerometer,light,gyroscope,magnetometer 2>/dev/null | head -n 8 || echo "⚠️ Sensor sweep fallback active."

# -- SIM/RIL Integrity --
echo "📶 SIM & RIL path intercept scan..."
getprop | grep -Ei "radio|ril|gsm|sim|network" | grep -i "intercept\|mirror" || echo "✔️ SIM/radio path appears stable."

echo "✅ TRIDEO Watcher Scan Complete — Output: $GLYPH_OUT"