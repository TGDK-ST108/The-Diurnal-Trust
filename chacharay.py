from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.backends import default_backend
import os

# Generate a random 256-bit (32-byte) key for ChaCha20-Poly1305
key = ChaCha20Poly1305.generate_key()
cipher = ChaCha20Poly1305(key)

# Example "ray" (input message)
ray = b"Return the shield"

# Encrypt the ray to produce the shield (ciphertext + tag)
nonce = os.urandom(12)  # 96-bit nonce
shield = cipher.encrypt(nonce, ray, associated_data=None)

# Decrypt the shield to retrieve the ray
retrieved_ray = cipher.decrypt(nonce, shield, associated_data=None)

# Output
print("Key (hex):", key.hex())
print("Nonce (hex):", nonce.hex())
print("Ray:", ray.decode())
print("Shield (hex):", shield.hex())
print("Retrieved Ray:", retrieved_ray.decode())
print("Integrity Check:", retrieved_ray == ray)
