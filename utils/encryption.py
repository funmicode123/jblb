# from cryptography.fernet import Fernet
# import os


# FERNET_KEY = os.getenv("FERNET_SECRET_KEY")

# # if not FERNET_KEY:
# #     raise ValueError("Missing FERNET_SECRET_KEY in environment variables")


# fernet = Fernet(FERNET_KEY.encode())


# def encrypt_value(value):
#     if not isinstance(value, str):
#         value = str(value)
#     return fernet.encrypt(value.encode()).decode()


# def decrypt_value(encrypted_value: str) -> str:
#     """Decrypts a string value."""
#     if not encrypted_value:
#         return None
#     return fernet.decrypt(encrypted_value.encode()).decode()

from cryptography.fernet import Fernet
import os
from functools import lru_cache


@lru_cache()
def get_fernet():
    key = os.getenv("FERNET_SECRET_KEY")
    if not key:
        raise ValueError("Missing FERNET_SECRET_KEY in environment variables")
    return Fernet(key.encode())


def encrypt_value(value):
    if value is None:
        return None

    if not isinstance(value, str):
        value = str(value)

    fernet = get_fernet()
    return fernet.encrypt(value.encode()).decode()


def decrypt_value(encrypted_value: str) -> str:
    if not encrypted_value:
        return None

    fernet = get_fernet()
    return fernet.decrypt(encrypted_value.encode()).decode()

