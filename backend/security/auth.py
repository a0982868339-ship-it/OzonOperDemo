import os
import json
import base64
import hmac
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models.user import User


security = HTTPBearer()


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_jwt(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_enc = b64url_encode(json.dumps(header).encode())
    payload_enc = b64url_encode(json.dumps(payload).encode())
    msg = f"{header_enc}.{payload_enc}".encode()
    signature = hmac.new(secret.encode(), msg, hashlib.sha256).digest()
    sig_enc = b64url_encode(signature)
    return f"{header_enc}.{payload_enc}.{sig_enc}"


def verify_jwt(token: str, secret: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    header = json.loads(b64url_decode(parts[0]).decode())
    payload = json.loads(b64url_decode(parts[1]).decode())
    algo = header.get("alg", "HS256")
    if algo != "HS256":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unsupported alg")
    msg = f"{parts[0]}.{parts[1]}".encode()
    expected = hmac.new(secret.encode(), msg, hashlib.sha256).digest()
    actual = b64url_decode(parts[2])
    if not hmac.compare_digest(expected, actual):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad signature")
    return payload


def get_db() -> Session:
    return SessionLocal()


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    secret = os.environ.get("AUTH_SECRET", "ozon-demo-secret")
    payload = verify_jwt(token, secret)
    email = payload.get("email") or payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid payload")
    with get_db() as db:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found")
        if user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user


def admin_required(user: User = Depends(get_current_admin)) -> User:
    return user
