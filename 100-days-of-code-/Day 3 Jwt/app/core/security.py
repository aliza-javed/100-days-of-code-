"""PBKDF2-HMAC-SHA256 password hashing (stdlib only)."""
import hashlib
import hmac
import os


def hash_password(plain: str) -> str:
    """
    Hash password using PBKDF2-HMAC-SHA256.
    Format: pbkdf2$<salt_hex>$<hash_hex>
    """
    salt = os.urandom(32)
    key  = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt, 260_000)
    return f"pbkdf2${salt.hex()}${key.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time verification of a plain password against its hash."""
    try:
        _, salt_hex, key_hex = hashed.split("$")
        salt    = bytes.fromhex(salt_hex)
        stored  = bytes.fromhex(key_hex)
        derived = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt, 260_000)
        return hmac.compare_digest(derived, stored)
    except Exception:
        return False
