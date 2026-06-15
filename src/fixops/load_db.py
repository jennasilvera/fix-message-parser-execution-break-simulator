from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from fixops.config import DB_PATH, PROJECT_ROOT, RUN_AS_OF
from fixops.fix_parser import parse_to_csv


def create_database(db_path: Path | str = DB_PATH, base_dir: Path | str | None = None) -> Path:
    if base_dir is None:
        base_dir = PROJECT_ROOT
    base_dir = Path(base_dir)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    schema_path = base_dir / "sql" / "schema.sql"
    if not schema_path.exists():
        schema_path = PROJECT_ROOT / "sql" / "schema.sql"
    input_dir = base_dir / "data" / "input"
    raw_path = base_dir / "data" / "raw" / "fix_messages.txt"
    generated_path = base_dir / "data" / "generated" / "fix_execution_reports.csv"

    if not generated_path.exists():
        parse_to_csv(raw_path, generated_path)

    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        tables = {
            "internal_orders": input_dir / "internal_orders.csv",
            "fix_execution_reports": generated_path,
            "broker_drop_copy": input_dir / "broker_drop_copy.csv",
            "expected_order_states": input_dir / "expected_order_states.csv",
        }
        for table, path in tables.items():
            df = pd.read_csv(path)
            df.to_sql(table, conn, if_exists="append", index=False)

        conn.execute(
            "INSERT INTO run_control(control_name, control_value) VALUES (?, ?)",
            ("run_as_of", RUN_AS_OF),
        )
        conn.commit()

    return db_path


def main() -> None:
    db_path = create_database()
    print(f"Loaded SQLite database -> {db_path}")


if __name__ == "__main__":
    main()
