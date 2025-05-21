#!/data/data/com.termux/files/usr/bin/bash
# TGDK DUDE :: TETRADEN COMPILE WRAPPER

echo "[TGDK] Starting compilation for The-Diurnal-Trust..."

mkdir -p bin

# Compile C files
echo "[+] Compiling C modules..."
clang -O3 Dioluminousity.c -o bin/Dioluminousity
clang -O3 HeliosPhatPenetrator.c -o bin/HeliosPhatPenetrator
clang -O3 TRINITY.c -o bin/TRINITY
clang -O3 eQ5o1.c -o bin/eQ5o1
clang -O3 ghost_mode.c -o bin/ghost_mode

# Compile C++ files
echo "[+] Compiling C++ modules..."
clang++ -O3 activate.cpp -o bin/activate
clang++ -O3 conda_capsule.cpp -o bin/conda_capsule
clang++ -O3 ext.cpp -o bin/ext
clang++ -O3 qquap_e_stub.cpp -o bin/qquap_e_stub
clang++ -O3 smirf.cpp -o bin/smirf

# Python: check & echo
echo "[+] Validating Python modules..."
for py in coderight.py mathCalligula.py vector_court.py; do
  python3 -m py_compile $py && echo "OK: $py"
done

# Bash: grant exec + validate
echo "[+] Preparing Bash scripts..."
chmod +x *.bash ghost_mode.sh

echo "[+] DONE. Launchable binaries in ./bin/"
ls -al bin/