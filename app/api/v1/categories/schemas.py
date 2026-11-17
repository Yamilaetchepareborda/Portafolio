from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=60, examples=["FastAPI"])
    slug: str = Field(..., min_length=2, max_length=60, pattern=SLUG_PATTERN,
                      examples=["fastapi"],
                      description="Minúsculas, números y guiones")


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=60)
    slug: Optional[str] = Field(None, min_length=2, max_length=60,
                                pattern=SLUG_PATTERN)


class CategoryPublic(BaseModel):
    id: int
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)
