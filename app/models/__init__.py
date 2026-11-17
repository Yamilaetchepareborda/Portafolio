# Todos los modelos se registran acá para que Base.metadata los conozca
# antes de create_all() y para que las relaciones por nombre ("PostORM")
# se puedan resolver sin imports circulares.
from .user import UserORM
from .category import CategoryORM
from .tag import TagORM
from .post import PostORM, post_tags

__all__ = ["UserORM", "CategoryORM", "TagORM", "PostORM", "post_tags"]
