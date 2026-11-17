from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, DateTime, UniqueConstraint, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from .category import CategoryORM
    from .tag import TagORM
    from .user import UserORM

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey(
        "posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)


class PostORM(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("title", name="unique_post_title"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    # Link al repositorio (botón "Ver en GitHub" en los proyectos).
    repo_url: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc))

    # El post queda vinculado al usuario real que lo creó (reemplaza a
    # AuthorORM). Si se borra el usuario, el post se conserva sin autor.
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user: Mapped[Optional["UserORM"]] = relationship(
        back_populates="posts", lazy="joined")

    # Categoría opcional: si se borra la categoría, el post queda sin ella.
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True, index=True)
    category: Mapped[Optional["CategoryORM"]] = relationship(
        back_populates="posts", lazy="joined")

    tags: Mapped[List["TagORM"]] = relationship(
        secondary=post_tags,
        back_populates="posts",
        lazy="selectin",
        passive_deletes=True
    )
