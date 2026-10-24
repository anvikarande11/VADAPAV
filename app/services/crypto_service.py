from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def get_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return key

cipher_suite = Fernet(get_or_create_key())

def encrypt_file(file_bytes: bytes) -> bytes:
    """Encrypts raw file bytes into scrambled ciphertext."""
    return cipher_suite.encrypt(file_bytes)

def decrypt_file(encrypted_bytes: bytes) -> bytes:
    """Decrypts scrambled ciphertext back into original file bytes."""
    return cipher_suite.decrypt(encrypted_bytes)