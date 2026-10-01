from __future__ import annotations

from .connection import connect_database, database_path, get_connection
from .init_db import init_db, initialize_database


_LAZY_ORM_NAMES = {"Base", "SessionLocal", "engine", "get_db"}


def __getattr__(name: str):
    if name in _LAZY_ORM_NAMES:
        from . import orm

        return getattr(orm, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Base",
    "SessionLocal",
    "connect_database",
    "database_path",
    "engine",
    "get_connection",
    "get_db",
    "init_db",
    "initialize_database",
]
