import json
import re

from pipeline.audit import log_event, mask_account

ISO_UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def test_mask_account_normal_case_keeps_prefix_and_last_two_chars():
    assert mask_account("ACC-1001") == "ACC-****01"


def test_mask_account_without_prefix_still_masks_middle_and_keeps_last_two():
    assert mask_account("1234567890") == "****90"


def test_mask_account_short_value_degrades_to_stars():
    assert mask_account("ACC-1") == "****"
    assert mask_account("ACC-12") == "****"
    assert mask_account("1") == "****"


def test_mask_account_empty_value_degrades_to_stars():
    assert mask_account("") == "****"


def test_mask_account_none_degrades_to_stars_without_raising():
    assert mask_account(None) == "****"


def test_log_event_returns_entry_with_exactly_four_fields(tmp_path):
    entry = log_event(
        base_dir=tmp_path,
        agent="fraud_detector",
        transaction_id="TXN001",
        outcome="approved",
    )

    assert set(entry.keys()) == {"timestamp", "agent", "transaction_id", "outcome"}
    assert entry["agent"] == "fraud_detector"
    assert entry["transaction_id"] == "TXN001"
    assert entry["outcome"] == "approved"
    assert ISO_UTC_PATTERN.match(entry["timestamp"])


def test_log_event_writes_one_json_line_to_audit_log(tmp_path):
    entry = log_event(
        base_dir=tmp_path,
        agent="validator",
        transaction_id="TXN002",
        outcome="rejected",
    )

    log_path = tmp_path / "audit.log"
    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == entry


def test_log_event_appends_multiple_calls_as_separate_lines(tmp_path):
    log_event(base_dir=tmp_path, agent="a1", transaction_id="TXN001", outcome="approved")
    log_event(base_dir=tmp_path, agent="a2", transaction_id="TXN002", outcome="rejected")

    log_path = tmp_path / "audit.log"
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["transaction_id"] == "TXN001"
    assert json.loads(lines[1])["transaction_id"] == "TXN002"


def test_log_event_entry_carries_only_the_four_allowed_fields_no_pii(tmp_path):
    # transaction_id and outcome are caller-controlled identifiers/labels,
    # never raw account numbers or free-text descriptions; log_event itself
    # must not add any additional field where such data could be smuggled in.
    entry = log_event(
        base_dir=tmp_path,
        agent="fraud_detector",
        transaction_id="TXN003",
        outcome="flagged",
    )

    assert set(entry.keys()) == {"timestamp", "agent", "transaction_id", "outcome"}
