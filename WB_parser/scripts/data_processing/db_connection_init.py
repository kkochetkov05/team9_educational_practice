"""
Скрипт инициализирует подключение к базе данных
"""

import sqlite3

from config import DB_PATH
_conn = None

def get_connection():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH)
    return _conn