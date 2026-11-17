import os
from contextlib import contextmanager
from typing import Iterator

from dotenv import load_dotenv
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import CategoryORM, PostORM, TagORM, UserORM
from app.seeds.data import ADMIN_EMAIL, CATEGORIES, POSTS, TAGS, USERS
from app.utils.slugify_utils import ensure_unique_slug, make_slug

load_dotenv()


class SeedError(Exception):
    pass


@contextmanager
def atomic(db: Session) -> Iterator[Session]:
    """Todo o nada: commit al final o rollback si algo falla."""
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise


def _password_for(user: dict) -> str:
    env_var = user["password_env"]
    password = os.getenv(env_var)
    if not password:
        raise SeedError(f"Falta {env_var} en el .env (ver .env.example).")
    if len(password) < 8:
        raise SeedError(f"{env_var} tiene que tener al menos 8 caracteres.")
    return password


# ---------- upserts: si existe (por email/slug/nombre) se actualiza, si no se crea


def seed_users(db: Session) -> str:
    created = updated = 0
    with atomic(db):
        for data in USERS:
            password = _password_for(data)
            email = data["email"].strip().lower()
            user = db.execute(
                select(UserORM).where(func.lower(UserORM.email) == email)
            ).scalar_one_or_none()

            if user is None:
                user = UserORM(email=email, hashed_password=hash_password(password))
                db.add(user)
                created += 1
            else:
                # Solo se re-hashea si cambió la contraseña del .env.
                if not verify_password(password, user.hashed_password):
                    user.hashed_password = hash_password(password)
                updated += 1

            user.full_name = data["full_name"]
            user.role = data["role"]
            user.is_active = True
    return f"Usuarios: {created} creados, {updated} actualizados"


def seed_categories(db: Session) -> str:
    created = updated = 0
    with atomic(db):
        for data in CATEGORIES:
            category = db.execute(
                select(CategoryORM).where(CategoryORM.slug == data["slug"])
            ).scalar_one_or_none()
            if category is None:
                db.add(CategoryORM(name=data["name"], slug=data["slug"]))
                created += 1
            else:
                category.name = data["name"]
                updated += 1
    return f"Categorías: {created} creadas, {updated} actualizadas"


def _get_or_create_tag(db: Session, name: str) -> tuple[TagORM, bool]:
    name = name.strip().lower()
    tag = db.execute(
        select(TagORM).where(func.lower(TagORM.name) == name)
    ).scalar_one_or_none()
    if tag:
        return tag, False
    tag = TagORM(name=name)
    db.add(tag)
    db.flush()
    return tag, True


def seed_tags(db: Session) -> str:
    created = 0
    with atomic(db):
        for name in TAGS:
            _, was_created = _get_or_create_tag(db, name)
            created += was_created
    return f"Tags: {created} creados, {len(TAGS) - created} ya existían"


def seed_posts(db: Session) -> str:
    created = updated = 0
    with atomic(db):
        for data in POSTS:
            author = db.execute(
                select(UserORM).where(func.lower(UserORM.email) == data.get("author_email", ADMIN_EMAIL).lower())
            ).scalar_one_or_none()
            if author is None:
                raise SeedError("No existe el autor del post. Corré primero: "
                                "python -m app.seeds users")

            category = db.execute(
                select(CategoryORM).where(CategoryORM.slug == data["category"])
            ).scalar_one_or_none()
            if category is None:
                raise SeedError(f"No existe la categoría '{data['category']}'. "
                                "Corré primero: python -m app.seeds categories")

            # La clave del upsert es el slug que sale del título.
            slug = make_slug(data["title"])
            post = db.execute(
                select(PostORM).where(PostORM.slug == slug)
            ).scalar_one_or_none()

            if post is None:
                post = PostORM(slug=ensure_unique_slug(db, data["title"]))
                db.add(post)
                created += 1
            else:
                updated += 1

            post.title = data["title"]
            post.content = data["content"].strip()
            post.repo_url = data.get("repo_url")
            post.image_url = data.get("image_url")
            post.created_at = data["created_at"]
            post.user = author
            post.category = category
            post.tags = [_get_or_create_tag(db, name)[0] for name in data["tags"]]
            db.flush()
    return f"Posts: {created} creados, {updated} actualizados"
