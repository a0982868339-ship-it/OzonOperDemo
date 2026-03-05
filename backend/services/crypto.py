import base64
import os
from cryptography.fernet import Fernet


def get_fernet() -> Fernet:
    raw_key = os.environ.get("AI_CONFIG_KEY", "")
    if raw_key:
        # User provided key must be valid 32-byte base64
        return Fernet(raw_key.encode())
    else:
        # Hardcoded default key for dev environment (must be 32 bytes URL-safe base64)
        # "ozon-ai-config-key-32-bytes!!" is 29 bytes, not 32. 
        # Let's use a proper generated key for default dev mode.
        # This is a fixed key for dev purposes so data persists across restarts.
        default_key = b'W7v4o8z9P5q2R1s0T3u6V9y2X5z8A1b4C7d0E3f6G9h='
        return Fernet(default_key)


def encrypt_value(value: str) -> str:
    return get_fernet().encrypt(value.encode()).decode()


def decrypt_value(value: str) -> str:
    return get_fernet().decrypt(value.encode()).decode()
