from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TagPublic(BaseModel):
    id: int
    name: str = Field(..., min_length=2, max_length=30)

    model_config = ConfigDict(from_attributes=True)


class TagCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=30,
                      examples=["fastapi"])

    @field_validator("name")
    @classmethod
    def normalize(cls, value: str) -> str:
        return value.strip().lower()


class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=30)

    @field_validator("name")
    @classmethod
    def normalize(cls, value: Optional[str]) -> Optional[str]:
        return value.strip().lower() if value is not None else value


class TagWithCount(TagPublic):
    uses: int


class PaginatedTags(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    search: Optional[str] = None
    items: List[TagPublic]
