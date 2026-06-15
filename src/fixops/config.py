from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INPUT_DIR = DATA_DIR / "input"
GENERATED_DIR = DATA_DIR / "generated"
DB_DIR = PROJECT_ROOT / "db"
REPORTS_DIR = PROJECT_ROOT / "reports" / "exceptions"
SQL_DIR = PROJECT_ROOT / "sql"

FIX_MESSAGES_PATH = RAW_DIR / "fix_messages.txt"
FIX_EXECUTION_REPORTS_PATH = GENERATED_DIR / "fix_execution_reports.csv"
DB_PATH = DB_DIR / "trading_ops.db"
RUN_AS_OF = "2026-06-14 16:00:00"
