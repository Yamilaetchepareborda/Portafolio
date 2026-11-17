from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import CategoryORM, PostORM


class SlugInUseError(ValueError):
    pass


class NameInUseError(ValueError):
    pass


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, category_id: int) -> Optional[CategoryORM]:
        return self.db.get(CategoryORM, category_id)

    def get_by_slug(self, slug: str) -> Optional[CategoryORM]:
        return self.db.execute(
            select(CategoryORM).where(CategoryORM.slug == slug.strip().lower())
        ).scalar_one_or_none()

    def get_by_name(self, name: str) -> Optional[CategoryORM]:
        return self.db.execute(
            select(CategoryORM).where(
                func.lower(CategoryORM.name) == name.strip().lower())
        ).scalar_one_or_none()

    def list(self) -> List[CategoryORM]:
        return list(self.db.execute(
            select(CategoryORM).order_by(CategoryORM.name.asc())
        ).scalars().all())

    def with_counts(self) -> List[dict]:
        """Categorías con la cantidad de posts (para los filtros del blog)."""
        count = func.count(PostORM.id)
        rows = self.db.execute(
            select(CategoryORM, count)
            .outerjoin(PostORM, PostORM.category_id == CategoryORM.id)
            .group_by(CategoryORM.id)
            .order_by(CategoryORM.name.asc())
        ).all()
        return [{"id": c.id, "name": c.name, "slug": c.slug, "uses": n}
                for c, n in rows]

    def _check_unique(self, name: Optional[str], slug: Optional[str],
                      exclude_id: Optional[int] = None) -> None:
        if slug:
            found = self.get_by_slug(slug)
            if found and found.id != exclude_id:
                raise SlugInUseError("Slug en uso")
        if name:
            found = self.get_by_name(name)
            if found and found.id != exclude_id:
                raise NameInUseError("Ya existe una categoría con ese nombre")

    def create(self, name: str, slug: str) -> CategoryORM:
        self._check_unique(name, slug)
        category = CategoryORM(name=name.strip(), slug=slug.strip().lower())
        self.db.add(category)
        self.db.flush()
        return category

    def update(self, category: CategoryORM, updates: dict) -> CategoryORM:
        self._check_unique(updates.get("name"), updates.get("slug"),
                           exclude_id=category.id)
        for key, value in updates.items():
            if value is not None:
                setattr(category, key, value.strip())
        self.db.flush()
        return category

    def delete(self, category: CategoryORM) -> None:
        self.db.delete(category)
