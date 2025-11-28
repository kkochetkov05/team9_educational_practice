import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent

RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw_temp_data'
DB_PATH = PROJECT_ROOT / 'data' / 'sql_database' / 'wildberries_data.db'

PARSER_SCRIPT_PATH = PROJECT_ROOT / 'scripts' / 'parser' / 'main.py'
DATA_PROCESSING_SCRIPT_PATH = PROJECT_ROOT / 'scripts' / 'data_processing' / 'main.py'
ANALYTICS_SCRIPT_PATH = PROJECT_ROOT / 'scripts' / 'analytics' / 'main.py'


def run_script(path: Path):
    subprocess.run(["python", str(path)], check=True)


def main_menu():
    while True:
        print("\n" + "=" * 60)
        print(f"Текущая БД: {DB_PATH}")
        print("-" * 60)
        print("1 — Запустить парсер, затем обработать данные и загрузить в БД")
        print(f"2 — Запустить только парсер (сырые данные → {RAW_DATA_DIR})")
        print("3 — Обработать данные из raw_data и загрузить в БД")
        print("4 — Запустить аналитику")
        print("0 — Выход")
        print("-" * 60)

        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            print("Выход из программы.")
            break

        elif choice == "1":
            print("\n[1] Запуск парсера...")
            run_script(PARSER_SCRIPT_PATH)
            print("[1] Парсер завершил работу.\n")

            print("[1] Обработка данных и загрузка в БД...")
            run_script(DATA_PROCESSING_SCRIPT_PATH)
            print("[1] Обработка завершена.\n")

        elif choice == "2":
            print("\n[2] Запуск парсера...")
            run_script(PARSER_SCRIPT_PATH)
            print("[2] Парсер завершил работу.\n")

        elif choice == "3":
            print("\n[3] Обработка данных и загрузка в БД...")
            run_script(DATA_PROCESSING_SCRIPT_PATH)
            print("[3] Обработка завершена.\n")

        elif choice == "4":
            print("\n[4] Запуск аналитики...")
            run_script(ANALYTICS_SCRIPT_PATH)
            print("[4] Аналитика завершена.\n")

        else:
            print("Неверный ввод. Введите 0, 1, 2, 3 или 4.")


if __name__ == "__main__":
    main_menu()