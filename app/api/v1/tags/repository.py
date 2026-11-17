from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import PostORM, TagORM, post_tags
from app.services.pagination import paginate_query


class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, tag_id: int) -> Optional[TagORM]:
        return self.db.get(TagORM, tag_id)

    def get_by_name(self, name: str) -> Optional[TagORM]:
        return self.db.execute(
            select(TagORM).where(func.lower(TagORM.name) == name.strip().lower())
        ).scalar_one_or_none()

    def search(self, search: Optional[str], page: int, per_page: int,
             order_by: str = "name", direction: str = "asc") -> dict:
        query = select(TagORM)
        if search:
            query = query.where(TagORM.name.ilike(f"%{search.strip()}%"))

        return paginate_query(
            self.db, TagORM, base_query=query, page=page, per_page=per_page,
            order_by=order_by, direction=direction,
            allowed_order={"id": TagORM.id, "name": func.lower(TagORM.name)},
        )

    def create(self, name: str) -> TagORM:
        normalized = name.strip().lower()
        if self.get_by_name(normalized):
            raise ValueError("La etiqueta ya existe")

        tag = TagORM(name=normalized)
        self.db.add(tag)
        self.db.flush()
        return tag

    def update(self, tag: TagORM, updates: dict) -> TagORM:
        new_name = updates.get("name")
        if new_name:
            existing = self.get_by_name(new_name)
            if existing and existing.id != tag.id:
                raise ValueError("La etiqueta ya existe")
            tag.name = new_name.strip().lower()
        self.db.flush()
        return tag

    def delete(self, tag: TagORM) -> None:
        self.db.delete(tag)

    def most_popular(self) -> Optional[dict]:
        """Tag más usado: JOIN tags ↔ post_tags ↔ posts, GROUP BY tag."""
        uses = func.count(PostORM.id).label("uses")
        row = self.db.execute(
            select(TagORM, uses)
            .join(post_tags, post_tags.c.tag_id == TagORM.id)
            .join(PostORM, PostORM.id == post_tags.c.post_id)
            .group_by(TagORM.id)
            .order_by(uses.desc(), TagORM.name.asc())
            .limit(1)
        ).first()

        if row is None:
            return None

        tag, count = row
        return {"id": tag.id, "name": tag.name, "uses": count}

    def with_counts(self, limit: Optional[int] = None) -> List[dict]:
        """Todos los tags que tienen al menos un post, con su cantidad de usos.
        Lo usan los chips de filtro del blog."""
        uses = func.count(PostORM.id).label("uses")
        query = (
            select(TagORM, uses)
            .join(post_tags, post_tags.c.tag_id == TagORM.id)
            .join(PostORM, PostORM.id == post_tags.c.post_id)
            .group_by(TagORM.id)
            .order_by(uses.desc(), TagORM.name.asc())
        )
        if limit:
            query = query.limit(limit)
        return [{"id": t.id, "name": t.name, "uses": c}
                for t, c in self.db.execute(query).all()]
