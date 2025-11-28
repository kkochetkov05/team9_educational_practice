import sqlite3
from pathlib import Path

db_file = Path(__file__).parent.parent.parent / 'data' / 'sql_database' / 'wildberries_data.db'
_conn = None

def get_connection():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(db_file)
    return _conn