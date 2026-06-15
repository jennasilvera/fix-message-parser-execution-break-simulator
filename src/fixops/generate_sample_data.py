from __future__ import annotations

from pathlib import Path

import pandas as pd

from fixops.config import GENERATED_DIR, INPUT_DIR, RAW_DIR


def _fix_message(
    seq: int,
    ts: str,
    order_id: str,
    cl_ord_id: str,
    exec_id: str,
    exec_type: str,
    ord_status: str,
    symbol: str,
    side: str,
    order_qty: int,
    last_qty: int,
    last_px: float,
    leaves_qty: int,
    cum_qty: int,
    avg_px: float,
    text: str = "",
    price: float | None = None,
) -> str:
    fields = [
        ("8", "FIX.4.2"),
        ("9", "000"),
        ("35", "8"),
        ("49", "BROKER1"),
        ("56", "CLIENT1"),
        ("34", str(seq)),
        ("52", ts),
        ("37", order_id),
        ("11", cl_ord_id),
        ("17", exec_id),
        ("150", exec_type),
        ("39", ord_status),
        ("55", symbol),
        ("54", side),
        ("38", str(order_qty)),
    ]
    if price is not None:
        fields.append(("44", f"{price:.2f}"))
    fields.extend(
        [
            ("32", str(last_qty)),
            ("31", f"{last_px:.4f}"),
            ("151", str(leaves_qty)),
            ("14", str(cum_qty)),
            ("6", f"{avg_px:.4f}"),
            ("60", ts),
        ]
    )
    if text:
        fields.append(("58", text))
    fields.append(("10", f"{seq % 1000:03d}"))
    return "|".join(f"{tag}={value}" for tag, value in fields) + "|"


def generate_sample_data(base_dir: Path | str | None = None) -> None:
    if base_dir is None:
        from fixops.config import PROJECT_ROOT

        base_dir = PROJECT_ROOT
    base_dir = Path(base_dir)
    raw_dir = base_dir / "data" / "raw"
    input_dir = base_dir / "data" / "input"
    generated_dir = base_dir / "data" / "generated"
    raw_dir.mkdir(parents=True, exist_ok=True)
    input_dir.mkdir(parents=True, exist_ok=True)
    generated_dir.mkdir(parents=True, exist_ok=True)

    internal_orders = pd.DataFrame(
        [
            ["ORD-1001", "AAPL", "BUY", 1000, "LIMIT", 190.25, "STAT_ARB", "2026-06-14 09:30:01"],
            ["ORD-1002", "MSFT", "SELL", 500, "LIMIT", 420.10, "STAT_ARB", "2026-06-14 09:31:05"],
            ["ORD-1003", "TSLA", "BUY", 200, "MARKET", None, "MOMENTUM", "2026-06-14 09:35:11"],
            ["ORD-1004", "NVDA", "BUY", 150, "LIMIT", 900.00, "MOMENTUM", "2026-06-14 09:38:44"],
            ["ORD-1005", "AMZN", "SELL", 300, "LIMIT", 180.50, "PAIR_TRADE", "2026-06-14 09:40:03"],
            ["ORD-1006", "META", "BUY", 1000, "LIMIT", 500.00, "PAIR_TRADE", "2026-06-14 09:42:21"],
            ["ORD-1007", "JPM", "SELL", 600, "LIMIT", 205.30, "RISK_REBAL", "2026-06-14 09:45:01"],
            ["ORD-1008", "IBM", "BUY", 400, "LIMIT", 190.00, "RISK_REBAL", "2026-06-14 10:00:00"],
            ["ORD-1009", "ORCL", "BUY", 250, "LIMIT", 130.25, "STAT_ARB", "2026-06-14 10:05:00"],
            ["ORD-1010", "ADBE", "SELL", 120, "LIMIT", 475.10, "MOMENTUM", "2026-06-14 10:12:00"],
            ["ORD-1011", "CRM", "BUY", 350, "LIMIT", 250.00, "PAIR_TRADE", "2026-06-14 10:15:00"],
            ["ORD-1012", "GOOG", "BUY", 100, "LIMIT", 175.00, "STAT_ARB", "2026-06-14 10:20:00"],
            ["ORD-1013", "AMD", "SELL", 800, "LIMIT", 160.00, "MOMENTUM", "2026-06-14 10:25:00"],
            ["ORD-1014", "INTC", "BUY", 1000, "LIMIT", 33.00, "RISK_REBAL", "2026-06-14 10:30:00"],
        ],
        columns=["cl_ord_id", "symbol", "side", "order_qty", "order_type", "limit_px", "strategy", "sent_ts"],
    )
    internal_orders.to_csv(input_dir / "internal_orders.csv", index=False)

    broker_drop_copy = pd.DataFrame(
        [
            ["BD-1", "ORD-1001", "B-1001", "E-1001-F1", "AAPL", "BUY", 400, 190.22, "2026-06-14 09:30:07", "BROKER1"],
            ["BD-2", "ORD-1001", "B-1001", "E-1001-F2", "AAPL", "BUY", 600, 190.28, "2026-06-14 09:30:09", "BROKER1"],
            ["BD-3", "ORD-1002", "B-1002", "E-1002-F1", "MSFT", "SELL", 500, 420.05, "2026-06-14 09:31:11", "BROKER1"],
            ["BD-4", "ORD-1003", "B-1003", "E-1003-F1", "TSLA", "BUY", 180, 181.75, "2026-06-14 09:35:15", "BROKER1"],
            ["BD-5", "ORD-1006", "B-1006", "E-1006-F1", "META", "BUY", 1000, 500.00, "2026-06-14 09:42:28", "BROKER1"],
            ["BD-6", "ORD-1007", "B-1007", "E-1007-F1", "JPM", "BUY", 600, 205.31, "2026-06-14 09:45:05", "BROKER1"],
            ["BD-7", "ORD-1009", "B-1009", "E-DUP-900", "ORCL", "BUY", 250, 130.24, "2026-06-14 10:05:04", "BROKER1"],
            ["BD-8", "ORD-1010", "B-1010", "E-1010-F1", "ADBE", "SELL", 120, 475.09, "2026-06-14 10:12:07", "BROKER1"],
            ["BD-9", "ORD-1012", "B-1012", "E-1012-F1", "GOOGL", "BUY", 100, 175.01, "2026-06-14 10:20:05", "BROKER1"],
            ["BD-10", "ORD-1013", "B-1013", "E-1013-P1", "AMD", "SELL", 300, 160.01, "2026-06-14 10:25:07", "BROKER1"],
            ["BD-11", "ORD-1014", "B-1014", "E-1014-P1", "INTC", "BUY", 700, 33.01, "2026-06-14 10:30:07", "BROKER1"],
            ["BD-12", "ORD-9999", "B-9999", "E-9999-F1", "SPY", "BUY", 50, 550.10, "2026-06-14 10:40:03", "BROKER1"],
        ],
        columns=["broker_exec_id", "cl_ord_id", "order_id", "exec_id", "symbol", "side", "executed_qty", "avg_px", "exec_ts", "broker"],
    )
    broker_drop_copy.to_csv(input_dir / "broker_drop_copy.csv", index=False)

    expected_order_states = pd.DataFrame(
        [
            ["ORD-1001", "Filled", 1000, 0, 190.256, "Fully filled with two executions"],
            ["ORD-1002", "Filled", 500, 0, 420.05, "Clean fill"],
            ["ORD-1003", "Filled", 200, 0, 181.75, "Quantity mismatch expected versus broker"],
            ["ORD-1004", "Rejected", 0, 150, 0.0, "Rejected by broker"],
            ["ORD-1005", "Filled", 300, 0, 180.45, "Missing broker drop-copy row"],
            ["ORD-1006", "Filled", 1000, 0, 501.00, "Price mismatch versus broker"],
            ["ORD-1007", "Filled", 600, 0, 205.31, "Broker reports opposite side"],
            ["ORD-1008", "Filled", 400, 0, 190.00, "Expected filled but latest FIX status is still new/stale"],
            ["ORD-1009", "Filled", 250, 0, 130.24, "Duplicate ExecID in FIX stream"],
            ["ORD-1010", "Filled", 120, 0, 475.09, "Clean fill"],
            ["ORD-1011", "Filled", 350, 0, 250.00, "Missing execution report"],
            ["ORD-1012", "Filled", 100, 0, 175.01, "FIX/broker symbol differs from internal symbol"],
            ["ORD-1013", "Filled", 800, 0, 160.01, "Order-status mismatch: partial fill versus expected filled"],
            ["ORD-1014", "PartiallyFilled", 700, 300, 33.01, "CumQty + LeavesQty inconsistency in FIX report"],
        ],
        columns=["cl_ord_id", "expected_ord_status", "expected_cum_qty", "expected_leaves_qty", "expected_avg_px", "investigation_note"],
    )
    expected_order_states.to_csv(input_dir / "expected_order_states.csv", index=False)

    messages = [
        _fix_message(1, "2026-06-14 09:30:02", "B-1001", "ORD-1001", "E-1001-N", "0", "0", "AAPL", "1", 1000, 0, 0.0, 1000, 0, 0.0, price=190.25),
        _fix_message(2, "2026-06-14 09:30:07", "B-1001", "ORD-1001", "E-1001-F1", "1", "1", "AAPL", "1", 1000, 400, 190.22, 600, 400, 190.22, price=190.25),
        _fix_message(3, "2026-06-14 09:30:09", "B-1001", "ORD-1001", "E-1001-F2", "2", "2", "AAPL", "1", 1000, 600, 190.28, 0, 1000, 190.256, price=190.25),
        _fix_message(4, "2026-06-14 09:31:11", "B-1002", "ORD-1002", "E-1002-F1", "2", "2", "MSFT", "2", 500, 500, 420.05, 0, 500, 420.05, price=420.10),
        _fix_message(5, "2026-06-14 09:35:15", "B-1003", "ORD-1003", "E-1003-F1", "2", "2", "TSLA", "1", 200, 200, 181.75, 0, 200, 181.75),
        _fix_message(6, "2026-06-14 09:38:46", "B-1004", "ORD-1004", "E-1004-R1", "8", "8", "NVDA", "1", 150, 0, 0.0, 150, 0, 0.0, text="Limit price outside broker risk band", price=900.00),
        _fix_message(7, "2026-06-14 09:40:08", "B-1005", "ORD-1005", "E-1005-F1", "2", "2", "AMZN", "2", 300, 300, 180.45, 0, 300, 180.45, price=180.50),
        _fix_message(8, "2026-06-14 09:42:28", "B-1006", "ORD-1006", "E-1006-F1", "2", "2", "META", "1", 1000, 1000, 501.00, 0, 1000, 501.00, price=500.00),
        _fix_message(9, "2026-06-14 09:45:05", "B-1007", "ORD-1007", "E-1007-F1", "2", "2", "JPM", "2", 600, 600, 205.31, 0, 600, 205.31, price=205.30),
        _fix_message(10, "2026-06-14 10:00:01", "B-1008", "ORD-1008", "E-1008-N", "0", "0", "IBM", "1", 400, 0, 0.0, 400, 0, 0.0, price=190.00),
        _fix_message(11, "2026-06-14 10:05:04", "B-1009", "ORD-1009", "E-DUP-900", "2", "2", "ORCL", "1", 250, 250, 130.24, 0, 250, 130.24, price=130.25),
        _fix_message(12, "2026-06-14 10:05:05", "B-1009", "ORD-1009", "E-DUP-900", "2", "2", "ORCL", "1", 250, 250, 130.24, 0, 250, 130.24, price=130.25),
        _fix_message(13, "2026-06-14 10:12:07", "B-1010", "ORD-1010", "E-1010-F1", "2", "2", "ADBE", "2", 120, 120, 475.09, 0, 120, 475.09, price=475.10),
        _fix_message(14, "2026-06-14 10:20:05", "B-1012", "ORD-1012", "E-1012-F1", "2", "2", "GOOGL", "1", 100, 100, 175.01, 0, 100, 175.01, price=175.00),
        _fix_message(15, "2026-06-14 10:25:07", "B-1013", "ORD-1013", "E-1013-P1", "1", "1", "AMD", "2", 800, 300, 160.01, 500, 300, 160.01, price=160.00),
        _fix_message(16, "2026-06-14 10:30:07", "B-1014", "ORD-1014", "E-1014-P1", "1", "1", "INTC", "1", 1000, 700, 33.01, 400, 700, 33.01, price=33.00),
        _fix_message(17, "2026-06-14 10:40:03", "B-9999", "ORD-9999", "E-9999-F1", "2", "2", "SPY", "1", 50, 50, 550.10, 0, 50, 550.10),
    ]
    (raw_dir / "fix_messages.txt").write_text("\n".join(messages) + "\n", encoding="utf-8")

    # Create a placeholder so the generated directory is committed in an empty repo.
    (generated_dir / ".gitkeep").touch()


def main() -> None:
    generate_sample_data()
    print("Generated simulated CSV inputs and raw FIX messages.")


if __name__ == "__main__":
    main()
