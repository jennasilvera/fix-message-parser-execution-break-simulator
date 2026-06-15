-- Reconciliation controls for FIX Message Parser & Execution Break Simulator.
-- These mirror the SQL used by src/fixops/reconcile.py.

-- 1) Missing execution report: internal order exists but no FIX report arrived.
SELECT i.*
FROM internal_orders i
LEFT JOIN fix_execution_reports f ON i.cl_ord_id = f.cl_ord_id
WHERE f.cl_ord_id IS NULL;

-- 2) Missing broker drop copy: FIX fill exists but broker file has no matching ExecID.
SELECT f.cl_ord_id, f.exec_id, f.symbol, f.side_name, f.last_qty, f.last_px
FROM fix_execution_reports f
LEFT JOIN broker_drop_copy b ON f.exec_id = b.exec_id
WHERE f.exec_type_name IN ('PartialFill', 'Fill')
  AND b.exec_id IS NULL;

-- 3) Rejected order.
WITH latest AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY cl_ord_id ORDER BY sending_time DESC, source_line_no DESC) AS rn
    FROM fix_execution_reports
)
SELECT *
FROM latest
WHERE rn = 1 AND (ord_status_name = 'Rejected' OR exec_type_name = 'Rejected');

-- 4) Stale open order.
WITH latest AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY cl_ord_id ORDER BY sending_time DESC, source_line_no DESC) AS rn
    FROM fix_execution_reports
), run_time AS (
    SELECT control_value AS run_as_of FROM run_control WHERE control_name = 'run_as_of'
)
SELECT l.*, ROUND((julianday(r.run_as_of) - julianday(l.sending_time)) * 24 * 60, 1) AS age_minutes
FROM latest l
CROSS JOIN run_time r
WHERE l.rn = 1
  AND l.ord_status_name IN ('New', 'PartiallyFilled')
  AND COALESCE(l.leaves_qty, 0) > 0
  AND ((julianday(r.run_as_of) - julianday(l.sending_time)) * 24 * 60) > 60;

-- 5) Quantity mismatch.
SELECT f.cl_ord_id, f.exec_id, f.last_qty AS fix_last_qty, b.executed_qty AS broker_executed_qty
FROM fix_execution_reports f
JOIN broker_drop_copy b ON f.exec_id = b.exec_id
WHERE f.exec_type_name IN ('PartialFill', 'Fill')
  AND COALESCE(f.last_qty, 0) <> COALESCE(b.executed_qty, 0);

-- 6) Price mismatch.
SELECT f.cl_ord_id, f.exec_id, f.last_px AS fix_last_px, b.avg_px AS broker_px
FROM fix_execution_reports f
JOIN broker_drop_copy b ON f.exec_id = b.exec_id
WHERE f.exec_type_name IN ('PartialFill', 'Fill')
  AND ABS(COALESCE(f.last_px, 0) - COALESCE(b.avg_px, 0)) > 0.01;

-- 7) Side mismatch.
SELECT f.cl_ord_id, f.exec_id, i.side AS internal_side, f.side_name AS fix_side, b.side AS broker_side
FROM fix_execution_reports f
JOIN internal_orders i ON f.cl_ord_id = i.cl_ord_id
LEFT JOIN broker_drop_copy b ON f.exec_id = b.exec_id
WHERE f.exec_type_name IN ('PartialFill', 'Fill')
  AND (COALESCE(i.side, '') <> COALESCE(f.side_name, '') OR COALESCE(b.side, f.side_name) <> COALESCE(f.side_name, ''));

-- 8) Symbol mismatch.
SELECT f.cl_ord_id, f.exec_id, i.symbol AS internal_symbol, f.symbol AS fix_symbol, b.symbol AS broker_symbol
FROM fix_execution_reports f
JOIN internal_orders i ON f.cl_ord_id = i.cl_ord_id
LEFT JOIN broker_drop_copy b ON f.exec_id = b.exec_id
WHERE f.exec_type_name IN ('PartialFill', 'Fill')
  AND (COALESCE(i.symbol, '') <> COALESCE(f.symbol, '') OR COALESCE(b.symbol, f.symbol) <> COALESCE(f.symbol, ''));

-- 9) Order status mismatch.
WITH latest AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY cl_ord_id ORDER BY sending_time DESC, source_line_no DESC) AS rn
    FROM fix_execution_reports
)
SELECT e.cl_ord_id, e.expected_ord_status, l.ord_status_name AS latest_fix_ord_status
FROM expected_order_states e
JOIN latest l ON e.cl_ord_id = l.cl_ord_id AND l.rn = 1
WHERE COALESCE(e.expected_ord_status, '') <> COALESCE(l.ord_status_name, '');

-- 10) Duplicate ExecID.
SELECT exec_id, COUNT(*) AS duplicate_count, GROUP_CONCAT(cl_ord_id, ', ') AS cl_ord_ids
FROM fix_execution_reports
WHERE exec_id IS NOT NULL
GROUP BY exec_id
HAVING COUNT(*) > 1;

-- 11) Unexpected fill.
SELECT f.*
FROM fix_execution_reports f
LEFT JOIN internal_orders i ON f.cl_ord_id = i.cl_ord_id
WHERE f.exec_type_name IN ('PartialFill', 'Fill')
  AND i.cl_ord_id IS NULL;

-- 12) CumQty / LeavesQty inconsistency.
SELECT f.cl_ord_id, f.exec_id, f.order_qty, f.cum_qty, f.leaves_qty, COALESCE(f.cum_qty, 0) + COALESCE(f.leaves_qty, 0) AS cum_plus_leaves
FROM fix_execution_reports f
WHERE COALESCE(f.order_qty, 0) <> (COALESCE(f.cum_qty, 0) + COALESCE(f.leaves_qty, 0));
