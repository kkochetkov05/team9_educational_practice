from pathlib import Path
import pandas as pd
import json

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

    merged_days_df = pd.read_sql(f"SELECT DISTINCT date FROM {table_name} ORDER BY date", conn)

    merged_days = merged_days_df["date"].tolist()

    with open(merged_days_path, "w", encoding="utf-8") as f:
        json.dump(merged_days, f)

    print(f"Готово. База данных сохранена в: {db_file}")


# ───────────── CONFIGURATION ───────────── #
csv_folder = Path(__file__).parent.parent.parent / 'data' / 'clean_data'  # folder containing CSV files
db_file = Path(__file__).parent.parent.parent / 'data' / 'sql_database' / 'wildberries_data.db'  # name of output DB file
merged_days_path = Path(__file__).parent.parent.parent / 'sources' / 'merged_days.json'
table_name = "wildberries_data"  # table name
# ───────────────────────────────────────── #


def merge_main(conn):

    print("\nЗагрузка данных в БД")

    from get_csv_files import get_csv_files
    csv_files, available_days, merged_days = get_csv_files(csv_folder, conn)

    if not csv_files:
        print(f"Все данные уже загружены в базу данных или их нет в директории {csv_folder}")
        csv_files_to_delete = list(csv_folder.glob("*.csv"))
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
