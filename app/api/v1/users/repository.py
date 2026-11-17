from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import UserORM
from app.services.pagination import paginate_query


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int) -> Optional[UserORM]:
        return self.db.get(UserORM, user_id)

    def get_by_email(self, email: str) -> Optional[UserORM]:
        return self.db.execute(
            select(UserORM).where(func.lower(UserORM.email) == email.strip().lower())
        ).scalar_one_or_none()

    def search(self, search: Optional[str], page: int, per_page: int) -> dict:
        query = select(UserORM)
        if search:
            query = query.where(UserORM.email.ilike(f"%{search.strip()}%"))
        return paginate_query(self.db, UserORM, base_query=query,
                              page=page, per_page=per_page,
                              order_by="id", allowed_order={"id": UserORM.id})

    def create(self, email: str, password: str, full_name: Optional[str] = None,
               role: str = "user") -> UserORM:
        if self.get_by_email(email):
            raise ValueError("El email ya está registrado")
        user = UserORM(email=email.strip().lower(), full_name=full_name,
                       hashed_password=hash_password(password), role=role)
        self.db.add(user)
        self.db.flush()
        return user

    def authenticate(self, email: str, password: str) -> Optional[UserORM]:
        user = self.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def update(self, user: UserORM, updates: dict) -> UserORM:
        for key, value in updates.items():
            setattr(user, key, value)
        self.db.flush()
        return user

    def delete(self, user: UserORM) -> None:
        self.db.delete(user)
