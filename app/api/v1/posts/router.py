from math import ceil
from fastapi import APIRouter, Query, Depends, Path, status, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional, Union, Literal, Annotated
from app.core.db import get_db
from app.core.security import require_role
from app.models import UserORM
from .schemas import (PostPublic, PaginatedPost,
                      PostCreate, PostUpdate, PostSummary, split_tag_names)
from .repository import PostRepository
from app.services.file_storage import save_uploaded_image

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PaginatedPost)
def list_posts(
    text: Optional[str] = Query(
        default=None,
        deprecated=True,
        description="Parámetro obsoleto, usa 'query o search' en su lugar."
    ),
    query: Optional[str] = Query(
        default=None,
        description="Texto para buscar por título",
        alias="search",
        min_length=3,
        max_length=50,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜ-]+$"
    ),
    per_page: int = Query(
        10, ge=1, le=50,
        description="Número de resultados (1-50)"
    ),
    page: int = Query(
        1, ge=1,
        description="Número de página (>=1)"
    ),
    order_by: Literal["id", "title", "created_at"] = Query(
        "id", description="Campo de orden"
    ),
    direction: Literal["asc", "desc"] = Query(
        "asc", description="Dirección de orden"
    ),
    db: Session = Depends(get_db)
):
    repository = PostRepository(db)
    query = query or text

    total, items = repository.search(
        query, order_by, direction, page, per_page)

    total_pages = ceil(total/per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page, total_pages)

    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items
    )


@router.get("/by-tags", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,
        description="Una o más etiquetas. Ejemplo: ?tags=python&tags=fastapi"
    ),
    db: Session = Depends(get_db)
):
    repository = PostRepository(db)
    return repository.by_tags(tags)


@router.get("/{post_id}", response_model=Union[PostPublic, PostSummary], response_description="Post encontrado")
def get_post(post_id: int = Path(
    ...,
    ge=1,
    title="ID del post",
    description="Identificador entero del post. Debe ser mayor a 1",
    examples=[1]
), include_content: bool = Query(default=True, description="Incluir o no el contenido"), db: Session = Depends(get_db)):

    repository = PostRepository(db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)


@router.post("", response_model=PostPublic, response_description="Post creado (OK)", status_code=status.HTTP_201_CREATED)
def create_post(post: Annotated[PostCreate, Depends(PostCreate.as_form)],
                image: Optional[UploadFile] = File(None),
                db: Session = Depends(get_db),
                user: UserORM = Depends(require_role("editor"))):
    repository = PostRepository(db)
    saved = None
    try:
        if image is not None:
            saved = save_uploaded_image(image)

        image_url = saved["url"] if saved else None

        post = repository.create_post(
            title=post.title,
            content=post.content,
            user=user,
            # Fix de FormData: "python, fastapi" -> ["python", "fastapi"]
            tags=[{"name": name} for name in split_tag_names(post.tags)],
            image_url=image_url,
            repo_url=post.repo_url,
        )
        db.commit()
        db.refresh(post)
        return post
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="El título ya existe, prueba con otro")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el post")


@router.put("/{post_id}", response_model=PostPublic, response_description="Post actualizado", response_model_exclude_none=True)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db),
                user: UserORM = Depends(require_role("editor"))):

    repository = PostRepository(db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    try:
        updates = data.model_dump(exclude_unset=True)
        post = repository.update_post(post, updates)
        db.commit()
        db.refresh(post)
        return post
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="El título ya existe, prueba con otro")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al actualizar el post")


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db),
                user: UserORM = Depends(require_role("admin"))):
    repository = PostRepository(db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    try:
        repository.delete_post(post)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al eliminar el post")
