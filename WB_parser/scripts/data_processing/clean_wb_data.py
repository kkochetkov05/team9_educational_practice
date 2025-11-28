import pandas as pd
import json

from config import *

def clean_wb_data(input_file, output_file=None):
    """
    Очищает данные Wildberries: удаляет ненужные категории и строки с NaN
    """

    with open(LIGHT_INDUSTRY_CATEGORIES_PATH, 'r', encoding='utf-8') as f:
        categories = json.load(f)

    try:
        # if is_file_already_cleaned(input_file):
        #     print(f"Пропускаем уже очищенный файл: {Path(input_file).name}")
        #     return None

        df = pd.read_csv(input_file)

        print(f"Обработка файла: {input_file}")
        print(f"Исходное количество строк: {len(df):,}")

        # Удаление строк с NaN значениями
        df_clean = df.dropna()

        # Фильтрация по нужным категориям
        df_filtered = df_clean[df_clean['entity'].isin(categories)]

        # Расчет статистики
        removed_count = len(df_clean) - len(df_filtered)

        print(f"Удалено строк: {removed_count:,}")
        print(f"Осталось строк: {len(df_filtered):,}")

        if output_file is None:
            input_filename = Path(input_file).name
            # Файлы сохраняются в WB_parser/data/clear_data/
            output_file = CLEAN_DATA_DIR / f"{(input_filename.split('.'))[0]}_cleaned.csv"

        df_filtered.to_csv(output_file, index=False)
        print(f"Очищенные данные сохранены в: {output_file}")

        return df_filtered

    except FileNotFoundError:
        print(f"Файл {input_file} не найден!")
        return None

def clean_main(conn):
    """
     Обрабатывает все CSV файлы в папке raw_data
     """
    print(f"\nОчистка данных из {RAW_DATA_DIR}")
    # print(f"Исходные данные: {RAW_DATA_DIR}")
    # print(f"Выходные данные: {CLEAN_DATA_DIR}")

    from get_csv_files import get_csv_files
    csv_files, available_days, merged_days = get_csv_files(RAW_DATA_DIR, conn)

    if not csv_files:
        print(f"Все данные уже очищены или их нет в директории {RAW_DATA_DIR}")
        csv_files_to_delete = list(RAW_DATA_DIR.glob("*.csv"))
    else:
        for csv_file in csv_files:
            print(f"\nОбрабатываю: {csv_file.name}")
            clean_wb_data(str(csv_file))
        csv_files_to_delete = csv_files
    if csv_files_to_delete:
        print("Удалить файл(ы) с необработанными данными?")
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
    clean_main(conn)