from fixops.fix_parser import parse_fix_message


def test_parse_execution_report_pipe_delimited_message():
    msg = "8=FIX.4.2|35=8|49=BROKER1|56=CLIENT1|34=1|52=2026-06-14 09:30:07|37=B-1001|11=ORD-1001|17=E-1001-F1|150=1|39=1|55=AAPL|54=1|38=1000|32=400|31=190.22|151=600|14=400|6=190.22|10=001|"
    parsed = parse_fix_message(msg)

    assert parsed["msg_type_name"] == "ExecutionReport"
    assert parsed["cl_ord_id"] == "ORD-1001"
    assert parsed["exec_type_name"] == "PartialFill"
    assert parsed["ord_status_name"] == "PartiallyFilled"
    assert parsed["side_name"] == "BUY"
    assert parsed["order_qty"] == 1000
    assert parsed["last_qty"] == 400
    assert parsed["last_px"] == 190.22


def test_parse_soh_delimited_message():
    msg = "8=FIX.4.2\x0135=8\x0111=ORD-ABC\x01150=2\x0139=2\x0154=2\x0138=10\x0132=10\x0131=99.5\x01151=0\x0114=10\x016=99.5\x01"
    parsed = parse_fix_message(msg)

    assert parsed["cl_ord_id"] == "ORD-ABC"
    assert parsed["exec_type_name"] == "Fill"
    assert parsed["ord_status_name"] == "Filled"
    assert parsed["side_name"] == "SELL"
