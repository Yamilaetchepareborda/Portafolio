from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_role
from app.models import UserORM
from .repository import TagRepository
from .schemas import PaginatedTags, TagCreate, TagPublic, TagUpdate, TagWithCount

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=PaginatedTags)
def list_tags(
    search: Optional[str] = Query(None, max_length=30,
                                  description="Buscar por nombre"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    order_by: Literal["id", "name"] = Query("name"),
    direction: Literal["asc", "desc"] = Query("asc"),
    db: Session = Depends(get_db),
):
    result = TagRepository(db).search(search, page, per_page, order_by, direction)
    total, pages = result["total"], result["pages"]
    current = 1 if pages == 0 else min(page, pages)
    return PaginatedTags(
        page=current, per_page=per_page, total=total, total_pages=pages,
        has_prev=current > 1, has_next=current < pages,
        search=search, items=result["items"],
    )


# Va antes de /{tag_id}: si no, FastAPI intentaría convertir
# "most-popular" a entero y respondería 422.
@router.get("/most-popular", response_model=TagWithCount)
def most_popular_tag(db: Session = Depends(get_db)):
    tag = TagRepository(db).most_popular()
    if not tag:
        raise HTTPException(status_code=404, detail="Todavía no hay tags en uso")
    return tag


@router.get("/{tag_id}", response_model=TagPublic)
def get_tag(tag_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    tag = TagRepository(db).get(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")
    return tag


@router.post("", response_model=TagPublic, status_code=status.HTTP_201_CREATED)
def create_tag(data: TagCreate, db: Session = Depends(get_db),
               _user: UserORM = Depends(require_role("editor"))):
    repository = TagRepository(db)
    try:
        tag = repository.create(data.name)
        db.commit()
        db.refresh(tag)
        return tag
    except (ValueError, IntegrityError):
        db.rollback()
        raise HTTPException(status_code=409, detail="La etiqueta ya existe")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear la etiqueta")


@router.put("/{tag_id}", response_model=TagPublic)
def update_tag(data: TagUpdate, tag_id: int = Path(..., ge=1),
               db: Session = Depends(get_db),
               _user: UserORM = Depends(require_role("editor"))):
    repository = TagRepository(db)
    tag = repository.get(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")
    try:
        tag = repository.update(tag, data.model_dump(exclude_unset=True))
        db.commit()
        db.refresh(tag)
        return tag
    except (ValueError, IntegrityError):
        db.rollback()
        raise HTTPException(status_code=409, detail="La etiqueta ya existe")


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int = Path(..., ge=1), db: Session = Depends(get_db),
               _admin: UserORM = Depends(require_role("admin"))):
    repository = TagRepository(db)
    tag = repository.get(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")
    try:
        repository.delete(tag)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar la etiqueta")
