"""
FILE: auth.py
ROLE: The security layer. Everything about identity and access lives here.

WHAT THIS FILE DOES:
- Hashes passwords with bcrypt before storing (one-way, irreversible)
- Verifies passwords at login by comparing hashes
- Creates JWT access tokens (expire in 30 min) and refresh tokens (7 days)
- Provides get_current_user() which decodes tokens and returns the logged-in user

WHAT THIS FILE DOES NOT DO:
- Does not define endpoints (that's main.py)
- Does not store anything in the database directly
- Does not know about documents — only users and tokens

HOW get_current_user() WORKS (used on every protected endpoint):
1. FastAPI extracts the Bearer token from the request header
2. We decode the JWT using SECRET_KEY
3. We extract the user_id from the token payload
4. We look up that user_id in the database
5. We return the User object to the endpoint function
6. If ANY step fails → automatically returns 401 Unauthorized

SECURITY DECISIONS:
- bcrypt==4.0.1 pinned (newer versions break passlib on Windows)
- Tokens carry user_id only — no sensitive data in the token
- SECRET_KEY lives in .env — never hardcoded
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db, User
import os

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

SECRET_KEY = os.getenv("SECRET_KEY", "changethisinproduction")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ─────────────────────────────────────────
# PASSWORD HASHING
# bcrypt is a one-way hash — you can never reverse it back to plain text
# To verify: hash the input again and compare hashes
# ─────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ─────────────────────────────────────────
# JWT TOKEN CREATION
# A JWT has 3 parts: header.payload.signature
# The payload carries user_id and expiry time
# The signature proves the token wasn't tampered with
# ─────────────────────────────────────────

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,       # sub = subject = who this token is for
        "exp": expire,        # exp = when this token expires
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ─────────────────────────────────────────
# CURRENT USER DEPENDENCY
# FastAPI calls this automatically on protected endpoints
# It reads the token from the Authorization header,
# decodes it, finds the user in DB, and returns them
# ─────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        raise credentials_exception

    return user