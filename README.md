# Portafolio de Yamila Etchepareborda · Mini Blog con FastAPI

Blog personal que funciona como **portafolio de desarrolladora**. Es la versión final del *Mini Blog* que construimos durante la cursada de **Desarrollo de Sistemas Web** (3° año, Tecnicatura Superior en Desarrollo de Software, Instituto IDRA).

Un mismo servidor FastAPI sirve dos cosas:

- **La API REST** (`/api/v1/...`, documentada en `/docs`): posts, tags, categorías, usuarios con JWT y roles, subida de imágenes.
- **El sitio web** (`/`, `/proyectos`, `/blog`, `/sobre-mi`), renderizado con **Jinja2** usando los mismos repositorios que la API.

> **Código base:** este proyecto parte del repositorio del profesor **César Gimenez Lascano** ([@cgldev](https://github.com/cgldev)) — [cgldev/fastapi-miniblog](https://github.com/cgldev/fastapi-miniblog), hasta el módulo *Manejo de archivos*. Sobre esa base completé los módulos 9 a 12 (Tags, Users, Categorías, Seeds y Slug) y agregué el sitio web.

## Tecnologías

- Python 3.12 · **FastAPI** · Pydantic v2
- **SQLAlchemy 2.0** (`Mapped` / `mapped_column`) · SQLite por defecto, PostgreSQL configurable (`psycopg2-binary`)
- **JWT** con PyJWT · contraseñas con **pwdlib** (Argon2)
- **Jinja2** + CSS propio (sin frameworks) · Markdown con `markdown-it-py`
- **python-slugify** para los slugs · **Typer** para el CLI de seeds
- python-dotenv para la configuración

## Estructura

```text
app/
├── main.py                  # Application Factory: create_app() + include_router
├── core/
│   ├── db.py                # engine, SessionLocal, Base, get_db
│   └── security.py          # pwdlib, JWT, get_current_user, require_role
├── models/                  # un archivo por tabla (registrados en __init__.py)
│   ├── user.py  category.py  tag.py  post.py
├── api/v1/                  # patrón Router + Repository + DTOs (schemas)
│   ├── auth/       router.py  schemas.py
│   ├── users/      router.py  repository.py  schemas.py
│   ├── posts/      router.py  repository.py  schemas.py
│   ├── tags/       router.py  repository.py  schemas.py
│   ├── categories/ router.py  repository.py  schemas.py
│   └── uploads/    router.py
├── services/
│   ├── pagination.py        # paginate_query() global
│   └── file_storage.py      # guardado de imágenes en app/media
├── utils/slugify_utils.py   # ensure_unique_slug()
├── seeds/                   # data.py, service.py (atomic + upsert), run.py (Typer)
├── content/profile.py       # datos personales y de la carrera (editables)
├── web/                     # router de páginas + render seguro de Markdown
├── templates/               # base.html y páginas (herencia de plantillas)
├── static/                  # css, js, img/avatar.png
└── media/                   # imágenes subidas (no se versiona)
```

## Instalación

Requisitos: **Python 3.10 o superior** (probado con 3.12).

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Después editá `.env`:

- `JWT_SECRET`: un secreto largo. Podés generarlo con `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
- `SEED_ADMIN_PASSWORD`: la contraseña del usuario admin.
- `SEED_DEMO_PASSWORD`: la contraseña de los usuarios de ejemplo (editor y user).

El archivo `.env`, la base `blog.db` y la carpeta `app/media/` **no se suben** al repositorio (están en `.gitignore`).

## Cargar los datos iniciales (seeds)

```bash
python -m app.seeds all
```

También se puede correr por partes: `python -m app.seeds users | categories | tags | posts`.

Los seeds son **idempotentes**: hacen un *upsert* por email o slug dentro de una transacción (`atomic(db)`), así que correrlos varias veces no duplica nada. Cargan:

| Usuario | Rol | Contraseña |
|---|---|---|
| Yamila Etchepareborda (email en `app/seeds/data.py`) | `admin` | `SEED_ADMIN_PASSWORD` |
| `editor@example.com` | `editor` | `SEED_DEMO_PASSWORD` |
| `usuario@example.com` | `user` | `SEED_DEMO_PASSWORD` |

Además: 5 categorías, 30 tags, 8 posts de proyectos y 4 apuntes de cursada.

## Levantar el servidor

```bash
fastapi dev app/main.py
```

- Sitio: <http://127.0.0.1:8000>
- API interactiva (Swagger): <http://127.0.0.1:8000/docs>

Para probar endpoints protegidos en Swagger: botón **Authorize** → en *username* va el **email** y en *password* la contraseña.

### PostgreSQL (opcional)

Cambiá `DATABASE_URL` en `.env`, por ejemplo `postgresql+psycopg2://usuario:clave@localhost:5432/portafolio`, y corré los seeds de nuevo. Las tablas se crean solas al iniciar.

## Páginas del sitio

| Ruta | Contenido |
|---|---|
| `/` | Foto, presentación, links, proyectos destacados, últimos posts y contacto (`/#contacto`) |
| `/proyectos` | Posts de la categoría *Proyectos* con tecnologías y botón "Ver en GitHub" |
| `/blog` | Listado paginado con búsqueda por título y filtros por categoría y tag |
| `/blog/{slug}` | Detalle del post (Markdown renderizado de forma segura) |
| `/sobre-mi` | Formación, materias aprobadas por año (sin notas), proyecto final y stack |
| cualquier otra | Página 404 propia (la API sigue respondiendo 404 en JSON) |

## Endpoints de la API

Todos bajo `/api/v1`. Roles: `user` (0) < `editor` (1) < `admin` (2); cada nivel incluye al anterior.

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `POST` | `/auth/register` | público | Registro (siempre con rol `user`) → 201 |
| `POST` | `/auth/login` | público | Login con formulario OAuth2 (Swagger *Authorize*) |
| `POST` | `/auth/login-json` | público | Login con JSON `{email, password}` |
| `GET` | `/auth/me` | logueado | Perfil del usuario actual |
| `GET` | `/posts` | público | Listado paginado; `search`, `order_by`, `direction`, `category`, `tag` |
| `GET` | `/posts/by-tags` | público | Posts que tienen alguno de los tags |
| `GET` | `/posts/{id}` | público | Post por id (`include_content`) |
| `GET` | `/posts/post/{slug}` | público | Post por slug (`include_content` → `PostPublic` o `PostSummary`) |
| `POST` | `/posts` | editor | Crear post (form-data: título, contenido, tags, `category_id`, `repo_url`, imagen) → 201 |
| `PUT` | `/posts/{id}` | editor | Editar post |
| `DELETE` | `/posts/{id}` | admin | Borrar post → 204 |
| `GET` | `/tags` | público | Listado paginado con búsqueda |
| `GET` | `/tags/most-popular` | público | Tag más usado (`TagWithCount`) |
| `GET` | `/tags/{id}` | público | Tag por id |
| `POST` | `/tags` | editor | Crear tag → 201 (409 si existe) |
| `PUT` | `/tags/{id}` | editor | Editar tag |
| `DELETE` | `/tags/{id}` | admin | Borrar tag → 204 |
| `GET` | `/categories` | público | Listado de categorías |
| `GET` | `/categories/{id}` · `/categories/slug/{slug}` | público | Categoría por id o slug |
| `POST` | `/categories` | editor | Crear → 201 (400 "Slug en uso") |
| `PUT` | `/categories/{id}` | editor | Editar |
| `DELETE` | `/categories/{id}` | admin | Borrar → 204 (los posts quedan con `category_id` nulo) |
| `GET` | `/users` | admin | Listado paginado de usuarios |
| `GET` | `/users/{id}` | admin | Usuario por id |
| `PATCH` | `/users/{id}` | admin | Editar nombre o activar/desactivar |
| `PATCH` | `/users/{id}/role` | admin | Cambiar rol |
| `DELETE` | `/users/{id}` | admin | Borrar usuario → 204 (sus posts quedan sin autor) |
| `POST` | `/upload/bytes` · `/upload/file` · `/upload/save` | público | Ejemplos de subida de archivos (módulo del profe) |

Códigos usados: 201 al crear, 204 al borrar, 400/409 por duplicados, 401 sin token o token inválido, 403 sin permisos, 404 si no existe y 422 por validación.

## Decisiones de diseño

- **`Author` → `User`:** se eliminó `AuthorORM`. Cada post guarda `user_id` (FK a `users`, `ON DELETE SET NULL`), así el autor es el usuario real que lo creó y no hay datos duplicados.
- **`full_name` en usuarios:** además de lo pedido, `users` tiene un nombre visible para mostrar como autor sin exponer el email en el sitio.
- **`repo_url` en posts:** columna opcional para el botón "Ver en GitHub" de cada proyecto.
- **Slug estable:** se genera al crear el post y no cambia al editar el título, para no romper links.
- **SQLite con claves foráneas:** se activa `PRAGMA foreign_keys=ON` para que `ON DELETE SET NULL` funcione igual que en PostgreSQL.
- **Markdown seguro:** `markdown-it-py` con `html=False` escapa cualquier HTML y bloquea links `javascript:`, por eso no hace falta `bleach`.
- **Sin migraciones:** como en clase, las tablas se crean con `create_all()` al iniciar. Si cambia un modelo, borrá `blog.db` y corré los seeds de nuevo.

## Créditos

- Código base: **César Gimenez Lascano** ([@cgldev](https://github.com/cgldev)) — [fastapi-miniblog](https://github.com/cgldev/fastapi-miniblog).
- Módulos 9 a 12 y sitio web: **Yamila Etchepareborda** ([@Yamilaetchepareborda](https://github.com/Yamilaetchepareborda)).
