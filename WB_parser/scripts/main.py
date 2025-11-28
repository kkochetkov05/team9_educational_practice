import subprocess
from pathlib import Path

if __name__ == '__main__':

    PROJECT_ROOT = Path(__file__).parent.parent
    PARSER_SCRIPT_PATH = PROJECT_ROOT / 'scripts' / 'parser' / 'main.py'
    DATA_PROCESSING_SCRIPT_PATH = PROJECT_ROOT / 'scripts' / 'data_processing' / 'main.py'
    DB_PATH = PROJECT_ROOT / 'data' / 'sql_database' / 'wildberries_data.db'
    RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw_data'

    answer_pull = ['1', '2', '3']

    print("Что сделать?")
    print(f"1 - запустить парсер, после обработать данные и загрузить их в БД ({DB_PATH})")
    print(f"2 - запустить только парсер. Результат: сырые данные в {RAW_DATA_DIR}")
    print(f"3 - обработать данные из {RAW_DATA_DIR} и занести их в БД ({DB_PATH})\n")
    inp = input('1/2/3\n')

    while inp not in answer_pull:
        inp = input('1/2/3')
    if inp == '1':
        scripts_to_run = [
            PARSER_SCRIPT_PATH,
            DATA_PROCESSING_SCRIPT_PATH,
        ]

        for script in scripts_to_run:
            subprocess.run(["python", str(script)], check=True)
    elif inp == '2':
        subprocess.run(["python", str(PARSER_SCRIPT_PATH)], check=True)
    elif inp == '3':
        subprocess.run(["python", str(DATA_PROCESSING_SCRIPT_PATH)], check=True)