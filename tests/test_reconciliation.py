from pathlib import Path

from fixops.fix_parser import parse_to_csv
from fixops.generate_sample_data import generate_sample_data
from fixops.load_db import create_database
from fixops.reconcile import run_all_reconciliations


def test_reconciliation_outputs_expected_controls(tmp_path: Path):
    generate_sample_data(tmp_path)
    parse_to_csv(tmp_path / "data" / "raw" / "fix_messages.txt", tmp_path / "data" / "generated" / "fix_execution_reports.csv")
    db_path = tmp_path / "db" / "trading_ops.db"
    create_database(db_path=db_path, base_dir=tmp_path)

    results = run_all_reconciliations(db_path=db_path, reports_dir=tmp_path / "reports" / "exceptions")

    assert len(results["missing_execution_report"]) == 1
    assert len(results["missing_broker_drop_copy"]) == 1
    assert len(results["rejected_order"]) == 1
    assert len(results["stale_open_order"]) >= 1
    assert len(results["quantity_mismatch"]) == 1
    assert len(results["price_mismatch"]) == 1
    assert len(results["side_mismatch"]) == 1
    assert len(results["symbol_mismatch"]) == 1
    assert len(results["order_status_mismatch"]) >= 2
    assert len(results["duplicate_exec_id"]) == 1
    assert len(results["unexpected_fill"]) == 1
    assert len(results["cumqty_leavesqty_inconsistency"]) == 1

    assert (tmp_path / "reports" / "exceptions" / "missing_execution_report.csv").exists()
