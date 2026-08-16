import json

from agents.transaction_validator import (
    AGENT_NAME,
    ISO_4217,
    NEXT_AGENT,
    REQUIRED_FIELDS,
    main,
    process_message,
    validation_errors,
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
}


def _txn(**overrides):
    txn = dict(VALID_TXN)
    txn.update(overrides)
    return txn


def test_constants_match_spec():
    assert AGENT_NAME == "transaction_validator"
    assert NEXT_AGENT == "fraud_detector"
    assert REQUIRED_FIELDS == (
        "transaction_id",
        "timestamp",
        "source_account",
        "destination_account",
        "amount",
        "currency",
        "transaction_type",
    )


def test_iso_4217_includes_required_currencies():
    assert {"USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"} <= ISO_4217


def test_validation_errors_empty_for_a_valid_transaction():
    assert validation_errors(_txn()) == []


def test_validation_errors_negative_amount():
    errors = validation_errors(_txn(amount="-100.00"))

    assert any("amount" in error for error in errors)


def test_validation_errors_zero_amount():
    errors = validation_errors(_txn(amount="0.00"))

    assert any("amount" in error for error in errors)


def test_validation_errors_non_numeric_amount():
    errors = validation_errors(_txn(amount="not-a-number"))

    assert any("amount" in error for error in errors)


def test_validation_errors_unknown_currency():
    errors = validation_errors(_txn(currency="XYZ"))

    assert any("currency" in error for error in errors)


def test_validation_errors_missing_field():
    txn = _txn()
    del txn["destination_account"]

    errors = validation_errors(txn)

    assert any("destination_account" in error for error in errors)


def test_validation_errors_empty_string_field_counts_as_missing():
    errors = validation_errors(_txn(source_account=""))

    assert any("source_account" in error for error in errors)


def test_validation_errors_bad_timestamp():
    errors = validation_errors(_txn(timestamp="not-a-timestamp"))

    assert any("timestamp" in error for error in errors)


def test_validation_errors_non_string_timestamp_does_not_raise():
    errors = validation_errors(_txn(timestamp=12345))

    assert any("timestamp" in error for error in errors)


def test_validation_errors_unhashable_currency_does_not_raise():
    errors = validation_errors(_txn(currency=["XYZ"]))

    assert any("currency" in error for error in errors)


def test_validation_errors_accepts_z_suffixed_timestamp():
    assert validation_errors(_txn(timestamp="2026-03-16T09:00:00Z")) == []


def test_process_message_happy_path_forwards_to_fraud_detector():
    message = create_envelope(
        source_agent="integrator", target_agent="transaction_validator", data=_txn()
    )

    result = process_message(message)

    assert result["source_agent"] == "transaction_validator"
    assert result["target_agent"] == "fraud_detector"
    assert result["data"]["status"] == "validated"
    assert result["data"]["transaction_id"] == "TXN001"


def test_process_message_rejects_invalid_transaction_with_joined_reason():
    message = create_envelope(
        source_agent="integrator",
        target_agent="transaction_validator",
        data=_txn(amount="-100.00", currency="XYZ"),
    )

    result = process_message(message)

    assert result["target_agent"] == "results"
    assert result["data"]["status"] == "rejected"
    assert "amount" in result["data"]["reason"]
    assert "currency" in result["data"]["reason"]


def test_process_message_never_mutates_input_data_dict():
    original_data = _txn(amount="-100.00")
    message = create_envelope(
        source_agent="integrator", target_agent="transaction_validator", data=original_data
    )

    process_message(message)

    assert "status" not in original_data
    assert "reason" not in original_data
    assert message["data"] is original_data


def test_cli_dry_run_reports_correct_counts(tmp_path, monkeypatch, capsys):
    sample = [
        _txn(),
        _txn(transaction_id="TXN006", currency="XYZ"),
        _txn(transaction_id="TXN007", amount="-100.00"),
    ]
    sample_path = tmp_path / "sample.json"
    sample_path.write_text(json.dumps(sample), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv", ["transaction_validator", "--dry-run", "--sample", str(sample_path)]
    )

    exit_code = main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "TXN001" in output
    assert "TXN006" in output
    assert "TXN007" in output
    assert "Total: 3" in output
    assert "Valid: 1" in output
    assert "Invalid: 2" in output
