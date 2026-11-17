import typer

from app.core.db import Base, SessionLocal, engine
from app.seeds import service

app = typer.Typer(help="Carga los datos iniciales del portafolio (idempotente).",
                  no_args_is_help=True)


def _run(*steps) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for step in steps:
            summary = step(db)
            typer.echo(f"  {summary}")
    except service.SeedError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    finally:
        db.close()
    typer.secho("Listo.", fg=typer.colors.GREEN)


@app.command()
def users():
    """Usuarios (admin, editor y user de ejemplo)."""
    _run(service.seed_users)


@app.command()
def categories():
    """Categorías del blog."""
    _run(service.seed_categories)


@app.command()
def tags():
    """Tags de tecnologías."""
    _run(service.seed_tags)


@app.command()
def posts():
    """Posts (requiere usuarios y categorías cargados)."""
    _run(service.seed_posts)


@app.command(name="all")
def all_():
    """Todo, en orden: usuarios, categorías, tags y posts."""
    _run(service.seed_users, service.seed_categories,
         service.seed_tags, service.seed_posts)


if __name__ == "__main__":
    app()
