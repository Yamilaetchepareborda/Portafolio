import os
from fastapi import FastAPI
from app.core.db import Base, engine
from dotenv import load_dotenv
from app.api.v1.posts.router import router as post_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.categories.router import router as category_router
from app.api.v1.tags.router import router as tag_router
from app.api.v1.users.router import router as user_router
from app.api.v1.uploads.router import router as upload_router
from fastapi.staticfiles import StaticFiles

load_dotenv()

MEDIA_DIR = "app/media"
API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog")
    Base.metadata.create_all(bind=engine)  # dev

    app.include_router(auth_router, prefix=API_PREFIX)
    app.include_router(post_router, prefix=API_PREFIX)
    app.include_router(category_router, prefix=API_PREFIX)
    app.include_router(tag_router, prefix=API_PREFIX)
    app.include_router(user_router, prefix=API_PREFIX)
    app.include_router(upload_router, prefix=API_PREFIX)

    os.makedirs(MEDIA_DIR, exist_ok=True)  # Ensure media directory exists
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

    return app


app = create_app()
