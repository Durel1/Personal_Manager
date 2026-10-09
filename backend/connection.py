"""Short-lived SQLite connections shared by schema and query helpers."""
import os
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path
from backend.storage import application_directory


def database_path():
    override = os.environ.get('PERSONAL_MANAGER_DB')
    if override:
        return Path(override)
    if getattr(sys, 'frozen', False):
        folder = application_directory()
        folder.mkdir(parents=True, exist_ok=True)
        return folder/'projet_stage.db'
    default = Path(__file__).resolve().parents[1] / 'projet_stage.db'
    return default


@contextmanager
def connect_database(path=None):
    connection = sqlite3.connect(path if path is not None else database_path(), timeout=10)
    try:
        connection.execute('PRAGMA foreign_keys = ON')
        with connection:
            yield connection
    finally:
        # SQLite's context manager commits/rolls back, but does not close.
        connection.close()
