from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw_temp_data"
CLEAN_DATA_DIR = PROJECT_ROOT / "data" / "clean_temp_data"
BRANDS_URLS_PATH = PROJECT_ROOT / 'sources' / 'brands_urls.json'