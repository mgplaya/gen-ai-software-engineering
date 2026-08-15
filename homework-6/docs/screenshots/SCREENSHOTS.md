# Required Screenshots

This directory is a placeholder — the 5 screenshots below still need to be captured manually and
committed here (as `.png` files with these exact names) before the PR is opened. `.gitkeep` keeps
the empty directory tracked by git in the meantime.

| File | What to capture | Command / action that produces the screen |
|---|---|---|
| `pipeline-run.png` | Full terminal output of a real pipeline run: the per-transaction status table (TXN001–TXN008) and the final `Transactions in / Results / rejected / settled / settled_with_flag` summary counts | `uv run python integrator.py` |
| `test-coverage.png` | The `pytest-cov` terminal report showing per-module coverage and the `TOTAL` line at ≥ 90% (gate is 80%) | `uv run pytest --cov=agents --cov=pipeline --cov=mcp --cov=integrator --cov-report=term-missing -q` |
| `skill-run-pipeline.png` | The `/run-pipeline` slash command executing inside a **restarted** Claude Code session, showing its steps (clear `shared/`, run integrator, summarize results, report rejections) | Restart Claude Code, then type `/run-pipeline` |
| `hook-trigger.png` | The coverage-gate hook firing: one pane/run showing a normal push allowed (exit 0, "coverage gate passed") and one showing a blocked push (exit 2, `BLOCKED: test coverage below 99%` on stderr) | `echo '{"tool_input": {"command": "git push origin homework-6-submission"}}' \| .claude/hooks/coverage-gate.sh` (repeat with `COVERAGE_GATE_MIN=99` exported for the blocked case) |
| `mcp-interaction.png` | Both required MCP interactions in one shot: a context7 query result (library lookup used during code generation) and a call to the custom `pipeline-status` server's `get_transaction_status` tool (e.g. for `TXN001`) | Ask Claude Code to resolve a library via context7, then invoke `get_transaction_status("TXN001")` against the running `mcp/server.py` |
