import json
import shutil
from pathlib import Path

import pytest

import integrator
from agents import fraud_detector, transaction_validator
from pipeline.protocol import ensure_shared_dirs, read_json

REAL_SAMPLE_PATH = Path(__file__).resolve().parent.parent / "sample-transactions.json"

EXPECTED_SETTLED = {"TXN001", "TXN003", "TXN008"}
EXPECTED_SETTLED_WITH_FLAG = {"TXN002", "TXN004", "TXN005"}
EXPECTED_REJECTED = {"TXN006", "TXN007"}


@pytest.fixture
def sample_copy(tmp_path):
    dest = tmp_path / "sample-transactions.json"
    shutil.copy(REAL_SAMPLE_PATH, dest)
    return dest


def _result_files(base_dir):
    return [
        p
        for p in (base_dir / "results").glob("*.json")
        if p.name != "pipeline-summary.json"
    ]


def _load_results_by_txn_id(base_dir):
    by_id = {}
    for path in _result_files(base_dir):
        envelope = read_json(path)
        by_id[envelope["data"]["transaction_id"]] = envelope["data"]
    return by_id


# --- full integration run ---------------------------------------------------


def test_run_pipeline_matches_expected_outcome(tmp_path, sample_copy):
    summary = integrator.run_pipeline(tmp_path, sample_copy)

    by_id = _load_results_by_txn_id(tmp_path)

    assert set(by_id) == EXPECTED_SETTLED | EXPECTED_SETTLED_WITH_FLAG | EXPECTED_REJECTED
    assert len(by_id) == 8

    for txn_id in EXPECTED_SETTLED:
        assert by_id[txn_id]["status"] == "settled"
    for txn_id in EXPECTED_SETTLED_WITH_FLAG:
        assert by_id[txn_id]["status"] == "settled_with_flag"
    for txn_id in EXPECTED_REJECTED:
        assert by_id[txn_id]["status"] == "rejected"

    assert summary["transactions_in"] == 8
    assert summary["results_total"] == 8
    assert summary["by_status"] == {
        "settled": 3,
        "settled_with_flag": 3,
        "rejected": 2,
    }

    assert (tmp_path / "results" / "pipeline-summary.json").exists()


def test_run_pipeline_leaves_input_output_processing_empty(tmp_path, sample_copy):
    integrator.run_pipeline(tmp_path, sample_copy)

    assert list((tmp_path / "input").glob("*.json")) == []
    assert list((tmp_path / "output").glob("*.json")) == []
    assert list((tmp_path / "processing").glob("*.json")) == []


# --- summary aggregates ------------------------------------------------------


def test_summary_rejection_reasons(tmp_path, sample_copy):
    summary = integrator.run_pipeline(tmp_path, sample_copy)

    assert set(summary["rejection_reasons"]) == EXPECTED_REJECTED
    assert "currency" in summary["rejection_reasons"]["TXN006"]
    assert "amount" in summary["rejection_reasons"]["TXN007"]


def test_summary_settled_volume_by_currency(tmp_path, sample_copy):
    summary = integrator.run_pipeline(tmp_path, sample_copy)

    # USD settled: TXN001 1498.50, TXN003 9989.99, TXN008 3196.80,
    # TXN002 24975.00, TXN005 74925.00 => 114585.29
    # EUR settled: TXN004 499.50
    assert summary["settled_volume_by_currency"]["USD"] == "114585.29"
    assert summary["settled_volume_by_currency"]["EUR"] == "499.50"


# --- error handling for malformed messages ----------------------------------


def test_malformed_json_file_becomes_error_result(tmp_path):
    ensure_shared_dirs(tmp_path)
    garbage_path = tmp_path / "input" / "garbage.json"
    garbage_path.write_text("{not valid json at all", encoding="utf-8")

    integrator.run_agent(
        tmp_path, transaction_validator.AGENT_NAME, transaction_validator.process_message
    )

    results = _result_files(tmp_path)
    assert len(results) == 1

    envelope = read_json(results[0])
    assert envelope["data"]["status"] == "error"
    assert envelope["data"]["transaction_id"] == "garbage"
    assert envelope["data"]["reason"]

    # the bad file must be claimed out of input/processing, never left behind
    assert list((tmp_path / "input").glob("*.json")) == []
    assert list((tmp_path / "processing").glob("*.json")) == []


def test_invalid_envelope_becomes_error_result(tmp_path):
    ensure_shared_dirs(tmp_path)
    bad_path = tmp_path / "input" / "bad-envelope.json"
    # valid JSON, correctly targeted, but missing required envelope fields
    # (message_id, timestamp, source_agent, message_type) so validate_envelope
    # rejects it once claimed.
    bad_path.write_text(
        json.dumps({"target_agent": "transaction_validator", "data": {}}),
        encoding="utf-8",
    )

    integrator.run_agent(
        tmp_path, transaction_validator.AGENT_NAME, transaction_validator.process_message
    )

    results = _result_files(tmp_path)
    assert len(results) == 1
    envelope = read_json(results[0])
    assert envelope["data"]["status"] == "error"
    assert envelope["data"]["transaction_id"] == "bad-envelope"


def test_run_agent_only_claims_messages_targeted_at_it(tmp_path):
    ensure_shared_dirs(tmp_path)
    from pipeline.message import create_envelope
    from pipeline.protocol import write_json

    other_envelope = create_envelope("integrator", "fraud_detector", {"transaction_id": "X"})
    write_json(tmp_path / "input" / f"{other_envelope['message_id']}.json", other_envelope)

    integrator.run_agent(
        tmp_path, transaction_validator.AGENT_NAME, transaction_validator.process_message
    )

    # not addressed to transaction_validator: must be left untouched in input
    assert len(list((tmp_path / "input").glob("*.json"))) == 1
    assert _result_files(tmp_path) == []


# --- seed_input --------------------------------------------------------------


def test_seed_input_wraps_each_record_and_returns_count(tmp_path, sample_copy):
    ensure_shared_dirs(tmp_path)

    count = integrator.seed_input(tmp_path, sample_copy)

    assert count == 8
    input_files = list((tmp_path / "input").glob("*.json"))
    assert len(input_files) == 8

    envelope = read_json(input_files[0])
    assert envelope["source_agent"] == "integrator"
    assert envelope["target_agent"] == "transaction_validator"
    assert envelope["message_id"] + ".json" == input_files[0].name


# --- audit log ----------------------------------------------------------------


def test_audit_log_exists_and_never_contains_raw_account_numbers(tmp_path, sample_copy):
    integrator.run_pipeline(tmp_path, sample_copy)

    audit_path = tmp_path / "audit.log"
    assert audit_path.exists()

    content = audit_path.read_text(encoding="utf-8")
    assert content.strip() != ""
    assert "ACC-1001" not in content
    assert "ACC-" not in content

    lines = [json.loads(line) for line in content.splitlines() if line.strip()]
    assert len(lines) > 0
    for entry in lines:
        assert set(entry) == {"timestamp", "agent", "transaction_id", "outcome"}


# --- main() --------------------------------------------------------------------


def test_main_returns_1_when_sample_missing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(integrator, "DEFAULT_SAMPLE_PATH", tmp_path / "does-not-exist.json")
    monkeypatch.setattr(integrator, "DEFAULT_BASE_DIR", tmp_path / "shared")

    exit_code = integrator.main()

    assert exit_code == 1
    assert "does-not-exist.json" in capsys.readouterr().err


def test_main_runs_pipeline_and_prints_summary(tmp_path, monkeypatch, capsys, sample_copy):
    monkeypatch.setattr(integrator, "DEFAULT_SAMPLE_PATH", sample_copy)
    monkeypatch.setattr(integrator, "DEFAULT_BASE_DIR", tmp_path / "shared")

    exit_code = integrator.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "TXN001" in output
    assert "settled" in output
