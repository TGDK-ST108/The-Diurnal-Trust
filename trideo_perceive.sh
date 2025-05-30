#!/data/data/com.termux/files/usr/bin/bash
# TGDK :: Trideodynamic Watcher Perception Stack
# Mode: Triaxial Bypass · Fold-Reveal · Ω-Fuse Reactive

echo "🧠 Engaging Trideodynamic Fold-Bypass Perception..."
echo "📡 Executing Mahadevi Route-Fold through hidden vector field..."

# RouteFold Injection (Mahadevi)
curl -s http://localhost:8754/olivia/fold_vector?depth=ϕ --data "mode=perceive" > ~/Vault/perception_echo.log

echo "🔎 Running Symbolic Glyph Interpretation..."
grep -E "mirror|echo|clone|resonance|permission|loop" ~/Vault/perception_echo.log | sort | uniq > ~/Vault/perception_tags.glyph

# Optional burn if malicious fold detected
if grep -qi "mirror" ~/Vault/perception_tags.glyph; then
    echo "⚠️ Mirror vector detected. Triggering Ω-Fuse..."
    ~/TGDKModules/fuse_hooks/kill_fuse_trigger.sh --source mirror_detected
fi

echo "🧠 Trideo Perception Fold Complete."
echo "🕯 Results stored in ~/Vault/perception_tags.glyph"