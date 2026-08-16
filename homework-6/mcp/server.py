"""FastMCP server exposing pipeline result status as tools and a resource.

The banking pipeline (see ../integrator.py) writes one result envelope per
transaction to shared/results/<transaction_id>.json, plus a plain summary
dict at shared/results/pipeline-summary.json (not an envelope — it has no
"data" key and is always skipped when listing results).

This module lives at mcp/server.py. The directory is named `mcp`, which
would shadow the installed `mcp` SDK package that fastmcp depends on if it
were ever imported as a package (`import mcp...`). To avoid that, this file
is never imported as part of a `mcp` package — it has no mcp/__init__.py
sibling, and callers (tests, `uv run python mcp/server.py`) load or run it
by file path only.

Plain helper functions are the single source of truth; the decorated
tools/resource below are thin wrappers around them.
"""

import json
import os
from pathlib import Path

from fastmcp import FastMCP

SHARED_DIR = Path(os.environ.get("PIPELINE_SHARED_DIR", Path(__file__).resolve().parent.parent / "shared"))

SUMMARY_FILENAME = "pipeline-summary.json"

_OPTIONAL_FIELDS = ("reason", "risk_score", "settled_amount")

mcp = FastMCP("pipeline-status")


def load_result(results_dir: Path, transaction_id: str) -> dict:
    """Load one transaction's result envelope and flatten it to a status dict.

    Returns a dict with transaction_id, status, and any of reason/risk_score/
    settled_amount present in the envelope's "data". If no result file exists
    yet for this transaction, returns a graceful {"status": "not_found", ...}
    answer instead of raising.
    """
    result_file = results_dir / f"{transaction_id}.json"
    if not result_file.is_file():
        return {"transaction_id": transaction_id, "status": "not_found"}

    envelope = json.loads(result_file.read_text(encoding="utf-8"))
    data = envelope.get("data", {})

    result = {
        "transaction_id": data.get("transaction_id", transaction_id),
        "status": data.get("status", "unknown"),
    }
    for field in _OPTIONAL_FIELDS:
        if field in data:
            result[field] = data[field]
    return result


def summarize(results_dir: Path) -> dict:
    """Aggregate every result file in results_dir into a count + status list.

    Skips pipeline-summary.json (a plain summary dict, not a result envelope).
    Returns {"count": N, "results": [{transaction_id, status, reason}, ...]}.
    """
    results = []
    for result_file in sorted(results_dir.glob("*.json")):
        if result_file.name == SUMMARY_FILENAME:
            continue
        envelope = json.loads(result_file.read_text(encoding="utf-8"))
        data = envelope.get("data", {})
        results.append(
            {
                "transaction_id": data.get("transaction_id", result_file.stem),
                "status": data.get("status", "unknown"),
                "reason": data.get("reason"),
            }
        )
    return {"count": len(results), "results": results}


def summary_text(shared_dir: Path) -> str:
    """Return pipeline-summary.json's raw text, or a friendly fallback.

    pipeline-summary.json lives at shared_dir/results/pipeline-summary.json
    (alongside the per-transaction result envelopes, not directly under
    shared_dir). The fallback is used when no pipeline run has produced a
    summary yet.
    """
    summary_file = shared_dir / "results" / SUMMARY_FILENAME
    if not summary_file.is_file():
        return "No pipeline run yet — run `uv run python integrator.py` first."
    return summary_file.read_text(encoding="utf-8")


@mcp.tool
def get_transaction_status(transaction_id: str) -> dict:
    """Look up a single transaction's settlement status by transaction_id."""
    return load_result(SHARED_DIR / "results", transaction_id)


@mcp.tool
def list_pipeline_results() -> dict:
    """List every processed transaction's status from the latest pipeline run."""
    return summarize(SHARED_DIR / "results")


@mcp.resource("pipeline://summary")
def pipeline_summary() -> str:
    """The latest pipeline run's summary (pipeline-summary.json) as text."""
    return summary_text(SHARED_DIR)


if __name__ == "__main__":
    mcp.run()
