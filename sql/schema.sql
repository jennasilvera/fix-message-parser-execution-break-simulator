DROP TABLE IF EXISTS internal_orders;
DROP TABLE IF EXISTS fix_execution_reports;
DROP TABLE IF EXISTS broker_drop_copy;
DROP TABLE IF EXISTS expected_order_states;
DROP TABLE IF EXISTS run_control;

CREATE TABLE internal_orders (
    cl_ord_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
    order_qty INTEGER NOT NULL CHECK (order_qty > 0),
    order_type TEXT NOT NULL,
    limit_px REAL,
    strategy TEXT,
    sent_ts TEXT NOT NULL
);

CREATE TABLE fix_execution_reports (
    sending_time TEXT,
    transact_time TEXT,
    msg_type TEXT,
    msg_type_name TEXT,
    sender_comp_id TEXT,
    target_comp_id TEXT,
    msg_seq_num INTEGER,
    order_id TEXT,
    cl_ord_id TEXT,
    exec_id TEXT,
    exec_type TEXT,
    exec_type_name TEXT,
    ord_status TEXT,
    ord_status_name TEXT,
    symbol TEXT,
    side TEXT,
    side_name TEXT,
    order_qty INTEGER,
    price REAL,
    last_qty INTEGER,
    last_px REAL,
    leaves_qty INTEGER,
    cum_qty INTEGER,
    avg_px REAL,
    text TEXT,
    raw_message TEXT,
    source_line_no INTEGER
);

CREATE TABLE broker_drop_copy (
    broker_exec_id TEXT PRIMARY KEY,
    cl_ord_id TEXT,
    order_id TEXT,
    exec_id TEXT,
    symbol TEXT,
    side TEXT,
    executed_qty INTEGER,
    avg_px REAL,
    exec_ts TEXT,
    broker TEXT
);

CREATE TABLE expected_order_states (
    cl_ord_id TEXT PRIMARY KEY,
    expected_ord_status TEXT,
    expected_cum_qty INTEGER,
    expected_leaves_qty INTEGER,
    expected_avg_px REAL,
    investigation_note TEXT
);

CREATE TABLE run_control (
    control_name TEXT PRIMARY KEY,
    control_value TEXT NOT NULL
);

CREATE INDEX idx_fix_cl_ord_id ON fix_execution_reports(cl_ord_id);
CREATE INDEX idx_fix_exec_id ON fix_execution_reports(exec_id);
CREATE INDEX idx_broker_cl_ord_id ON broker_drop_copy(cl_ord_id);
CREATE INDEX idx_broker_exec_id ON broker_drop_copy(exec_id);
