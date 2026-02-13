"""
Provides encryption and hashing utilities for sensitive data.
"""

import hashlib
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

_runtime_key: str | None = None


def generate_secret_key() -> str:
    """Generate a new Fernet key (base64 string)."""
    return Fernet.generate_key().decode()


def get_secret_key() -> str:
    """
    Resolve encryption key with this order:
    1) SECRET_KEY from .env/environment
    2) Runtime-generated key (if KEY_MODE=runtime or SECRET_KEY is missing)
    """
    global _runtime_key

    env_key = os.getenv("SECRET_KEY")
    key_mode = os.getenv("KEY_MODE", "env").strip().lower()

    if env_key:
        return env_key

    if key_mode == "runtime" or not env_key:
        if _runtime_key is None:
            _runtime_key = generate_secret_key()
        return _runtime_key

    raise ValueError("No encryption key available. Set SECRET_KEY or KEY_MODE=runtime.")


def _get_cipher() -> Fernet:
    key = get_secret_key()
    return Fernet(key.encode())

def encrypt_data(data: str) -> str:
    encrypted = _get_cipher().encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str) -> str:
    decrypted = _get_cipher().decrypt(encrypted_data.encode())
    return decrypted.decode()


def hash_data(data: str, salt: str = "") -> str:
    """Return deterministic SHA-256 hash for a value."""
    payload = f"{salt}{data}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def hash_sensitive_fields(record: dict, fields: list[str], salt: str = "") -> dict:
    """Return a copy where selected fields are replaced by SHA-256 hashes."""
    hashed = dict(record)
    for field in fields:
        value = hashed.get(field)
        if value is None or value == "":
            hashed[field] = ""
            continue
        hashed[field] = hash_data(str(value), salt=salt)
    return hashed
