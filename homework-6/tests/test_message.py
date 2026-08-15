import re

from pipeline.message import create_envelope, utc_now_iso, validate_envelope

ISO_UTC_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
)


def test_envelope_has_all_six_required_fields():
    envelope = create_envelope(
        source_agent="validator",
        target_agent="fraud_detector",
        data={"transaction_id": "TXN001"},
    )

    assert set(envelope.keys()) == {
        "message_id",
        "timestamp",
        "source_agent",
        "target_agent",
        "message_type",
        "data",
    }


def test_envelope_defaults_message_type_to_transaction():
    envelope = create_envelope(
        source_agent="validator",
        target_agent="fraud_detector",
        data={"transaction_id": "TXN001"},
    )

    assert envelope["message_type"] == "transaction"


def test_envelope_message_type_can_be_overridden():
    envelope = create_envelope(
        source_agent="validator",
        target_agent="fraud_detector",
        data={},
        message_type="audit",
    )

    assert envelope["message_type"] == "audit"


def test_message_ids_are_unique_across_calls():
    envelope_a = create_envelope(
        source_agent="validator", target_agent="fraud_detector", data={}
    )
    envelope_b = create_envelope(
        source_agent="validator", target_agent="fraud_detector", data={}
    )

    assert envelope_a["message_id"] != envelope_b["message_id"]


def test_envelope_timestamp_matches_iso_utc_z_style():
    envelope = create_envelope(
        source_agent="validator", target_agent="fraud_detector", data={}
    )

    assert ISO_UTC_PATTERN.match(envelope["timestamp"])


def test_utc_now_iso_matches_spec_style():
    timestamp = utc_now_iso()

    assert ISO_UTC_PATTERN.match(timestamp)


def test_envelope_source_and_target_agent_are_preserved():
    envelope = create_envelope(
        source_agent="validator",
        target_agent="fraud_detector",
        data={"key": "value"},
    )

    assert envelope["source_agent"] == "validator"
    assert envelope["target_agent"] == "fraud_detector"
    assert envelope["data"] == {"key": "value"}


def test_validate_envelope_passes_a_good_envelope():
    envelope = create_envelope(
        source_agent="validator", target_agent="fraud_detector", data={}
    )

    assert validate_envelope(envelope) == []


def test_validate_envelope_flags_non_dict_input():
    errors = validate_envelope(["not", "a", "dict"])

    assert errors == ["envelope must be a dict"]


def test_validate_envelope_flags_missing_fields():
    incomplete = {
        "message_id": "abc",
        "timestamp": "2026-03-16T10:00:00Z",
        "source_agent": "validator",
        # missing target_agent, message_type, data
    }

    errors = validate_envelope(incomplete)

    assert any("target_agent" in error for error in errors)
    assert any("message_type" in error for error in errors)
    assert any("data" in error for error in errors)


def test_validate_envelope_flags_non_dict_data():
    envelope = create_envelope(
        source_agent="validator", target_agent="fraud_detector", data={}
    )
    envelope["data"] = "not a dict"

    errors = validate_envelope(envelope)

    assert any("data" in error for error in errors)
