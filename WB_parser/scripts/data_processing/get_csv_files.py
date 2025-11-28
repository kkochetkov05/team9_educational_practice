import pandas as pd
from config import table_name

def get_csv_files(csv_folder, conn):
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
        print("CSV файлов не найдено")
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