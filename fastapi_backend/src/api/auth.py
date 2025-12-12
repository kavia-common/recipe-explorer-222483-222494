import base64
import hashlib
import hmac
import os
import time
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.orm import Session

from .db import get_db
from .models import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
TOKEN_TTL_SECONDS = int(os.getenv("TOKEN_TTL_SECONDS", "86400"))  # 1 day

def hash_password(password: str) -> str:
    salt = os.getenv("PASSWORD_SALT", "salt")
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)

def _sign(data: str) -> str:
    sig = hmac.new(SECRET_KEY.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode("utf-8")

# PUBLIC_INTERFACE
def create_token(user_id: int) -> str:
    """Create a simple HMAC signed token containing user_id and expiry timestamp."""
    exp = int(time.time()) + TOKEN_TTL_SECONDS
    payload = f"{user_id}.{exp}"
    sig = _sign(payload)
    token = f"{payload}.{sig}"
    return base64.urlsafe_b64encode(token.encode("utf-8")).decode("utf-8")

def decode_token(token: str) -> Optional[int]:
    try:
        raw = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        parts = raw.split(".")
        if len(parts) != 3:
            return None
        user_id = int(parts[0])
        exp = int(parts[1])
        sig = parts[2]
        if not hmac.compare_digest(sig, _sign(f"{user_id}.{exp}")):
            return None
        if time.time() > exp:
            return None
        return user_id
    except Exception:
        return None

bearer_scheme = HTTPBearer(auto_error=False)

# PUBLIC_INTERFACE
def get_current_user(db: Session = Depends(get_db), creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> User:
    """Security dependency: validate bearer token and return current User."""
    if not creds or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = decode_token(creds.credentials)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return user
