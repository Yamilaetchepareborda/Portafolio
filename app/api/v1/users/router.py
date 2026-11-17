from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_role
from app.models import UserORM
from .repository import UserRepository
from .schemas import PaginatedUsers, UserPublic, UserRoleUpdate, UserUpdate

# Toda la gestión de usuarios es solo para admin (nivel 2).
router = APIRouter(prefix="/users", tags=["users"])


def _get_or_404(repository: UserRepository, user_id: int) -> UserORM:
    user = repository.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("", response_model=PaginatedUsers)
def list_users(
    search: Optional[str] = Query(None, max_length=255,
                                  description="Buscar por email"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _admin: UserORM = Depends(require_role("admin")),
):
    result = UserRepository(db).search(search, page, per_page)
    pages = result["pages"]
    current = 1 if pages == 0 else min(page, pages)
    return PaginatedUsers(page=current, per_page=per_page, total=result["total"],
                          total_pages=pages, has_prev=current > 1,
                          has_next=current < pages, items=result["items"])


@router.get("/{user_id}", response_model=UserPublic)
def get_user(user_id: int = Path(..., ge=1), db: Session = Depends(get_db),
             _admin: UserORM = Depends(require_role("admin"))):
    return _get_or_404(UserRepository(db), user_id)


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(data: UserUpdate, user_id: int = Path(..., ge=1),
                db: Session = Depends(get_db),
                _admin: UserORM = Depends(require_role("admin"))):
    repository = UserRepository(db)
    user = repository.update(_get_or_404(repository, user_id),
                             data.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/role", response_model=UserPublic)
def change_role(data: UserRoleUpdate, user_id: int = Path(..., ge=1),
                db: Session = Depends(get_db),
                admin: UserORM = Depends(require_role("admin"))):
    repository = UserRepository(db)
    user = _get_or_404(repository, user_id)
    if user.id == admin.id and data.role != "admin":
        raise HTTPException(status_code=400,
                            detail="No podés quitarte el rol de admin a vos misma")
    user = repository.update(user, {"role": data.role})
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int = Path(..., ge=1), db: Session = Depends(get_db),
                admin: UserORM = Depends(require_role("admin"))):
    repository = UserRepository(db)
    user = _get_or_404(repository, user_id)
    if user.id == admin.id:
        raise HTTPException(status_code=400,
                            detail="No podés eliminar tu propio usuario")
    try:
        repository.delete(user)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar el usuario")
