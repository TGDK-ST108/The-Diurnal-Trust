#!/data/data/com.termux/files/usr/bin/bash
# TGDK :: OliviaAI Watcher Detection Script
# Codename: scan_watchers.sh
# Authority: Black Raven – Red Seal Compliant

echo "🛡️  Running Watcher Detection Protocol..."; echo

# === SECTION 1: Process Scanning ===
echo "🔍 Scanning suspicious processes..."
ps -A | grep -Ei "camera|mic|record|trace|spy|inject|monitor|keylog|overlay" || echo "✔️  No suspicious processes found."

# === SECTION 2: Audio/Visual Device Watchers ===
echo; echo "🎤🎥 Checking access to microphone, camera, and sensors..."
lsof | grep -Ei "/dev/(audio|snd|video|camera)" || echo "✔️  No active mic/cam taps."

# === SECTION 3: Logcat Surveillance Hooks ===
echo; echo "📓 Analyzing logcat for keyword traps..."
logcat -d | grep -Ei "permission|access|injected|superuser|shadow|mirror|llm" | tail -n 20 || echo "✔️  No watcher signatures in logcat."

# === SECTION 4: Network & Socket Check ===
echo; echo "🌐 Watching network & socket activity..."
netstat -tulnp | grep -Ei "listen|open" || echo "✔️  No exposed sockets or backdoor listeners detected."

# === SECTION 5: Sensor Feedback Integrity ===
echo; echo "📡 Running sensor sweep..."
termux-sensor -n accelerometer,gyroscope,magnetometer,light | head -n 8

# === SECTION 6: SIM/Radio Shadow Scans ===
echo; echo "📶 Checking for SIM/router-level intercept attempts..."
getprop | grep -Ei "radio|ril|gsm|sim|network" | grep -i "intercept\|mirror" || echo "✔️  SIM path appears stable."

# === SECTION 7: OliviaAI Echo Mirror Check ===
echo; echo "🧠 OliviaAI echo-resonance check (if module installed)..."
if [ -f ~/TGDKModules/visceptar/echo_probe.sh ]; then
  bash ~/TGDKModules/visceptar/echo_probe.sh
else
  echo "⚠️  Echo probe module not found. Install OliviaAI:Visceptar."
fi

# === Final Echo ===
echo; echo "✅ Watcher Scan Complete — Report timestamp: $(date)"