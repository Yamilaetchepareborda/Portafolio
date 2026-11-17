from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.users.repository import UserRepository
from app.api.v1.users.schemas import UserCreate, UserLogin, UserPublic
from app.core.db import get_db
from app.core.security import create_access_token, get_current_user
from app.models import UserORM
from .schemas import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic,
             status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Registro público: siempre crea usuarios con rol `user`.
    Los roles editor/admin los asigna un admin."""
    repository = UserRepository(db)
    try:
        user = repository.create(email=data.email, password=data.password,
                                 full_name=data.full_name, role="user")
        db.commit()
        db.refresh(user)
        return user
    except (ValueError, IntegrityError):
        db.rollback()
        raise HTTPException(status_code=409, detail="El email ya está registrado")


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm llama "username" al campo: acá es el email.
    user = UserRepository(db).authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Usuario inactivo")

    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.post("/login-json", response_model=Token)
def login_json(data: UserLogin, db: Session = Depends(get_db)):
    """Mismo login pero con JSON ({email, password}), para clientes que no
    usan formularios. Swagger usa /auth/login (botón Authorize)."""
    user = UserRepository(db).authenticate(data.email, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Credenciales inválidas",
                            headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Usuario inactivo")
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.get("/me", response_model=UserPublic)
def read_me(current: UserORM = Depends(get_current_user)):
    return current
