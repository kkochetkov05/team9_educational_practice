from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw_temp_data"
CLEAN_DATA_DIR = PROJECT_ROOT / "data" / "clean_temp_data"
DB_PATH = PROJECT_ROOT / 'data' / 'sql_database' / 'wildberries_data.db'
LIGHT_INDUSTRY_CATEGORIES_PATH = PROJECT_ROOT / 'sources' / 'light_industry_categories.json'
table_name = "wildberries_data"