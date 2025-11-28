import subprocess
from pathlib import Path

if __name__ == '__main__':
    PROJECT_ROOT = Path(__file__).parent.parent

    parser_script_path = PROJECT_ROOT / 'scripts' / 'parser' / 'data_parser_main.py'
    data_processing_script_path = PROJECT_ROOT / 'scripts' / 'data_processing' / 'process_data_main.py'
    db_file = PROJECT_ROOT / 'data' / 'sql_database' / 'wildberries_data.db'
    raw_data_path = PROJECT_ROOT / 'data' / 'raw_data'

    answer_pull = ['1', '2', '3']

    print("Что сделать?")
    print(f"1 - запустить парсер, после обработать данные и загрузить их в БД ({db_file})")
    print(f"2 - запустить только парсер. Результат: сырые данные в {raw_data_path}")
    print(f"3 - обработать данные из {raw_data_path} и занести их в БД ({db_file})\n")
    inp = input('1/2/3\n')

    while inp not in answer_pull:
        inp = input('1/2/3')
    if inp == '1':
        scripts_to_run = [
            parser_script_path,
            data_processing_script_path,
        ]

        for script in scripts_to_run:
            subprocess.run(["python", str(script)], check=True)
    elif inp == '2':
        subprocess.run(["python", str(parser_script_path)], check=True)
    elif inp == '3':
        subprocess.run(["python", str(data_processing_script_path)], check=True)