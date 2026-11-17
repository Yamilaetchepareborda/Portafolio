from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_role
from app.models import CategoryORM, UserORM
from .repository import CategoryRepository, NameInUseError, SlugInUseError
from .schemas import CategoryCreate, CategoryPublic, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


def _get_or_404(repository: CategoryRepository, category_id: int) -> CategoryORM:
    category = repository.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


@router.get("", response_model=List[CategoryPublic])
def list_categories(db: Session = Depends(get_db)):
    return CategoryRepository(db).list()


@router.get("/slug/{slug}", response_model=CategoryPublic)
def get_category_by_slug(slug: str, db: Session = Depends(get_db)):
    category = CategoryRepository(db).get_by_slug(slug)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


@router.get("/{category_id}", response_model=CategoryPublic)
def get_category(category_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    return _get_or_404(CategoryRepository(db), category_id)


@router.post("", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db),
                    _user: UserORM = Depends(require_role("editor"))):
    repository = CategoryRepository(db)
    try:
        category = repository.create(data.name, data.slug)
        db.commit()
        db.refresh(category)
        return category
    except SlugInUseError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Slug en uso")
    except (NameInUseError, IntegrityError):
        db.rollback()
        raise HTTPException(status_code=409,
                            detail="Ya existe una categoría con ese nombre")


@router.put("/{category_id}", response_model=CategoryPublic)
def update_category(data: CategoryUpdate, category_id: int = Path(..., ge=1),
                    db: Session = Depends(get_db),
                    _user: UserORM = Depends(require_role("editor"))):
    repository = CategoryRepository(db)
    category = _get_or_404(repository, category_id)
    try:
        category = repository.update(category, data.model_dump(exclude_unset=True))
        db.commit()
        db.refresh(category)
        return category
    except SlugInUseError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Slug en uso")
    except (NameInUseError, IntegrityError):
        db.rollback()
        raise HTTPException(status_code=409,
                            detail="Ya existe una categoría con ese nombre")


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int = Path(..., ge=1), db: Session = Depends(get_db),
                    _admin: UserORM = Depends(require_role("admin"))):
    """Borra la categoría. Sus posts NO se borran: quedan con category_id nulo."""
    repository = CategoryRepository(db)
    category = _get_or_404(repository, category_id)
    try:
        repository.delete(category)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar la categoría")
