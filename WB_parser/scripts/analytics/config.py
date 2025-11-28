from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / 'data' / 'sql_database' / 'wildberries_data.db'
OUTPUT_BASE = PROJECT_ROOT / 'data' / "analytics_output"
BASIC_OUTPUT = OUTPUT_BASE / "basic_analytics"
USER_REQUEST_OUTPUT = OUTPUT_BASE / "user_request_analytics"