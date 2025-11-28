import sqlite3
from pathlib import Path

from config import DB_PATH
_conn = None

def get_connection():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH)
    return _conn