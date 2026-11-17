from typing import Optional

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PostORM

# PostORM.slug es String(160): se deja margen para el sufijo "-N".
SLUG_MAX_LENGTH = 150


def make_slug(text: str) -> str:
    """'¿Qué aprendí con FastAPI?' -> 'que-aprendi-con-fastapi'"""
    return slugify(text, max_length=SLUG_MAX_LENGTH, word_boundary=True) or "post"


def ensure_unique_slug(db: Session, base_text: str,
                       exclude_id: Optional[int] = None) -> str:
    """Devuelve un slug que todavía no usa ningún post.

    Si 'mi-post' ya existe prueba 'mi-post-2', 'mi-post-3', etc.
    `exclude_id` permite ignorar al propio post (por si se regenera).
    """
    base = make_slug(base_text)
    candidate = base
    counter = 2

    while True:
        query = select(PostORM.id).where(PostORM.slug == candidate)
        if exclude_id is not None:
            query = query.where(PostORM.id != exclude_id)
        if db.execute(query).first() is None:
            return candidate
        candidate = f"{base}-{counter}"
        counter += 1
