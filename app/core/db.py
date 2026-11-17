import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
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
