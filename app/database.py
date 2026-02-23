import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "ghc2026.db"


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()
