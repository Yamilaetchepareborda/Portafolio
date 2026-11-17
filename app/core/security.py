import os
import secrets
import warnings
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import UserORM

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    # Solo para no frenar el desarrollo: sin JWT_SECRET los tokens dejan
    # de valer cada vez que se reinicia el servidor.
    warnings.warn("JWT_SECRET no está definido en .env: se usa uno aleatorio.")
    JWT_SECRET = secrets.token_urlsafe(48)
JWT_ALG = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Argon2 (recomendado por pwdlib).
password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Jerarquía de roles: cada nivel incluye los permisos del anterior.
ROLE_LEVELS = {"user": 0, "editor": 1, "admin": 2}

credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticado",
    headers={"WWW-Authenticate": "Bearer"}
)


def raise_expired_token():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expirado",
        headers={"WWW-Authenticate": "Bearer"}
    )


def raise_forbidden():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tenés permisos suficientes",
    )


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(tz=timezone.utc) + \
        (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload=payload, key=JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    return jwt.decode(jwt=token, key=JWT_SECRET, algorithms=[JWT_ALG])


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> UserORM:
    try:
        payload = decode_token(token)
        sub: Optional[str] = payload.get("sub")
        if not sub or not sub.isdigit():
            raise credentials_exc
    except ExpiredSignatureError:
        raise raise_expired_token()
    except InvalidTokenError:
        raise credentials_exc

    user = db.get(UserORM, int(sub))
    if not user:
        raise credentials_exc
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Usuario inactivo")
    return user


def require_role(min_role: str):
    """Dependencia: deja pasar al usuario si su rol es >= min_role.

    Uso: user = Depends(require_role("editor"))
    """
    required_level = ROLE_LEVELS[min_role]

    def checker(user: UserORM = Depends(get_current_user)) -> UserORM:
        if ROLE_LEVELS.get(user.role, -1) < required_level:
            raise raise_forbidden()
        return user

    return checker
