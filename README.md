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
4. `WB_parser/scripts/main.py` - главный скрипт для взаимодействия с функционалом программы.

- # Структура
```
WB_parser/
├─ data/
│  ├─ analytics_output/
│  │  ├─ basic_analytics/
│  │  │  └─ .pdf файлы с основной аналитикой по всем дням
│  │  ├─ user_request_analytics/
│  │  │  └─ .jpg файлы с аналитикой по запросу
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

4. В директории `WB_parser/sources` содержатся `.json` файлы с нужными категориями и ссылками на нужные магазины.
5. Директории `WB_parser/data/raw_temp_data` и `WB_parser/data/clean_temp_data` нужны для хранения промежуточных данных в процессе обработки. Программа предоставляет выбор: удалять их сразу после обработки, или оставлять.
6. После обработки данные загружаются в базу данных - `WB_parser/data/sql_database/wildberries_data.db`.
7. В директории `WB_parser/data/analytics_output` содержатся файлы, содержащие аналитику, которую можно инициализировать в теле программы.

- # Как пользоваться
В `WB_parser/sources/brands_urls.json` добавить ссылки на файлы интересующих компаний. (*Опционально*) В `WB_parser/sources/categories.json` добавить интересующиеся категории.

Запустить файл `WB_parser/scripts/main.py` и следовать инструкциям в консоли.


1. При запуске парсера и обработки сырые данные сохраняются в папку `WB_parser/data/raw_temp_data` в `.csv` формате, затем обрабатываются и заносятся в базу данных `WB_parser/data/sql_database/wildberries_data.db`.
2. При запуске одного парсера сырые данные сохраняются в папку `WB_parser/data/raw_temp_data` в `.csv` формате.
3. При запуске одной обработки сырые `.csv` данные из `WB_parser/data/raw_temp_data` очистятся от ненужных категорий, NaN'ов, переместятся в `WB_parser/data/clean_temp_data`, затем загрузятся в базу данных `WB_parser/data/sql_database/wildberries_data.db`.
4. При запуске аналитики можно загрузить всю основную аналитику в папку `WB_parser/data/analytics_output/basic_analytics` в формате `.pdf` по каждому дню отдельно или загрузить аналитику по всему временному периоду по одной категории.

- # Команда
1. **Кочетков Кирилл** - разработка архитектуры, парсера.
2. **Князев Егор** - разработка скрипта для обработки данных.
3. **Еремин Михаил** - разработка скрипта для работы с базой данных.
4. **Кулябин Ярослав** - разработка скрипта для аналитики.