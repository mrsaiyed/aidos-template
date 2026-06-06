import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC
from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from app.utils.config import SECRET_KEY
from app.db.database import get_db
from app.models.user import User

ALGORITHM = "HS256"
SESSION_EXPIRY_HOURS = 24


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_session_token(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(hours=SESSION_EXPIRY_HOURS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_session_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(
    session_token: str = Cookie(None),
    db: Session = Depends(get_db),
) -> User:
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_session_token(session_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid session token")
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(status_code=401, detail="Invalid session token")
    user = db.query(User).filter(User.id == int(user_id_str)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
