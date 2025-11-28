import pandas as pd
from config import *

def merge(csv_files, conn):
    print(f"Загрузка {len(csv_files)} CSV файлов...")

    # читаем все CSV
    merged_df = pd.concat(
        (pd.read_csv(file) for file in csv_files),
        ignore_index=True
    )

    # удалим дубли по id + date, если такие возможны
    merged_df.drop_duplicates(subset=["id", "date"], keep="first", inplace=True)

    # Build CREATE TABLE statement dynamically
    columns = ", ".join(
        f"{col} TEXT"
        for col in merged_df.columns
    )

    cur = conn.cursor()
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({"PK INTEGER PRIMARY KEY AUTOINCREMENT"}, {columns})"
    cur.execute(create_table_sql)

    # Write data
    merged_df.to_sql(table_name, conn, if_exists="append", index=False)

    conn.commit()

    print(f"Готово. База данных сохранена в: {DB_PATH}")


def merge_main(conn):

    print("\nЗагрузка данных в БД")

    from get_csv_files import get_csv_files
    csv_files, available_days, merged_days = get_csv_files(CLEAN_DATA_DIR, conn)

    if not csv_files:
        print(f"Все данные уже загружены в базу данных или их нет в директории {CLEAN_DATA_DIR}")
        csv_files_to_delete = list(CLEAN_DATA_DIR.glob("*.csv"))
    else:
        merge(csv_files, conn)
        csv_files_to_delete = csv_files

    if csv_files_to_delete:
        print("Удалить csv файл(ы)?")
        print("y/n")
        inp = input()
        while inp != 'y' and inp != 'n':
            print("y/n")
            inp = input()
        if inp == 'y':
            for csv_file in csv_files_to_delete:
                csv_file.unlink()
        elif inp == 'n':
            pass

if __name__ == "__main__":
    from db_connection_init import get_connection
    conn = get_connection()
    merge_main(conn)
