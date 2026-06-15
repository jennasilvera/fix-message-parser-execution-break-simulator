# Sample Trade Support Investigation

## Break Type

Quantity mismatch between the parsed FIX execution report and the broker/drop-copy-style record.

## Context

This project uses fully simulated data. The scenario represents a common trading operations workflow where an internal order record, a FIX execution report, and a broker drop-copy record need to be compared to confirm execution accuracy.

## Investigation Summary

The reconciliation process identified one order where the executed quantity reported in the parsed FIX execution report did not match the quantity reported by the simulated broker drop copy.

## Why This Matters

Quantity mismatches can indicate:

- Partial fills not reflected consistently across systems
- Drop-copy delay or missing broker-side update
- Incorrect internal booking
- Duplicate or stale execution records
- Downstream position or P&L impact if not reviewed

## Investigation Steps

1. Locate the affected order in the exception report:

```text
reports/exceptions/quantity_mismatch.csv
