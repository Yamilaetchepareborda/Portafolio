"""Páginas del portafolio, renderizadas con Jinja2.

Las vistas usan los mismos repositorios que la API (no la llaman por HTTP),
así los filtros, la paginación y las reglas son exactamente los mismos.
"""
from datetime import datetime
from math import ceil
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.v1.categories.repository import CategoryRepository
from app.api.v1.posts.repository import PostRepository
from app.api.v1.tags.repository import TagRepository
from app.content import profile as content
from app.core.db import get_db
from app.models import CategoryORM, PostORM
from app.web.markdown import excerpt, render_markdown

router = APIRouter(include_in_schema=False)

templates = Jinja2Templates(directory="app/templates")

MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def date_es(value: Optional[datetime], short: bool = False) -> str:
    if not value:
        return ""
    month = MONTHS[value.month - 1]
    if short:
        return f"{month[:3]} {value.year}"
    return f"{value.day} de {month} de {value.year}"


def cover_hue(post_id: int) -> int:
    """Color estable por post para las portadas generadas sin imagen."""
    return (post_id * 47 + 250) % 360


templates.env.filters["markdown"] = render_markdown
templates.env.filters["excerpt"] = excerpt
templates.env.filters["date_es"] = date_es
templates.env.filters["hue"] = cover_hue
templates.env.globals.update(
    profile=content.PROFILE,
    projects_slug=content.PROJECTS_CATEGORY_SLUG,
    current_year=lambda: datetime.now().year,
)

BLOG_PER_PAGE = 6


def _to_int(value: Optional[str], default: int = 1) -> int:
    try:
        return max(1, int(value)) if value else default
    except ValueError:
        return default


def _clean(value: Optional[str], max_length: int) -> Optional[str]:
    if not value:
        return None
    value = value.strip()[:max_length]
    return value or None


def _projects(db: Session, limit: int = 50):
    _, items = PostRepository(db).search(
        None, "created_at", "desc", 1, limit,
        category=content.PROJECTS_CATEGORY_SLUG)
    return items


@router.get("/", name="home")
def home(request: Request, db: Session = Depends(get_db)):
    repository = PostRepository(db)

    # Últimos posts del blog (los proyectos tienen su propia sección).
    query = repository.filtered_query()
    query = query.where(~PostORM.category.has(
        CategoryORM.slug == content.PROJECTS_CATEGORY_SLUG))
    latest = db.execute(
        query.order_by(PostORM.created_at.desc()).limit(3)).scalars().all()

    by_slug = {p.slug: p for p in _projects(db)}
    featured = [by_slug[s] for s in content.FEATURED_PROJECT_SLUGS if s in by_slug]

    return templates.TemplateResponse(request, "index.html", {
        "active": "home", "latest": latest, "featured": featured,
    })


@router.get("/proyectos", name="projects")
def projects(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "projects.html", {
        "active": "projects", "projects": _projects(db),
    })


@router.get("/blog", name="blog")
def blog(request: Request,
         q: Optional[str] = None,
         categoria: Optional[str] = None,
         tag: Optional[str] = None,
         pagina: Optional[str] = None,
         db: Session = Depends(get_db)):
    q = _clean(q, 50)
    categoria = _clean(categoria, 60)
    tag = _clean(tag, 30)
    page = _to_int(pagina)

    # Paginación global (paginate_query) a través del repositorio.
    total, posts = PostRepository(db).search(
        q, "created_at", "desc", page, BLOG_PER_PAGE, tag=tag, category=categoria)
    total_pages = ceil(total / BLOG_PER_PAGE) if total else 0
    page = min(page, total_pages) if total_pages else 1

    categories = [c for c in CategoryRepository(db).with_counts() if c["uses"]]
    active_category = next((c for c in categories if c["slug"] == categoria), None)

    current = {"q": q, "categoria": categoria, "tag": tag}

    def blog_url(**changes) -> str:
        """URL del blog conservando los filtros actuales. Cambiar un filtro
        vuelve a la página 1."""
        params = {**current, "pagina": None, **changes}
        if params["pagina"] == 1:
            params["pagina"] = None
        query = urlencode({k: v for k, v in params.items() if v})
        return f"/blog?{query}" if query else "/blog"

    return templates.TemplateResponse(request, "blog.html", {
        "active": "blog", "blog_url": blog_url,
        "posts": posts, "total": total,
        "page": page, "total_pages": total_pages,
        "q": q or "", "categoria": categoria, "tag": tag,
        "active_category": active_category,
        "categories": categories,
        "tags": TagRepository(db).with_counts(),
    })


@router.get("/blog/{slug}", name="post_detail")
def post_detail(request: Request, slug: str, db: Session = Depends(get_db)):
    repository = PostRepository(db)
    post = repository.get_by_slug(slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    related = []
    if post.category:
        _, same_category = repository.search(
            None, "created_at", "desc", 1, 4, category=post.category.slug)
        related = [p for p in same_category if p.id != post.id][:3]

    return templates.TemplateResponse(request, "post_detail.html", {
        "active": "projects" if post.category and
        post.category.slug == content.PROJECTS_CATEGORY_SLUG else "blog",
        "post": post, "related": related,
    })


@router.get("/sobre-mi", name="about")
def about(request: Request):
    return templates.TemplateResponse(request, "about.html", {
        "active": "about",
        "education": content.EDUCATION,
        "subjects": content.SUBJECTS,
        "final_project": content.FINAL_PROJECT,
        "skills": content.SKILLS,
    })


def render_not_found(request: Request):
    return templates.TemplateResponse(request, "404.html", {"active": None},
                                      status_code=404)
