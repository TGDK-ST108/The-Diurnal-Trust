#!/usr/bin/env python3
# TGDK :: Stegdox.Sword CounterOps Module
# BFE-TGDK-STEGDOX-001 :: Encrypted Payload Carrier + OliviaAI Beacon

from PIL import Image
import stepic
import sys
import os
from datetime import datetime
from Crypto.Cipher import AES
import base64
import hashlib

LOGFILE = "stegdox_sword.log"
BEACON_TAG = "[TGDK::OliviaAI::SWORD-PAYLOAD]"

def log(msg):
    with open(LOGFILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(f"[Stegdox.Sword] {msg}")

def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

def unpad(s):
    return s[:-ord(s[-1])]

def aes_encrypt(msg, password):
    key = hashlib.sha256(password.encode()).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    raw = pad(msg)
    enc = cipher.encrypt(raw.encode())
    return base64.b64encode(enc).decode()

def aes_decrypt(enc_msg, password):
    try:
        key = hashlib.sha256(password.encode()).digest()
        cipher = AES.new(key, AES.MODE_ECB)
        raw = base64.b64decode(enc_msg)
        dec = cipher.decrypt(raw).decode()
        return unpad(dec)
    except:
        return "[DECRYPTION FAILED]"

def encode_image(input_path, output_path, message, password=None):
    try:
        img = Image.open(input_path).convert("RGB")
        final_message = BEACON_TAG + " " + (aes_encrypt(message, password) if password else message)
        stego = stepic.encode(img, final_message.encode('utf-8'))
        stego.save(output_path, "PNG")
        log(f"Payload embedded in {output_path}")
    except Exception as e:
        log(f"Encoding failed: {e}")

def decode_image(image_path, password=None):
    try:
        img = Image.open(image_path).convert("RGB")
        data = stepic.decode(img)
        log("Raw Extracted Data: " + data)
        if BEACON_TAG in data:
            content = data.split(BEACON_TAG)[-1].strip()
            decrypted = aes_decrypt(content, password) if password else content
            log("Decoded Payload: " + decrypted)
        else:
            log("No TGDK beacon found.")
    except Exception as e:
        log(f"Decoding failed: {e}")

def usage():
    print("Usage:")
    print("  Encode: stegdox_sword.py encode <in.png> <out.png> <'message'> [password]")
    print("  Decode: stegdox_sword.py decode <in.png> [password]")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "encode" and (len(sys.argv) == 5 or len(sys.argv) == 6):
        in_file = sys.argv[2]
        out_file = sys.argv[3]
        msg = sys.argv[4]
        pwd = sys.argv[5] if len(sys.argv) == 6 else None
        encode_image(in_file, out_file, msg, pwd)
    elif cmd == "decode" and (len(sys.argv) == 3 or len(sys.argv) == 4):
        in_file = sys.argv[2]
        pwd = sys.argv[3] if len(sys.argv) == 4 else None
        decode_image(in_file, pwd)
    else:
        usage()