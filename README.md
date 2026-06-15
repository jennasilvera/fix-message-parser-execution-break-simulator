# FIX Message Parser & Execution Break Simulator

![FIX Parser CI](https://github.com/YOUR_USERNAME/fix-message-parser-execution-break-simulator/actions/workflows/ci.yml/badge.svg)

A recruiter-ready trading operations portfolio project that parses simulated FIX execution-report messages, reconciles them against internal order records and broker drop-copy-style records, and generates exception reports for trade support investigation.

> **Important:** All data in this repository is simulated. This project does not use real broker, OMS, EMS, hedge fund, client, exchange, or proprietary trading data.

## Why This Project Exists

Trading Operations, Trade Support, and Production Support teams often investigate issues such as missing execution reports, stale orders, rejected orders, broker discrepancies, duplicate execution IDs, and order-state breaks.

This project demonstrates those workflows in a student-accessible way using Python, SQL, SQLite, pandas, CSV files, pytest, and GitHub Actions.

## What the Project Demonstrates

- Parse simulated FIX tag-value execution reports.
- Convert raw FIX messages into structured CSV rows.
- Understand core order lifecycle states: New, Partially Filled, Filled, Rejected, and stale/open.
- Reconcile internal orders, FIX reports, broker drop-copy records, and expected order states.
- Detect common trade support exceptions using SQL.
- Generate CSV exception reports for investigation.
- Maintain a simple operational runbook.
- Validate parser and reconciliation behavior with automated tests and CI.

## Core FIX Concepts Used

FIX messages are commonly represented as tag-value pairs. For readability, this project uses the pipe character `|` as the delimiter in sample files. Real FIX messages typically use the SOH delimiter.

Example simulated execution report:

```text
8=FIX.4.2|35=8|49=BROKER1|56=CLIENT1|34=2|52=2026-06-14 09:30:07|37=B-1001|11=ORD-1001|17=E-1001-F1|150=1|39=1|55=AAPL|54=1|38=1000|32=400|31=190.2200|151=600|14=400|6=190.2200|10=002|
```

| Tag | Field | Meaning in this project |
|---:|---|---|
| 35 | MsgType | Message type. `35=8` means Execution Report. |
| 11 | ClOrdID | Client order ID from the internal system. |
| 37 | OrderID | Broker-assigned order ID. |
| 17 | ExecID | Broker execution identifier. Should be unique per execution event. |
| 150 | ExecType | Event type, such as New, Partial Fill, Fill, or Reject. |
| 39 | OrdStatus | Current order status after the event. |
| 55 | Symbol | Instrument ticker in this simulation. |
| 54 | Side | `1=BUY`, `2=SELL`. |
| 38 | OrderQty | Original order quantity. |
| 32 | LastQty | Quantity executed on the current execution report. |
| 31 | LastPx | Price for the current execution. |
| 151 | LeavesQty | Remaining open quantity. |
| 14 | CumQty | Cumulative executed quantity. |
| 6 | AvgPx | Average execution price so far. |

## Repository Structure

```text
.
├── .github/workflows/ci.yml
├── data/
│   ├── raw/fix_messages.txt
│   ├── input/internal_orders.csv
│   ├── input/broker_drop_copy.csv
│   ├── input/expected_order_states.csv
│   └── generated/fix_execution_reports.csv
├── db/
├── reports/exceptions/
├── sql/
│   ├── schema.sql
│   └── reconciliation_queries.sql
├── src/fixops/
│   ├── config.py
│   ├── fix_parser.py
│   ├── generate_sample_data.py
│   ├── load_db.py
│   └── reconcile.py
├── tests/
│   ├── test_parser.py
│   └── test_reconciliation.py
├── PROJECT_SCOPE.md
├── RUNBOOK.md
├── Makefile
├── pyproject.toml
└── requirements.txt
```

## Data Files

| File | Purpose |
|---|---|
| `data/raw/fix_messages.txt` | Raw simulated FIX execution-report messages. |
| `data/input/internal_orders.csv` | Internal order records from a simulated order-management source. |
| `data/generated/fix_execution_reports.csv` | Parsed structured output from the FIX parser. |
| `data/input/broker_drop_copy.csv` | Broker/drop-copy-style execution data. |
| `data/input/expected_order_states.csv` | Expected final order states used for status reconciliation. |

## Reconciliation Controls

The project generates separate CSV reports for:

1. Missing execution report
2. Missing broker drop copy
3. Rejected order
4. Stale open order
5. Quantity mismatch
6. Price mismatch
7. Side mismatch
8. Symbol mismatch
9. Order status mismatch
10. Duplicate ExecID
11. Unexpected fill
12. CumQty / LeavesQty inconsistency

Reports are written to:

```text
reports/exceptions/
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
make run
```

Or run each step manually:

```bash
python -m fixops.generate_sample_data
python -m fixops.fix_parser
python -m fixops.load_db
python -m fixops.reconcile
```

Expected terminal output from reconciliation:

```text
Reconciliation complete. Exception report counts:
- missing_execution_report: 1
- missing_broker_drop_copy: 1
- rejected_order: 1
- stale_open_order: 3
- quantity_mismatch: 1
- price_mismatch: 1
- side_mismatch: 1
- symbol_mismatch: 1
- order_status_mismatch: 2
- duplicate_exec_id: 1
- unexpected_fill: 1
- cumqty_leavesqty_inconsistency: 1
```

## Run Tests

```bash
pytest
```

GitHub Actions runs tests on Python 3.10, 3.11, and 3.12 and also runs the end-to-end sample pipeline.

## Example Exception Report

`reports/exceptions/duplicate_exec_id.csv`

| exec_id | duplicate_count | cl_ord_ids | exception_reason |
|---|---:|---|---|
| E-DUP-900 | 2 | ORD-1009, ORD-1009 | Same ExecID appears multiple times in the FIX execution-report stream |


## Suggested Commit Sequence

1. `Initialize project structure and documentation`
2. `Add simulated order and broker datasets`
3. `Implement FIX execution report parser`
4. `Add SQLite schema and database loader`
5. `Implement reconciliation controls and exception exports`
6. `Add parser and reconciliation tests`
7. `Add GitHub Actions CI workflow`
8. `Expand README with runbook, interview notes, and resume bullets`

## Disclaimer

This repository is a portfolio simulation. It does not connect to a live FIX session, broker, OMS, EMS, execution venue, hedge fund system, or trading database.
