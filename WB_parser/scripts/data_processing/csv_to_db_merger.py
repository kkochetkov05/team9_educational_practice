from pathlib import Path
import sqlite3
import pandas as pd
import json

def get_csv_files():
    # with open(merged_days_path, 'r', encoding='utf-8') as f:
    #     merged_days = json.load(f)

    try:
        merged_days_df = pd.read_sql(f"SELECT DISTINCT date FROM {table_name} ORDER BY date", conn)
        merged_days = merged_days_df["date"].tolist()
    except:
        merged_days = []

    # Locate all CSV files
    csv_files = list(csv_folder.glob("*.csv"))

    if not csv_files:
        print("No CSV files found!")
        return [], [], []

    available_days = []
    for file in csv_files:
        available_days.append(str(file).split("\\")[-1].split('_')[0])

    for day in merged_days:
        if day in available_days:
            available_days.remove(day)

    i = 0
    while True:
        try:
            csv_file = csv_files[i]
        except IndexError:
            break
        if any(day == str(csv_files[i]).split("\\")[-1].split('_')[0] for day in merged_days):
            csv_files.remove(csv_files[i])
            i -= 1
        i += 1

    return csv_files, available_days, merged_days


def merge(csv_files):
    print(f"Loading {len(csv_files)} CSV files...")

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

    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({"PK INTEGER PRIMARY KEY AUTOINCREMENT"}, {columns})"
    cur.execute(create_table_sql)

    # Write data
    merged_df.to_sql(table_name, conn, if_exists="append", index=False)

    merged_days_df = pd.read_sql(f"SELECT DISTINCT date FROM {table_name} ORDER BY date", conn)

    merged_days = merged_days_df["date"].tolist()

    with open(merged_days_path, "w", encoding="utf-8") as f:
        json.dump(merged_days, f)

    conn.commit()
    conn.close()

    print(f"Merge complete! Database saved as: {db_file}")

    # for file in csv_files:
    #     file.unlink()


# if __name__ == '__main__':

# ───────────── CONFIGURATION ───────────── #
csv_folder = Path(__file__).parent.parent.parent / 'data' / 'clean_data'  # folder containing CSV files
# csv_folder = Path("WB_parser/data/raw_data")   # folder containing CSV files
db_file = Path(__file__).parent.parent.parent / 'data' / 'sql_database' / 'wildberries_data.db'  # name of output DB file
# db_file = "WB_parser/data/sql_database/merged.db"          # name of output DB file
merged_days_path = Path(__file__).parent.parent.parent / 'sources' / 'merged_days.json'
table_name = "wildberries_data"  # table name
# ───────────────────────────────────────── #

# подключаемся к БД
conn = sqlite3.connect(db_file)
cur = conn.cursor()

csv_files, available_days, merged_days = get_csv_files()

if not csv_files:
    print("All data is already merged!")
else:
    merge(csv_files)

