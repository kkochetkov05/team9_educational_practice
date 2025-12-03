"""
Инициализирует все файлы для обработки по очереди.
"""

from db_connection_init import get_connection
from clean_wb_data import *
from csv_to_db_merger import *


if __name__ == "__main__":
    conn = get_connection()
    clean_main(conn)
    merge_main(conn)
    conn.commit()
    conn.close()


