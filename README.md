# КОМАНДА 9
- # Описание
**Задача:** написать сервис, который собирает данные о товарах компаний, которые работают в России по отрасли "*Промышленность*" в товарной группе "*Легкая промышленность*".

Командой было принято решение сфокусировать внимание на маркетплейсе "***Wildberries***", так как он не обладает сложными механизмами защиты от парсинга, а также содержит огромное количество компаний в требуемой товарной группе.

На данном этапе реализации сервис позволяет собрать данные и предоставить небольшую аналитику о всех товарах компаний, ссылки на которые перечислены в файле `WB_parser/sources/brands_urls.json`, т.е. пользователь может самостоятельно пополнять его или менять под свои нужды.

- # Запуск программы
Стабильно работает на `Python 3.14`.

1. `git clone https://github.com/kkochetkov05/team9_educational_practice`
2. (желательно) создание venv
3. `pip install -r requirements.txt`
4. `python WB_parser/scripts/main.py` - главный скрипт для взаимодействия с функционалом программы.

- # Структура
```
WB_parser/
├─ data/
│  ├─ analytics_output/
│  │  ├─ basic_analytics/
│  │  └─ user_request_analytics/
│  ├─ clean_temp_data/
│  ├─ raw_temp_data/
│  └─ sql_database/
│     └─ wildberries_data.db
│
├─ scripts/
│  ├─ analytics/
│  │  ├─ config.py
│  │  └─ main.py
│  ├─ data_processing/
│  │  ├─ categories.py
│  │  ├─ clean_wb_data.py
│  │  ├─ config.py
│  │  ├─ csv_to_db_merger.py
│  │  ├─ db_connection_init.py
│  │  ├─ get_csv_files.py
│  │  └─ main.py
│  └─ parser/
│     ├─ config.py
│     ├─ get_brands_request_url.py
│     ├─ get_headers.py
│     ├─ main.py
│     └─ parser.py
│
├─ sources/
│  ├─ brands_urls.json
│  └─ light_industry_categories.json
│
└─ main.py
```

1. Директория `WB_parser/scripts/parser` содержит реализацию парсера. `WB_parser/scripts/parser/main.py` - исполняющий файл.
2. Директория `WB_parser/scripts/data_processing` содержит реализацию обработки данных и загрузку ее в базу данных. `WB_parser/scripts/data_processing/main.py` - исполняющий файл.
3. Директория `WB_parser/scripts/analytics` содержит реализацию аналитики по полученным данным. `WB_parser/scripts/analytics/main.py` - исполняющий файл.

В каждой из перечисленных выше директорий содержится файл `config.py`, в котором находятся все, необходимые для конкретного этапа, пути к ключевым файлам.

4. В директории `WB_parser/sources` содержатся 
5. Директории `WB_parser/data/raw_temp_data` и `WB_parser/data/clean_temp_data` нужны для хранения промежуточных данных в процессе обработки. Программа предоставляет выбор: удалять их сразу после обработки, или оставлять.
6. После обработки данные загружаются в базу данных - `WB_parser/data/sql_database/wildberries_data.db`.
7. В директории `WB_parser/data/analytics_output` содержатся файлы, содержащие аналитику, которую можно инициализировать в теле программы.