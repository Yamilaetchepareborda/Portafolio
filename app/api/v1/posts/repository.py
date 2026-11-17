from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.models import PostORM, TagORM, UserORM
from app.services.pagination import paginate_query


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, post_id: int) -> Optional[PostORM]:
        post_find = select(PostORM).where(PostORM.id == post_id)
        return self.db.execute(post_find).scalar_one_or_none()

    def filtered_query(self, query: Optional[str] = None,
                       tag: Optional[str] = None):
        """Consulta base con los filtros opcionales. La reutilizan la API y
        las páginas web, así los dos lados filtran igual."""
        results = select(PostORM)

        if query:
            results = results.where(PostORM.title.ilike(f"%{query.strip()}%"))
        if tag:
            results = results.where(
                PostORM.tags.any(func.lower(TagORM.name) == tag.strip().lower()))
        return results

    def search(self, query: Optional[str], order_by: str, direction: str,
               page: int, per_page: int, tag: Optional[str] = None
               ) -> Tuple[int, List[PostORM]]:
        # Paginación global (app/services/pagination.py): el total se cuenta
        # sobre la consulta filtrada.
        page_data = paginate_query(
            self.db, PostORM, base_query=self.filtered_query(query, tag),
            page=page, per_page=per_page,
            order_by=order_by, direction=direction,
            allowed_order={"id": PostORM.id,
                           "title": func.lower(PostORM.title),
                           "created_at": PostORM.created_at},
        )
        return page_data["total"], page_data["items"]

    def by_tags(self, tags: List[str]) -> List[PostORM]:
        normalized_tag_names = [tag.strip().lower()
                                for tag in tags if tag.strip()]

        if not normalized_tag_names:
            return []

        post_list = (
            select(PostORM)
            .options(selectinload(PostORM.tags))
            .where(PostORM.tags.any(func.lower(TagORM.name).in_(normalized_tag_names)))
            .order_by(PostORM.id.asc())
        )

        return self.db.execute(post_list).scalars().unique().all()

    def ensure_tag(self, name: str) -> TagORM:
        name = name.strip().lower()
        tag_obj = self.db.execute(
            select(TagORM).where(func.lower(TagORM.name) == name)).scalar_one_or_none()

        if tag_obj:
            return tag_obj

        tag_obj = TagORM(name=name)
        self.db.add(tag_obj)
        self.db.flush()

        return tag_obj

    def create_post(self, title: str, content: str, user: Optional[UserORM],
                    tags: List[dict], image_url: Optional[str],
                    repo_url: Optional[str] = None) -> PostORM:
        post = PostORM(title=title, content=content, image_url=image_url,
                       repo_url=repo_url, user=user)
        for tag in tags:
            tag_obj = self.ensure_tag(tag["name"])
            post.tags.append(tag_obj)

        self.db.add(post)
        self.db.flush()
        self.db.refresh(post)
        return post

    def update_post(self, post: PostORM, updates: dict) -> PostORM:
        for key, value in updates.items():
            setattr(post, key, value)

        return post

    def delete_post(self, post: PostORM) -> None:
        self.db.delete(post)
