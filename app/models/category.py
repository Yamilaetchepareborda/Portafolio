from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from .post import PostORM


class CategoryORM(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(60), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(
        String(60), unique=True, index=True, nullable=False)

    # passive_deletes: al borrar la categoría, la base pone category_id en
    # NULL (ON DELETE SET NULL) y los posts se conservan.
    posts: Mapped[List["PostORM"]] = relationship(
        back_populates="category", passive_deletes=True)
