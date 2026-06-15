from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd

from fixops.config import FIX_EXECUTION_REPORTS_PATH, FIX_MESSAGES_PATH

TAG_MAP = {
    "8": "begin_string",
    "9": "body_length",
    "35": "msg_type",
    "49": "sender_comp_id",
    "56": "target_comp_id",
    "34": "msg_seq_num",
    "52": "sending_time",
    "37": "order_id",
    "11": "cl_ord_id",
    "17": "exec_id",
    "150": "exec_type",
    "39": "ord_status",
    "55": "symbol",
    "54": "side",
    "38": "order_qty",
    "44": "price",
    "32": "last_qty",
    "31": "last_px",
    "151": "leaves_qty",
    "14": "cum_qty",
    "6": "avg_px",
    "58": "text",
    "60": "transact_time",
    "10": "check_sum",
}

MSG_TYPE_MAP = {
    "D": "NewOrderSingle",
    "8": "ExecutionReport",
}

EXEC_TYPE_MAP = {
    "0": "New",
    "1": "PartialFill",
    "2": "Fill",
    "4": "Canceled",
    "8": "Rejected",
}

ORD_STATUS_MAP = {
    "0": "New",
    "1": "PartiallyFilled",
    "2": "Filled",
    "4": "Canceled",
    "8": "Rejected",
}

SIDE_MAP = {
    "1": "BUY",
    "2": "SELL",
}

NUMERIC_FIELDS = {
    "body_length",
    "msg_seq_num",
    "order_qty",
    "price",
    "last_qty",
    "last_px",
    "leaves_qty",
    "cum_qty",
    "avg_px",
}

OUTPUT_COLUMNS = [
    "sending_time",
    "transact_time",
    "msg_type",
    "msg_type_name",
    "sender_comp_id",
    "target_comp_id",
    "msg_seq_num",
    "order_id",
    "cl_ord_id",
    "exec_id",
    "exec_type",
    "exec_type_name",
    "ord_status",
    "ord_status_name",
    "symbol",
    "side",
    "side_name",
    "order_qty",
    "price",
    "last_qty",
    "last_px",
    "leaves_qty",
    "cum_qty",
    "avg_px",
    "text",
    "raw_message",
]


def _coerce_numeric(value: str) -> int | float | str:
    """Convert integer-looking or decimal-looking values into numeric types."""
    if value == "":
        return value
    try:
        numeric = float(value)
        if numeric.is_integer():
            return int(numeric)
        return numeric
    except ValueError:
        return value


def normalize_fix_message(message: str) -> str:
    """Normalize FIX delimiter from SOH to pipe for readable sample data."""
    return message.strip().replace("\x01", "|").strip("|")


def parse_fix_message(message: str) -> dict[str, Any]:
    """Parse one FIX tag-value message into a flat dictionary.

    The parser supports standard SOH-delimited FIX and pipe-delimited sample data.
    It intentionally focuses on the subset of tags useful for order/execution support.
    """
    normalized = normalize_fix_message(message)
    parsed: dict[str, Any] = {"raw_message": normalized}

    if not normalized:
        raise ValueError("Cannot parse an empty FIX message")

    for token in normalized.split("|"):
        if "=" not in token:
            raise ValueError(f"Malformed FIX token without '=': {token!r}")
        tag, value = token.split("=", 1)
        field = TAG_MAP.get(tag, f"tag_{tag}")
        parsed[field] = _coerce_numeric(value) if field in NUMERIC_FIELDS else value

    parsed["msg_type_name"] = MSG_TYPE_MAP.get(str(parsed.get("msg_type", "")), "Unknown")
    parsed["exec_type_name"] = EXEC_TYPE_MAP.get(str(parsed.get("exec_type", "")), "Unknown")
    parsed["ord_status_name"] = ORD_STATUS_MAP.get(str(parsed.get("ord_status", "")), "Unknown")
    parsed["side_name"] = SIDE_MAP.get(str(parsed.get("side", "")), "Unknown")

    return parsed


def parse_fix_file(input_path: Path | str) -> list[dict[str, Any]]:
    """Parse a newline-delimited FIX sample file."""
    input_path = Path(input_path)
    rows = []
    with input_path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            row = parse_fix_message(line)
            row["source_line_no"] = line_no
            rows.append(row)
    return rows


def parse_to_dataframe(input_path: Path | str) -> pd.DataFrame:
    rows = parse_fix_file(input_path)
    df = pd.DataFrame(rows)
    for col in OUTPUT_COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df[OUTPUT_COLUMNS + ["source_line_no"]]


def parse_to_csv(input_path: Path | str = FIX_MESSAGES_PATH, output_path: Path | str = FIX_EXECUTION_REPORTS_PATH) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = parse_to_dataframe(input_path)
    df.to_csv(output_path, index=False, quoting=csv.QUOTE_MINIMAL)
    return output_path


def main() -> None:
    output = parse_to_csv()
    print(f"Parsed FIX messages -> {output}")


if __name__ == "__main__":
    main()
