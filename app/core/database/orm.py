from collections.abc import Generator
from importlib import import_module
import sqlite3

from sqlalchemy import Engine, create_engine, event, inspect
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def create_sqlite_engine(database_url: str) -> Engine:
    """Create a SQLite engine with foreign-key enforcement enabled."""
    db_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(db_engine, "connect")
    def enable_foreign_keys(
        connection: sqlite3.Connection,
        _record: object,
    ) -> None:
        cursor = connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

    return db_engine


engine = create_sqlite_engine(settings.database_url)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def _migrar_colunas_documents(banco: Engine) -> None:
    """Aplica migrações SQLite pequenas para bancos locais já existentes."""

    if banco.dialect.name != "sqlite":
        return

    colunas = {
        coluna["name"]
        for coluna in inspect(banco).get_columns("documents")
    }
    if "title" not in colunas:
        with banco.begin() as conexao:
            conexao.exec_driver_sql(
                "ALTER TABLE documents ADD COLUMN title VARCHAR"
            )


def init_db(bind: Engine | None = None) -> None:
    """Register domain models, create ORM tables and initialize FTS5."""
    for module in (
        "corpus",
        "documents",
        "query",
        "feedback",
        "rag",
        "auth",
    ):
        import_module(f"app.modules.{module}.model")

    banco = engine if bind is None else bind
    Base.metadata.create_all(bind=banco)
    _migrar_colunas_documents(banco)

    # FTS5 é uma tabela virtual SQLite, portanto não é representada por um
    # modelo ORM comum. Ela indexa DocumentChunk e é mantida por triggers.
    from src.fts import inicializar_fts5

    inicializar_fts5(banco)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
