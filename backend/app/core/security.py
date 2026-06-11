import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Union
import hmac

from app.core.config import settings

# A simple, secure password hashing using Python's standard hashlib (PBKDF2)
# This avoids external native dependencies like bcrypt or argon2 in the baseline.
def get_password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000, # Number of iterations
    )
    return f"pbkdf2_sha256$100000${salt.hex()}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password.startswith("pbkdf2_sha256$"):
        return False
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4:
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        stored_key = bytes.fromhex(parts[3])
        
        new_key = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(stored_key, new_key)
    except Exception:
        return False


# Token helper stubs for the baseline
def create_access_token(subject: Union[str, Any], expires_delta: Union[timedelta, None] = None) -> str:
    # A simple token generation for the baseline.
    # Returns a signed token string or simple secure token.
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add a random nonce to make every token unique
    nonce = secrets.token_hex(4)
    payload = f"{subject}:{int(expire.timestamp())}:{nonce}"
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return f"{payload}:{signature}"


def verify_access_token(token: str) -> Union[str, None]:
    try:
        parts = token.split(":")
        if len(parts) != 4:
            return None
        subject, exp_str, nonce, signature = parts
        
        # Verify signature
        payload = f"{subject}:{exp_str}:{nonce}"
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
            
        # Check expiration
        expiration = int(exp_str)
        if datetime.now(timezone.utc).timestamp() > expiration:
            return None
            
        return subject
    except Exception:
        return None
