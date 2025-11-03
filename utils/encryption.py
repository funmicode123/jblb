from cryptography.fernet import Fernet
import os

# Load key from environment (important for consistency)
FERNET_KEY = os.getenv("FERNET_SECRET_KEY")

if not FERNET_KEY:
    raise ValueError("Missing FERNET_SECRET_KEY in environment variables")

fernet = Fernet(FERNET_KEY.encode())

def encrypt_value(value: str) -> str:
    """Encrypts a string value."""
    if not value:
        return None
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    """Decrypts a string value."""
    if not encrypted_value:
        return None
    return fernet.decrypt(encrypted_value.encode()).decode()
