import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

# Se carga el .env acá porque este módulo se importa antes de que main.py
# llame a load_dotenv(): si no, DATABASE_URL siempre tomaría el default.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=SQL_ECHO, future=True, **engine_kwargs)

if DATABASE_URL.startswith("sqlite"):
    # SQLite no aplica las claves foráneas (ni ON DELETE SET NULL / CASCADE)
    # salvo que se active en cada conexión. PostgreSQL ya lo hace siempre.
    @event.listens_for(engine, "connect")
    def _enable_sqlite_fk(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
