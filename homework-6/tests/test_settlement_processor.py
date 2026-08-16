from decimal import Decimal

from agents.settlement_processor import (
    AGENT_NAME,
    FEE_RATE,
    process_message,
    settle,
)
from pipeline.message import create_envelope

VALID_TXN = {
    "transaction_id": "TXN001",
    "timestamp": "2026-03-16T09:00:00Z",
    "source_account": "ACC-1001",
    "destination_account": "ACC-2001",
    "amount": "1500.00",
    "currency": "USD",
    "transaction_type": "transfer",
    "description": "Monthly rent payment",
    "metadata": {"channel": "online", "country": "US"},
    "fraud_flag": False,
    "risk_score": "0",
    "status": "risk_scored",
}


def _txn(**overrides):
    txn = dict(VALID_TXN)
    txn.update(overrides)
    return txn


def _envelope(**overrides):
    return create_envelope(
        source_agent="fraud_detector",
        target_agent="settlement_processor",
        data=_txn(**overrides),
    )


def test_constants_match_spec():
    assert AGENT_NAME == "settlement_processor"
    assert FEE_RATE == Decimal("0.001")


# --- settle: fee arithmetic --------------------------------------------


def test_settle_plain_amount_fee_and_settled():
    result = settle(_txn(amount="1500.00"))

    assert result["settlement_fee"] == "1.50"
    assert result["settled_amount"] == "1498.50"


def test_settle_rounding_edge_half_up_not_half_even():
    # 9999.99 * 0.001 = 9.99999 -> rounds to 10.00 under ROUND_HALF_UP,
    # not 9.99 (which is what plain truncation or ROUND_DOWN would give).
    result = settle(_txn(amount="9999.99"))

    assert result["settlement_fee"] == "10.00"
    assert result["settled_amount"] == "9989.99"


# --- settle: status stamping --------------------------------------------


def test_settle_flagged_transaction_gets_settled_with_flag_status():
    result = settle(_txn(fraud_flag=True))

    assert result["status"] == "settled_with_flag"


def test_settle_clean_transaction_gets_settled_status():
    result = settle(_txn(fraud_flag=False))

    assert result["status"] == "settled"


def test_settle_never_mutates_its_argument():
    original = _txn(amount="1500.00", fraud_flag=False, status="risk_scored")
    original_copy = dict(original)

    result = settle(original)

    assert original == original_copy
    assert "settlement_fee" not in original
    assert "settled_amount" not in original
    assert result is not original
    assert result["settlement_fee"] == "1.50"
    assert result["status"] == "settled"


# --- process_message ------------------------------------------------------


def test_process_message_targets_results():
    message = _envelope()

    result = process_message(message)

    assert result["target_agent"] == "results"
    assert result["source_agent"] == AGENT_NAME


def test_process_message_clean_transaction():
    message = _envelope(amount="1500.00", fraud_flag=False)

    result = process_message(message)

    assert result["data"]["status"] == "settled"
    assert result["data"]["settlement_fee"] == "1.50"
    assert result["data"]["settled_amount"] == "1498.50"


def test_process_message_flagged_transaction():
    message = _envelope(amount="1500.00", fraud_flag=True)

    result = process_message(message)

    assert result["data"]["status"] == "settled_with_flag"
    assert result["data"]["settlement_fee"] == "1.50"
    assert result["data"]["settled_amount"] == "1498.50"


def test_process_message_never_mutates_input_data_dict():
    original_data = _txn()
    message = create_envelope(
        source_agent="fraud_detector",
        target_agent="settlement_processor",
        data=original_data,
    )

    process_message(message)

    assert "settlement_fee" not in original_data
    assert "settled_amount" not in original_data
    assert original_data["status"] == "risk_scored"
    assert message["data"] is original_data
