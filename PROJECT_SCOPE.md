# Project Scope

## Project Name

FIX Message Parser & Execution Break Simulator

## Goal

Build a realistic, recruiter-ready project that demonstrates trading operations, FIX message review, execution support, SQL reconciliation, exception reporting, and production-support thinking using only simulated data.

## What This Project Demonstrates

- Parsing simulated FIX execution reports from tag-value messages.
- Translating core FIX tags into structured columns.
- Understanding basic order lifecycle states: New, Partially Filled, Filled, Rejected, and open/stale orders.
- Comparing internal order records, FIX execution reports, broker drop-copy records, and expected order-state records.
- Detecting execution breaks with SQL controls.
- Producing CSV exception reports for investigation.
- Documenting operational triage steps in a runbook.
- Validating parser/reconciliation logic with pytest and GitHub Actions.

## What This Project Does Not Claim

This project does **not** claim professional experience with:

- Real broker connectivity
- Real FIX sessions
- OMS or EMS administration
- Hedge fund trading-desk systems
- Proprietary trading data
- Production trading infrastructure

All messages and datasets are simulated for educational and portfolio use.

## Intended Audience

- Trading Operations Associate recruiters
- Trade Support hiring managers
- Production Support interviewers
- Execution Operations teams
- Entry-level systematic trading / hedge fund operations teams

## Technical Stack

- Python
- pandas
- SQL
- SQLite
- CSV
- pytest
- GitHub Actions

## MVP Scope

The MVP focuses on batch-style parsing and reconciliation. It does not implement live FIX connectivity, real-time streaming, message sequencing, or order routing.

## Future Enhancements

- Add resend / sequence-gap simulation.
- Add cancel and cancel/replace workflows.
- Add allocation-level reconciliation.
- Add dashboard summary report.
- Add severity classification and SLA aging.
- Add CLI flags for report dates and threshold configuration.
