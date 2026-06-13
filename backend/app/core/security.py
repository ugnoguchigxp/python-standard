import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Union
import hmac
import hashlib
from pwdlib import PasswordHash
from app.core.config import settings

# Initialize Argon2 password hashing via pwdlib
password_hash = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        return False

def create_access_token(subject: Union[str, Any], expires_delta: Union[timedelta, None] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
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
        
        payload = f"{subject}:{exp_str}:{nonce}"
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
            
        expiration = int(exp_str)
        if datetime.now(timezone.utc).timestamp() > expiration:
            return None
            
        return subject
    except Exception:
        return None
