from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from fixops.config import DB_PATH, REPORTS_DIR

RECONCILIATION_QUERIES: dict[str, str] = {
    "missing_execution_report": """
        SELECT
            i.cl_ord_id,
            i.symbol,
            i.side,
            i.order_qty,
            i.sent_ts,
            'Internal order has no FIX execution report' AS exception_reason
        FROM internal_orders i
        LEFT JOIN fix_execution_reports f
            ON i.cl_ord_id = f.cl_ord_id
        WHERE f.cl_ord_id IS NULL
        ORDER BY i.sent_ts;
    """,
    "missing_broker_drop_copy": """
        SELECT
            f.cl_ord_id,
            f.exec_id,
            f.symbol,
            f.side_name AS fix_side,
            f.last_qty,
            f.last_px,
            f.sending_time,
            'FIX fill has no matching broker drop-copy row by ExecID' AS exception_reason
        FROM fix_execution_reports f
        JOIN internal_orders i
            ON f.cl_ord_id = i.cl_ord_id
        LEFT JOIN broker_drop_copy b
            ON f.exec_id = b.exec_id
        WHERE f.exec_type_name IN ('PartialFill', 'Fill')
          AND b.exec_id IS NULL
        ORDER BY f.sending_time;
    """,
    "rejected_order": """
        WITH latest AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY cl_ord_id ORDER BY sending_time DESC, source_line_no DESC) AS rn
            FROM fix_execution_reports
        )
        SELECT
            l.cl_ord_id,
            l.order_id,
            l.exec_id,
            l.symbol,
            l.side_name AS side,
            l.order_qty,
            l.ord_status_name,
            l.exec_type_name,
            l.text,
            'Broker rejected the order' AS exception_reason
        FROM latest l
        WHERE l.rn = 1
          AND (l.ord_status_name = 'Rejected' OR l.exec_type_name = 'Rejected')
        ORDER BY l.sending_time;
    """,
    "stale_open_order": """
        WITH latest AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY cl_ord_id ORDER BY sending_time DESC, source_line_no DESC) AS rn
            FROM fix_execution_reports
        ), run_time AS (
            SELECT control_value AS run_as_of FROM run_control WHERE control_name = 'run_as_of'
        )
        SELECT
            l.cl_ord_id,
            l.symbol,
            l.side_name AS side,
            l.order_qty,
            l.cum_qty,
            l.leaves_qty,
            l.ord_status_name,
            l.sending_time AS latest_fix_time,
            r.run_as_of,
            ROUND((julianday(r.run_as_of) - julianday(l.sending_time)) * 24 * 60, 1) AS age_minutes,
            'Order remains open for more than 60 minutes' AS exception_reason
        FROM latest l
        CROSS JOIN run_time r
        WHERE l.rn = 1
          AND l.ord_status_name IN ('New', 'PartiallyFilled')
          AND COALESCE(l.leaves_qty, 0) > 0
          AND ((julianday(r.run_as_of) - julianday(l.sending_time)) * 24 * 60) > 60
        ORDER BY age_minutes DESC;
    """,
    "quantity_mismatch": """
        SELECT
            f.cl_ord_id,
            f.exec_id,
            f.symbol,
            f.last_qty AS fix_last_qty,
            b.executed_qty AS broker_executed_qty,
            'FIX LastQty differs from broker drop-copy executed quantity' AS exception_reason
        FROM fix_execution_reports f
        JOIN broker_drop_copy b
            ON f.exec_id = b.exec_id
        WHERE f.exec_type_name IN ('PartialFill', 'Fill')
          AND COALESCE(f.last_qty, 0) <> COALESCE(b.executed_qty, 0)
        ORDER BY f.cl_ord_id;
    """,
    "price_mismatch": """
        SELECT
            f.cl_ord_id,
            f.exec_id,
            f.symbol,
            f.last_px AS fix_last_px,
            b.avg_px AS broker_px,
            ROUND(ABS(COALESCE(f.last_px, 0) - COALESCE(b.avg_px, 0)), 6) AS abs_price_diff,
            'FIX LastPx differs from broker drop-copy price by more than one cent' AS exception_reason
        FROM fix_execution_reports f
        JOIN broker_drop_copy b
            ON f.exec_id = b.exec_id
        WHERE f.exec_type_name IN ('PartialFill', 'Fill')
          AND ABS(COALESCE(f.last_px, 0) - COALESCE(b.avg_px, 0)) > 0.01
        ORDER BY abs_price_diff DESC;
    """,
    "side_mismatch": """
        SELECT
            f.cl_ord_id,
            f.exec_id,
            i.side AS internal_side,
            f.side_name AS fix_side,
            b.side AS broker_side,
            f.symbol,
            'Side differs across internal order, FIX report, or broker drop copy' AS exception_reason
        FROM fix_execution_reports f
        JOIN internal_orders i
            ON f.cl_ord_id = i.cl_ord_id
        LEFT JOIN broker_drop_copy b
            ON f.exec_id = b.exec_id
        WHERE f.exec_type_name IN ('PartialFill', 'Fill')
          AND (
              COALESCE(i.side, '') <> COALESCE(f.side_name, '')
              OR COALESCE(b.side, f.side_name) <> COALESCE(f.side_name, '')
          )
        ORDER BY f.cl_ord_id;
    """,
    "symbol_mismatch": """
        SELECT
            f.cl_ord_id,
            f.exec_id,
            i.symbol AS internal_symbol,
            f.symbol AS fix_symbol,
            b.symbol AS broker_symbol,
            'Symbol differs across internal order, FIX report, or broker drop copy' AS exception_reason
        FROM fix_execution_reports f
        JOIN internal_orders i
            ON f.cl_ord_id = i.cl_ord_id
        LEFT JOIN broker_drop_copy b
            ON f.exec_id = b.exec_id
        WHERE f.exec_type_name IN ('PartialFill', 'Fill')
          AND (
              COALESCE(i.symbol, '') <> COALESCE(f.symbol, '')
              OR COALESCE(b.symbol, f.symbol) <> COALESCE(f.symbol, '')
          )
        ORDER BY f.cl_ord_id;
    """,
    "order_status_mismatch": """
        WITH latest AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY cl_ord_id ORDER BY sending_time DESC, source_line_no DESC) AS rn
            FROM fix_execution_reports
        )
        SELECT
            e.cl_ord_id,
            e.expected_ord_status,
            l.ord_status_name AS latest_fix_ord_status,
            e.expected_cum_qty,
            l.cum_qty AS latest_fix_cum_qty,
            e.expected_leaves_qty,
            l.leaves_qty AS latest_fix_leaves_qty,
            e.investigation_note,
            'Latest FIX order status does not match expected order-state table' AS exception_reason
        FROM expected_order_states e
        JOIN latest l
            ON e.cl_ord_id = l.cl_ord_id AND l.rn = 1
        WHERE COALESCE(e.expected_ord_status, '') <> COALESCE(l.ord_status_name, '')
        ORDER BY e.cl_ord_id;
    """,
    "duplicate_exec_id": """
        SELECT
            exec_id,
            COUNT(*) AS duplicate_count,
            GROUP_CONCAT(cl_ord_id, ', ') AS cl_ord_ids,
            GROUP_CONCAT(source_line_no, ', ') AS source_lines,
            'Same ExecID appears multiple times in the FIX execution-report stream' AS exception_reason
        FROM fix_execution_reports
        WHERE exec_id IS NOT NULL
        GROUP BY exec_id
        HAVING COUNT(*) > 1
        ORDER BY duplicate_count DESC, exec_id;
    """,
    "unexpected_fill": """
        SELECT
            f.cl_ord_id,
            f.exec_id,
            f.symbol,
            f.side_name AS side,
            f.last_qty,
            f.last_px,
            f.sending_time,
            'Fill reported for ClOrdID not present in internal order records' AS exception_reason
        FROM fix_execution_reports f
        LEFT JOIN internal_orders i
            ON f.cl_ord_id = i.cl_ord_id
        WHERE f.exec_type_name IN ('PartialFill', 'Fill')
          AND i.cl_ord_id IS NULL
        ORDER BY f.sending_time;
    """,
    "cumqty_leavesqty_inconsistency": """
        SELECT
            f.cl_ord_id,
            f.exec_id,
            f.symbol,
            f.order_qty AS fix_order_qty,
            i.order_qty AS internal_order_qty,
            f.cum_qty,
            f.leaves_qty,
            (COALESCE(f.cum_qty, 0) + COALESCE(f.leaves_qty, 0)) AS cum_plus_leaves,
            'CumQty + LeavesQty does not equal OrderQty' AS exception_reason
        FROM fix_execution_reports f
        LEFT JOIN internal_orders i
            ON f.cl_ord_id = i.cl_ord_id
        WHERE f.msg_type_name = 'ExecutionReport'
          AND COALESCE(f.order_qty, i.order_qty, 0) <> (COALESCE(f.cum_qty, 0) + COALESCE(f.leaves_qty, 0))
        ORDER BY f.cl_ord_id, f.sending_time;
    """,
}


def run_reconciliation_query(conn: sqlite3.Connection, name: str) -> pd.DataFrame:
    if name not in RECONCILIATION_QUERIES:
        raise KeyError(f"Unknown reconciliation query: {name}")
    return pd.read_sql_query(RECONCILIATION_QUERIES[name], conn)


def run_all_reconciliations(
    db_path: Path | str = DB_PATH,
    reports_dir: Path | str = REPORTS_DIR,
) -> dict[str, pd.DataFrame]:
    db_path = Path(db_path)
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, pd.DataFrame] = {}
    with sqlite3.connect(db_path) as conn:
        for name in RECONCILIATION_QUERIES:
            df = run_reconciliation_query(conn, name)
            output_path = reports_dir / f"{name}.csv"
            df.to_csv(output_path, index=False)
            results[name] = df
    return results


def main() -> None:
    results = run_all_reconciliations()
    print("Reconciliation complete. Exception report counts:")
    for name, df in results.items():
        print(f"- {name}: {len(df)}")


if __name__ == "__main__":
    main()
