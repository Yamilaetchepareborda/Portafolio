from datetime import datetime
from typing import Optional, List, Literal, Annotated
from pydantic import BaseModel, Field, field_validator, ConfigDict
from fastapi import Form

from app.api.v1.categories.schemas import CategoryPublic
from app.api.v1.users.schemas import UserPublic


def split_tag_names(tags) -> List[str]:
    """Fix del bug de tags con FormData.

    Swagger (y cualquier formulario) puede mandar los tags como un único
    string "python, fastapi". Se separa por comas, se normaliza con
    strip().lower() y se eliminan duplicados conservando el orden.
    """
    names: List[str] = []
    for tag in tags or []:
        raw = tag.name if hasattr(tag, "name") else str(tag)
        for part in raw.split(","):
            name = part.strip().lower()
            if name and name not in names:
                names.append(name)
    return names


class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30,
                      description="Nombre de la etiqueta")

    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    user: Optional[UserPublic] = None
    category: Optional[CategoryPublic] = None
    image_url: Optional[str] = None
    repo_url: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titulo del post (mínimo 3 caracteres, máximo 100)",
        examples=["Mi primer post con FastAPI"]
    )
    content: Optional[str] = Field(
        default="Contenido no disponible",
        min_length=10,
        description="Contenido del post (mínimo 10 caracteres). Acepta Markdown.",
        examples=["Este es un contenido válido porque tiene 10 caracteres o más"]
    )
    tags: List[Tag] = Field(default_factory=list)  # []
    repo_url: Optional[str] = Field(None, max_length=300)
    category_id: Optional[int] = Field(None, ge=1)

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("El título no puede contener la palabra: 'spam'")
        return value

    @classmethod
    def as_form(
        cls,
        title: Annotated[str, Form(min_length=3)],
        content: Annotated[str, Form(min_length=10)],
        tags: Annotated[Optional[List[str]], Form(
            description="Uno o varios tags. También acepta \"python, fastapi\"")] = None,
        repo_url: Annotated[Optional[str], Form(max_length=300)] = None,
        category_id: Annotated[Optional[int], Form(
            ge=1, description="ID de la categoría (opcional)")] = None,
    ):
        # Con FormData los tags pueden llegar como "python, fastapi":
        # se separan antes de validar cada uno.
        tag_objs = [Tag(name=t) for t in split_tag_names(tags)]
        return cls(title=title, content=content, tags=tag_objs,
                   repo_url=repo_url or None, category_id=category_id)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = Field(None, min_length=10)
    repo_url: Optional[str] = Field(None, max_length=300)
    category_id: Optional[int] = Field(None, ge=1)


class PostPublic(PostBase):
    id: int
    slug: str

    model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
    id: int
    title: str
    slug: str

    model_config = ConfigDict(from_attributes=True)


class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title", "created_at"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: List[PostPublic]
