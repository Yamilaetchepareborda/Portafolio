"""Datos iniciales del portafolio.

Las contraseñas NO están acá: cada usuario indica de qué variable del .env
se lee (SEED_ADMIN_PASSWORD / SEED_DEMO_PASSWORD).
"""
from datetime import datetime

GITHUB = "https://github.com/Yamilaetchepareborda"

ADMIN_EMAIL = "yamilaetchepareborda.ye@gmail.com"

USERS = [
    {
        "email": ADMIN_EMAIL,
        "full_name": "Yamila Etchepareborda",
        "role": "admin",
        "password_env": "SEED_ADMIN_PASSWORD",
    },
    {
        "email": "editor@example.com",
        "full_name": "Editora de ejemplo",
        "role": "editor",
        "password_env": "SEED_DEMO_PASSWORD",
    },
    {
        "email": "usuario@example.com",
        "full_name": "Usuario de ejemplo",
        "role": "user",
        "password_env": "SEED_DEMO_PASSWORD",
    },
]

CATEGORIES = [
    {"name": "Proyectos", "slug": "proyectos"},
    {"name": "Apuntes de cursada", "slug": "apuntes-de-cursada"},
    {"name": "Python", "slug": "python"},
    {"name": "FastAPI", "slug": "fastapi"},
    {"name": "SQLAlchemy", "slug": "sqlalchemy"},
]

TAGS = [
    # Los pedidos para el portafolio
    "backend", "frontend", "apis", "python", "fastapi", "sqlalchemy", "react",
    "typescript", "nodejs", "nestjs", "angular", "nextjs", "java", "csharp",
    "mysql", "docker", "jwt", "design-patterns", "javascript",
    # Tecnologías puntuales que aparecen en los proyectos
    "typeorm", "chartjs", "tailwind", "rxjs", "dotnet", "supabase",
    "postgresql", "pwa", "jinja2", "n8n", "ia",
]

POSTS = [
    # ------------------------------------------------------------ Proyectos
    {
        "title": "Del Mar a la Roja Montaña",
        "category": "proyectos",
        "repo_url": f"{GITHUB}/del-mar-a-la-roja-montana",
        "created_at": datetime(2026, 9, 24, 10, 0),
        "tags": ["nestjs", "typeorm", "mysql", "react", "typescript", "jwt",
                 "docker", "backend", "frontend", "apis"],
        "content": """
Proyecto **full-stack en equipo**: una API REST con **NestJS + TypeORM + MySQL** y un
frontend de administración en **React**, todo dockerizado con **Docker Compose**.

## Qué hace

- API REST organizada en módulos de NestJS, con entidades y relaciones en TypeORM.
- Autenticación con **JWT**, usando *access token* de vida corta y *refresh token*
  para renovar la sesión sin volver a pedir la contraseña.
- Panel de administración en React + TypeScript que consume la API.
- `docker compose up` levanta la base, el backend y el frontend con un solo comando.

## Lo que aprendí

Trabajar en equipo sobre el mismo repositorio, separar bien las capas
(controladores, servicios y repositorios) y pensar la seguridad desde el
principio: dónde guardar cada token y cuándo invalidarlo.
""",
    },
    {
        "title": "Gráficos de Control",
        "category": "proyectos",
        "repo_url": f"{GITHUB}/GraficosDeControl",
        "created_at": datetime(2025, 9, 17, 10, 0),
        "tags": ["javascript", "chartjs", "apis", "frontend"],
        "content": """
**Gráfico de control estadístico de procesos** hecho en JavaScript *vanilla* con
**Chart.js**.

## Qué hace

- Consume los datos de una **API REST** con `fetch`.
- Calcula la media y los límites de control superior e inferior.
- Dibuja el gráfico y **marca los puntos fuera de control** y los patrones
  sospechosos (por ejemplo, rachas del mismo lado de la media).

## Lo que aprendí

Fue el cruce entre *Estadística y probabilidades* y programación: pasar de la
fórmula en el cuaderno a un gráfico interactivo, sin frameworks, entendiendo bien
qué hace el navegador.
""",
    },
    {
        "title": "Angular Pets CRUD",
        "category": "proyectos",
        "repo_url": f"{GITHUB}/angular-pets-crud",
        "created_at": datetime(2025, 11, 13, 10, 0),
        "tags": ["angular", "typescript", "rxjs", "frontend", "apis"],
        "content": """
**CRUD de registro de mascotas para una veterinaria**, hecho con **Angular 20**.

## Qué hace

- Alta, listado, edición y baja de mascotas consumiendo una **API REST**.
- *Standalone components* (sin `NgModule`), `HttpClient` y **RxJS** para manejar
  las respuestas asíncronas.
- Renderizado del lado del servidor (**SSR**) para que la primera carga sea rápida.

## Lo que aprendí

La forma de pensar de Angular: componentes, servicios inyectables y
observables. Comparado con React, todo viene más armado y tipado de punta a punta.
""",
    },
    {
        "title": "DeliveryGo",
        "category": "proyectos",
        "repo_url": f"{GITHUB}/DeliveryGo",
        "created_at": datetime(2025, 9, 23, 10, 0),
        "tags": ["csharp", "dotnet", "design-patterns", "backend"],
        "content": """
**Mini e-commerce de consola en C#** que aplica **9 patrones de diseño GoF**.

## Patrones aplicados

| Patrón | Para qué se usa |
|---|---|
| Command | Acciones del carrito con *undo/redo* |
| Strategy | Formas de envío y de pago intercambiables |
| Factory | Creación de productos y pedidos |
| Adapter | Integrar un servicio externo con otra interfaz |
| Decorator | Agregar extras a un pedido sin tocar la clase base |
| Singleton | Configuración global de la tienda |
| Builder | Armar pedidos complejos paso a paso |
| Observer | Avisar cambios de estado del pedido |
| Facade | Una entrada simple para todo el flujo de compra |

## Lo que aprendí

Que los patrones no son recetas para meter en todos lados: cada uno resuelve
un problema concreto. También a aplicar **POO** y principios **SOLID** en .NET.
""",
    },
    {
        "title": "Gestor de Gimnasio en Java",
        "category": "proyectos",
        "repo_url": f"{GITHUB}/gestor-gimnasio-java",
        "created_at": datetime(2026, 1, 19, 10, 0),
        "tags": ["java", "mysql", "design-patterns", "backend"],
        "content": """
**App de escritorio para gestionar un gimnasio**, hecha en **Java Swing**.
Proyecto académico en equipo.

## Arquitectura

- **MVC**: las vistas de Swing no conocen la base; hablan con los controladores.
- **DAO**: cada entidad tiene su objeto de acceso a datos con **JDBC** sobre **MySQL**.
- Gestión de socios, planes y pagos.

## Lo que aprendí

Separar responsabilidades en una app de escritorio y escribir SQL a mano con
JDBC, entendiendo qué hace un ORM por nosotros cuando después lo usamos.
""",
    },
    {
        "title": "Next.js Pokédex",
        "category": "proyectos",
        "repo_url": f"{GITHUB}/nextjs-pokedex",
        "created_at": datetime(2025, 10, 29, 10, 0),
        "tags": ["nextjs", "react", "typescript", "tailwind", "frontend", "apis"],
        "content": """
**Pokédex de la primera generación** hecha con **Next.js 16** (App Router).

## Qué hace

- Lista y detalle de los 151 Pokémon usando la **PokéAPI**.
- **React Server Components**: los datos se piden en el servidor y llega HTML listo.
- Estilos con **Tailwind CSS** y tipado completo con **TypeScript**.

## Lo que aprendí

La diferencia entre componentes de servidor y de cliente, y cómo Next.js
cachea las respuestas de una API externa.
""",
    },
    {
        "title": "Este portafolio: Mini Blog con FastAPI",
        "category": "proyectos",
        "repo_url": None,  # se completa cuando el repo esté publicado
        "created_at": datetime(2026, 11, 17, 10, 0),
        "tags": ["python", "fastapi", "sqlalchemy", "jwt", "jinja2", "backend", "apis"],
        "content": """
El sitio que estás viendo. Es la versión final del **Mini Blog** que armamos durante
la cursada de **Desarrollo de Sistemas Web** (3° año).

## Cómo está hecho

- **FastAPI** con *Application Factory* y el patrón **Router + Repository + DTOs** (Pydantic v2).
- **SQLAlchemy 2.0** con SQLite en desarrollo y PostgreSQL configurable por `.env`.
- **JWT** con usuarios reales, contraseñas con Argon2 y roles `user` / `editor` / `admin`.
- Categorías, tags *many-to-many*, slugs únicos, subida de imágenes y seeds idempotentes.
- Estas páginas se renderizan con **Jinja2** desde el mismo FastAPI, usando los mismos
  repositorios que la API. La API completa sigue en `/docs`.

El código base es del profesor César Gimenez Lascano
([@cgldev](https://github.com/cgldev)); yo completé los módulos de tags, usuarios,
categorías, seeds y slugs, y le sumé el sitio.
""",
    },
    {
        "title": "IM Fitness: proyecto final (Grupo 8)",
        "category": "proyectos",
        "repo_url": None,  # repositorio privado del equipo
        "created_at": datetime(2026, 10, 20, 10, 0),
        "tags": ["react", "typescript", "supabase", "postgresql", "pwa", "ia",
                 "n8n", "frontend", "backend"],
        "content": """
**Sistema de gestión de gimnasio** como **PWA** en **React + TypeScript + Vite**, con
**Supabase** como backend. Es nuestro proyecto final, del **Grupo 8**.

## Qué gestiona

- Socios, fichas médicas, planes de entrenamiento, pagos y membresías.
- Accesos por **molinete**.
- Funciona **offline en recepción** (IndexedDB) y sincroniza al volver la conexión.

## Backend y seguridad

- **PostgreSQL con Row Level Security**: los permisos se validan en la base,
  no solo en la interfaz.
- Autenticación por roles: **admin**, **profesor**, **alumno** y **tótem**.
- Almacenamiento de archivos en Supabase Storage.

## Inteligencia artificial

Dos agentes con contextos separados:

1. **Entrenador Virtual**, para alumnos y para el tótem (también por WhatsApp,
   orquestado con **n8n**).
2. **Asistente de Gestión y Copiloto de Rutinas**, para el staff.

## Cómo trabajamos

Metodología ágil en **Jira** y planificación con una **red PERT**. Equipo:
Emmanuel Espinosa, Iñaki Velo, Lorenzo Colombo y yo.
""",
    },
    # --------------------------------------------------- Apuntes de cursada
    {
        "title": "De la API en memoria a SQLAlchemy",
        "category": "apuntes-de-cursada",
        "created_at": datetime(2026, 9, 2, 10, 0),
        "tags": ["python", "fastapi", "sqlalchemy", "backend"],
        "content": """
Al principio del Mini Blog los posts vivían en una **lista de Python**. Funcionaba,
pero cada vez que reiniciaba el servidor se perdía todo.

## El cambio

Pasamos a **SQLAlchemy 2.0** con modelos tipados:

```python
class PostORM(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
```

- `Mapped` y `mapped_column` hacen que el editor entienda los tipos.
- `TYPE_CHECKING` evita los *imports* circulares entre modelos que se relacionan.
- Una sesión por request con `Depends(get_db)`, que se cierra sola al terminar.

## Lo que me llevo

Lo más útil fue entender que la **misma URL de conexión** sirve para SQLite en mi
máquina y para PostgreSQL en producción: solo cambia el `.env`.
""",
    },
    {
        "title": "Router + Repository: cada cosa en su lugar",
        "category": "apuntes-de-cursada",
        "created_at": datetime(2026, 9, 23, 10, 0),
        "tags": ["python", "fastapi", "design-patterns", "backend", "apis"],
        "content": """
En clase organizamos cada dominio en tres archivos: `router.py`, `repository.py` y
`schemas.py`. Al principio me parecía demasiado para un blog. Ahora no lo cambiaría.

## Qué hace cada uno

- **Router**: recibe la request, valida con Pydantic y decide el código HTTP
  (201 al crear, 204 al borrar, 404, 409...).
- **Repository**: es el único que habla con SQLAlchemy.
- **Schemas (DTOs)**: definen qué entra y qué sale. `UserPublic`, por ejemplo,
  nunca expone la contraseña.

## La prueba de fuego

Cuando sumé las páginas web de este portafolio con Jinja2, **no tuve que escribir
consultas nuevas**: las vistas usan los mismos repositorios que la API. Y la
paginación quedó en un solo lugar (`paginate_query`) para posts, tags y usuarios.
""",
    },
    {
        "title": "Seguridad con JWT y roles",
        "category": "apuntes-de-cursada",
        "created_at": datetime(2026, 10, 14, 10, 0),
        "tags": ["jwt", "fastapi", "python", "backend"],
        "content": """
Empezamos con usuarios falsos en un diccionario (`FAKE_USERS`). El último paso fue
pasar a una **tabla real de usuarios**.

## Contraseñas

Nunca se guardan en texto plano. Uso **pwdlib** con **Argon2**:

```python
password_hash = PasswordHash.recommended()
hashed = password_hash.hash("mi-clave")
```

## El token

El JWT lleva solo lo necesario: `sub` (el id del usuario) y `exp` (vencimiento),
firmado con un secreto que vive en el `.env`, nunca en el código.

## Roles

Tres niveles, y cada uno incluye al anterior:

| Rol | Puede |
|---|---|
| `user` | Leer contenido y ver su perfil |
| `editor` | Además, crear y editar posts |
| `admin` | Todo, incluido borrar usuarios y cambiar roles |

Con una dependencia `require_role("editor")` cada endpoint declara qué nivel
necesita, y FastAPI responde **401** si no hay token y **403** si el rol no alcanza.
""",
    },
    {
        "title": "Seeds idempotentes y slugs",
        "category": "apuntes-de-cursada",
        "created_at": datetime(2026, 11, 4, 10, 0),
        "tags": ["python", "sqlalchemy", "backend"],
        "content": """
Dos cosas chicas que hacen que el proyecto se sienta profesional.

## Seeds

Con **Typer** armé un comando para cargar los datos iniciales:

```bash
python -m app.seeds all
```

La clave es que sea **idempotente**: si lo corro dos veces no duplica nada. Para eso
hago un *upsert lógico* (si existe por email o slug, lo actualizo; si no, lo creo)
dentro de un `atomic(db)`, un *context manager* que hace commit al final o rollback
si algo falla.

## Slugs

En vez de `/blog/12`, las URLs son `/blog/seeds-idempotentes-y-slugs`. Se generan
con **python-slugify** a partir del título, y si el slug ya existe se prueba
`-2`, `-3`... hasta encontrar uno libre.
""",
    },
]
