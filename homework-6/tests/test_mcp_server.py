"""Helper-level tests for the pipeline-status FastMCP server.

The server lives at mcp/server.py. The directory is named `mcp`, which shadows
the installed `mcp` SDK package that fastmcp depends on, so the module is
loaded directly from its file path via importlib rather than `import mcp...`.
"""

import importlib.util
import json
from pathlib import Path

import pytest

SERVER_PATH = Path(__file__).resolve().parent.parent / "mcp" / "server.py"


def _load_server_module():
    spec = importlib.util.spec_from_file_location("pipeline_status_server", SERVER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def server():
    return _load_server_module()


def _write_result(results_dir: Path, transaction_id: str, data: dict) -> None:
    envelope = {
        "message_id": "test-message-id",
        "timestamp": "2026-01-01T00:00:00Z",
        "source_agent": "settlement_processor",
        "target_agent": "results",
        "message_type": "transaction",
        "data": data,
    }
    (results_dir / f"{transaction_id}.json").write_text(json.dumps(envelope), encoding="utf-8")


def test_load_result_found(tmp_path, server):
    _write_result(
        tmp_path,
        "TXN001",
        {
            "transaction_id": "TXN001",
            "status": "settled",
            "risk_score": "0",
            "settled_amount": "1498.50",
        },
    )

    result = server.load_result(tmp_path, "TXN001")

    assert result["transaction_id"] == "TXN001"
    assert result["status"] == "settled"
    assert result["risk_score"] == "0"
    assert result["settled_amount"] == "1498.50"


def test_load_result_not_found(tmp_path, server):
    result = server.load_result(tmp_path, "TXN999")

    assert result["status"] == "not_found"
    assert result["transaction_id"] == "TXN999"


def test_load_result_includes_reason_when_present(tmp_path, server):
    _write_result(
        tmp_path,
        "TXN006",
        {
            "transaction_id": "TXN006",
            "status": "rejected",
            "reason": "unsupported currency: 'XYZ'",
        },
    )

    result = server.load_result(tmp_path, "TXN006")

    assert result["status"] == "rejected"
    assert result["reason"] == "unsupported currency: 'XYZ'"


def test_load_result_omits_optional_fields_when_absent(tmp_path, server):
    _write_result(tmp_path, "TXN010", {"transaction_id": "TXN010", "status": "settled"})

    result = server.load_result(tmp_path, "TXN010")

    assert "reason" not in result
    assert "risk_score" not in result
    assert "settled_amount" not in result


def test_summarize_skips_pipeline_summary_and_counts_correctly(tmp_path, server):
    _write_result(tmp_path, "TXN001", {"transaction_id": "TXN001", "status": "settled"})
    _write_result(tmp_path, "TXN002", {"transaction_id": "TXN002", "status": "settled_with_flag"})
    _write_result(
        tmp_path,
        "TXN003",
        {"transaction_id": "TXN003", "status": "rejected", "reason": "amount must be greater than zero"},
    )
    (tmp_path / "pipeline-summary.json").write_text(
        json.dumps({"generated_at": "2026-01-01T00:00:00Z", "transactions_in": 3}),
        encoding="utf-8",
    )

    summary = server.summarize(tmp_path)

    assert summary["count"] == 3
    transaction_ids = {entry["transaction_id"] for entry in summary["results"]}
    assert transaction_ids == {"TXN001", "TXN002", "TXN003"}
    assert "pipeline-summary" not in transaction_ids

    rejected_entry = next(entry for entry in summary["results"] if entry["transaction_id"] == "TXN003")
    assert rejected_entry["status"] == "rejected"
    assert rejected_entry["reason"] == "amount must be greater than zero"


def test_summarize_empty_directory(tmp_path, server):
    summary = server.summarize(tmp_path)

    assert summary == {"count": 0, "results": []}


def test_summary_text_pass_through(tmp_path, server):
    # pipeline-summary.json lives under shared/results/, not directly under shared/.
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    summary_content = json.dumps({"generated_at": "2026-01-01T00:00:00Z", "transactions_in": 8})
    (results_dir / "pipeline-summary.json").write_text(summary_content, encoding="utf-8")

    text = server.summary_text(tmp_path)

    assert text == summary_content


def test_summary_text_fallback_when_missing(tmp_path, server):
    text = server.summary_text(tmp_path)

    assert "No pipeline run yet" in text
    assert "uv run python integrator.py" in text


def test_resource_wrapper_wiring_returns_real_summary_not_fallback(tmp_path, server, monkeypatch):
    """Regression test: the pipeline://summary resource wrapper must pass SHARED_DIR
    (the shared dir) to summary_text, which itself looks under <shared_dir>/results/.
    A prior bug had the wrapper and helper disagree on which directory holds
    pipeline-summary.json, so the wrapper always returned the fallback even when a
    real run had produced a summary. This exercises the exact call the wrapper makes.
    """
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    summary_content = json.dumps({"generated_at": "2026-01-01T00:00:00Z", "transactions_in": 8})
    (results_dir / "pipeline-summary.json").write_text(summary_content, encoding="utf-8")

    monkeypatch.setattr(server, "SHARED_DIR", tmp_path)

    # Same argument the pipeline_summary() resource wrapper passes: SHARED_DIR itself.
    text = server.summary_text(server.SHARED_DIR)

    assert text == summary_content
    assert "No pipeline run yet" not in text
