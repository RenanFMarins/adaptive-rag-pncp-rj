from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from sqlalchemy.orm import DeclarativeBase
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base

    DeclarativeBase = declarative_base

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


if hasattr(DeclarativeBase, "__mro__"):
    class Base(DeclarativeBase):
        pass
else:
    Base = DeclarativeBase()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
