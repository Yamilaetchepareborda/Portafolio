from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal["user", "editor", "admin"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128,
                          description="Contraseña en texto plano (se guarda hasheada)")
    full_name: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    """Lo que se expone de un usuario. Nunca incluye la contraseña."""
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: Role
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: Role


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class PaginatedUsers(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    items: List[UserPublic]
