import os
from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv

from app.core.db import Base, engine
from app.api.v1.posts.router import router as post_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.categories.router import router as category_router
from app.api.v1.tags.router import router as tag_router
from app.api.v1.users.router import router as user_router
from app.api.v1.uploads.router import router as upload_router
from app.web.router import router as web_router, render_not_found

load_dotenv()

MEDIA_DIR = "app/media"
STATIC_DIR = "app/static"
API_PREFIX = "/api/v1"
# Rutas que siempre responden JSON (la API y los archivos).
JSON_PATHS = (API_PREFIX, "/docs", "/redoc", "/openapi.json", "/media", "/static")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Portafolio de Yamila Etchepareborda · Mini Blog API",
        description="API del blog-portafolio (FastAPI + SQLAlchemy + JWT). "
                    "Para probar los endpoints protegidos usá **Authorize** "
                    "con el email y la contraseña de un usuario.",
        version="1.0.0",
    )
    Base.metadata.create_all(bind=engine)  # dev

    # API REST
    app.include_router(auth_router, prefix=API_PREFIX)
    app.include_router(post_router, prefix=API_PREFIX)
    app.include_router(category_router, prefix=API_PREFIX)
    app.include_router(tag_router, prefix=API_PREFIX)
    app.include_router(user_router, prefix=API_PREFIX)
    app.include_router(upload_router, prefix=API_PREFIX)

    # Sitio web (Jinja2), sin prefijo /api
    app.include_router(web_router)

    os.makedirs(MEDIA_DIR, exist_ok=True)  # Ensure media directory exists
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.exception_handler(StarletteHTTPException)
    async def not_found_page(request: Request, exc: StarletteHTTPException):
        # En las páginas del sitio, un 404 muestra la página linda;
        # la API sigue devolviendo JSON como siempre.
        if exc.status_code == 404 and not request.url.path.startswith(JSON_PATHS):
            return render_not_found(request)
        return await http_exception_handler(request, exc)

    return app


app = create_app()
