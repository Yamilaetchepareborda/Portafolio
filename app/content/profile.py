"""Datos personales y de la carrera que muestra el sitio.

Editá este archivo para actualizar el portafolio: las plantillas no tienen
datos escritos a mano.
"""

PROFILE = {
    "full_name": "Yamila Soledad Etchepareborda",
    "short_name": "Yamila Etchepareborda",
    "initials": "YE",
    "title": "Desarrolladora Full-Stack Jr",
    "stack_line": "React · Node.js · TypeScript · Python",
    "open_to": "Abierta a trabajo remoto",
    "location": "Mar del Plata, Argentina",
    "avatar": "img/avatar.png",
    "bio": (
        "Estudio el 3° año de la Tecnicatura Superior en Desarrollo de Software. "
        "Me gusta construir aplicaciones completas: desde el modelo de datos y la "
        "API hasta la interfaz que usa la gente. Trabajo en equipo con metodologías "
        "ágiles y me interesa escribir código claro, seguro y fácil de mantener."
    ),
    "github": "https://github.com/Yamilaetchepareborda",
    "github_user": "Yamilaetchepareborda",
    "linkedin": "https://www.linkedin.com/in/yamilaetchepareborda/",
    "linkedin_user": "yamilaetchepareborda",
}

EDUCATION = {
    "degree": "Tecnicatura Superior en Desarrollo de Software",
    "resolution": "Res. 5847/19",
    "institution": "Instituto IDRA",
    "status": "Cursando 3° año (2026)",
}

# Materias aprobadas por año (sin notas).
SUBJECTS = [
    {
        "year": "1° año",
        "period": "2024",
        "in_progress": False,
        "subjects": [
            "Introducción a la programación",
            "Administración y gestión de la base de datos",
            "Análisis matemático",
            "Introducción a las redes de datos",
            "Laboratorio de Hardware",
            "Sistemas digitales",
            "Sistemas operativos",
            "Prácticas profesionales I",
        ],
    },
    {
        "year": "2° año",
        "period": "2025",
        "in_progress": False,
        "subjects": [
            "Programación",
            "Desarrollo de sistemas orientado a objetos",
            "Desarrollo de aplicativos móviles",
            "Diseño Web",
            "Álgebra y lógica",
            "Estadística y probabilidades",
            "Inglés I",
            "Práctica profesional II",
        ],
    },
    {
        "year": "3° año",
        "period": "2026",
        "in_progress": True,
        "subjects": [
            "Desarrollo de Sistemas Web",
            "Ingeniería de Software",
            "Metodología de pruebas de sistemas",
            "Inglés II",
        ],
    },
]

FINAL_PROJECT = {
    "name": "IM Fitness",
    "team": "Grupo 8",
    "summary": (
        "Sistema de gestión de gimnasio como PWA en React + TypeScript con Supabase: "
        "socios, fichas médicas, planes, pagos, accesos por molinete, modo offline "
        "y dos agentes de IA."
    ),
    "post_slug": "im-fitness-proyecto-final-grupo-8",
}

# Tecnologías que se muestran en "Sobre mí", agrupadas.
SKILLS = [
    {"group": "Frontend", "items": ["React", "TypeScript", "Next.js", "Angular",
                                    "JavaScript", "Tailwind", "HTML y CSS"]},
    {"group": "Backend", "items": ["Node.js", "NestJS", "Python", "FastAPI",
                                   "Java", "C# / .NET"]},
    {"group": "Datos", "items": ["PostgreSQL", "MySQL", "SQLAlchemy", "TypeORM",
                                 "Supabase"]},
    {"group": "Herramientas", "items": ["Git y GitHub", "Docker", "JWT",
                                        "Jira", "n8n"]},
]

# Proyectos que aparecen en Inicio (por slug del post), en este orden.
FEATURED_PROJECT_SLUGS = [
    "im-fitness-proyecto-final-grupo-8",
    "del-mar-a-la-roja-montana",
    "deliverygo",
]

PROJECTS_CATEGORY_SLUG = "proyectos"
