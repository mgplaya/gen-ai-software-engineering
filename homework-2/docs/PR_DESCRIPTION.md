# PR: Homework 2 — Intelligent Customer Support System

> Draft PR body. Paste into the GitHub PR, embed the screenshots where marked, then delete this note.

## ✅ Summary of what was implemented

A **Customer Support ticket API** (NestJS 11 + TypeScript 5.7, in-memory storage) covering all five tasks of `homework-2/TASKS.md`:

- **Task 1 — Multi-format import API.** Full CRUD (`POST/GET/PUT/DELETE /tickets`, filtering by category/priority/status/customer/assignee/tag) plus `POST /tickets/import` — multipart upload of **CSV, JSON or XML** (format resolved from `?format=` → file extension → MIME type). Every row is re-validated with the same `CreateTicketDto` used by `POST /tickets`; a bad row never aborts the batch. The summary reports `{total, successful, failed, ticketIds, errors[{index, message}]}`. Malformed files → 400 with a human-readable message. Status codes: 201/200/204/400/404.
- **Task 2 — Auto-classification.** `POST /tickets/:id/auto-classify` + optional `autoClassify` flag on create/import. Deterministic keyword engine with **word-boundary matching** (`bug` never matches inside `debug`), ordered precedence tables (`bug_report` before `technical_issue`), confidence score (grows with keyword hits, 0.4 when nothing matches), human-readable reasoning, matched-keywords list, in-memory **decision log**, and `manual_override` tracking when a human changes the classified category/priority.
- **Task 3 — Test suite.** **56 tests in 8 suites**, written **before the implementation** (pure TDD): red run `54 failed / 2 passed` → green `56/56`. Coverage (enforced ≥85% in jest.config): **statements 97% · branches 87.8% · functions 100% · lines 99.3%**.
- **Task 4 — Multi-level docs by different AI models**: `docs/API_REFERENCE.md` (**Claude Haiku**), `docs/TESTING_GUIDE.md` (**Claude Sonnet**), `docs/ARCHITECTURE.md` (**Claude Opus**, 3 Mermaid diagrams), `README.md` + `HOWTORUN.md` (**Claude Fable 5**). 5 Mermaid diagrams total.
- **Task 5 — Integration & performance tests**: full lifecycle, bulk import + classification verification, 25 concurrent requests, combined category+priority filtering, 5 benchmark tests with CI-safe thresholds.
- **Sample data**: `tests/fixtures/` — 50 CSV / 20 JSON / 30 XML valid tickets seeded with classification keywords, plus `invalid_*` (per-row validation failures) and `malformed.*` (parser failures) for negative tests.

## 🛠️ AI tools & workflow (multi-agent pipeline)

Everything was built by a **Claude Code agent pipeline** orchestrated from one session (Fable 5):

1. **Explore + Plan agents** — repo recon, implementation design, user-approved plan.
2. Main session — cleanup of a broken previous attempt, scaffolding, TDD stub skeleton, fixtures.
3. **3 parallel test-writer agents** — each received a precise test spec and wrote its share of the 56 tests against stubs (red phase). The intermediate red run captured mid-iteration — one agent's 21 tests failing against the stubs (19 failed / 2 passed) — shows the red→green loop as it actually happened: 📸 `docs/screenshots/tdd-red-run.png`
4. Main session — implementation module by module until green (56/56). 📸 `docs/screenshots/tdd_green_run.png`
5. Coverage gate `npm run test:cov` ≥85%. 📸 *screenshot below*
6. **3 doc agents with different models** (Haiku/Sonnet/Opus) — Task 4's "different AI models per doc type" requirement.
7. **/code-review skill** — 4 parallel finder agents (line-by-line, cross-file tracer, reuse/simplification, efficiency/altitude) surfaced 8 confirmed findings, **all fixed**: null-body crashes in PUT (`metadata: null`, `tags: null`), `closed` erasing `resolved_at`, falsy values swallowed on import, substring false-positives in classification (→ word-boundary regexes), duplicated validation-error flattening, per-call XMLParser construction, SIGPIPE in the demo script. Tests stayed green after every fix.
8. Live smoke test: server boot + `demo/sample-requests.sh` walking all 7 endpoints end-to-end.

What I verified myself: red/green/coverage runs, the live demo output, review fixes, and final docs proofreading.

## ⚠️ Challenges & how they were addressed

- **Lost previous attempt**: `homework-2` contained only compiled JS from an earlier try (sources gone, source maps without `sourcesContent`). Rebuilt from scratch; the old structure served as a design reference only.
- **Concurrent supertest ECONNRESET**: concurrent requests against a non-listening Nest app race on `listen()`. Fixed by `await app.listen(0)` (ephemeral port) in concurrent suites.
- **Branch coverage below threshold** after green (81% < 85%): strengthened existing tests (nested validation errors, metadata update, manual override, no-file import, unsupported format, empty-tags fixtures) without changing the required 56-test structure → 87.8%.
- **Review findings** (see pipeline step 7) — real bugs found by adversarial finder agents in code that was already 100% green, a good illustration of why tests alone aren't enough.

## ▶️ How to run & verify

```bash
cd homework-2
npm install
npm test                # 56/56 green
npm run test:cov        # coverage ≥85% enforced
./demo/run.sh           # build + start on :3000
./demo/sample-requests.sh   # in a second terminal: full endpoint walkthrough
```

Docs: [README.md](../README.md) · [HOWTORUN.md](../HOWTORUN.md) · [API_REFERENCE.md](API_REFERENCE.md) · [ARCHITECTURE.md](ARCHITECTURE.md) · [TESTING_GUIDE.md](TESTING_GUIDE.md)

## 📸 Screenshots

All screenshots live in [`homework-2/docs/screenshots/`](screenshots/):

| What | File |
|------|------|
| **Coverage report** — all 4 metrics >85% (required deliverable) | [`test_coverage.png`](screenshots/test_coverage.png) |
| **TDD green run** — 56/56 passed, 8/8 suites | [`tdd_green_run.png`](screenshots/tdd_green_run.png) |
| **TDD red run (mid-iteration)** — a test-writer agent's suites failing against the stubs before any implementation existed (19 failed / 2 passed / 21); direct evidence of the red→green TDD iteration | [`tdd-red-run.png`](screenshots/tdd-red-run.png) |
| AI planning — approved plan: context, cleanup of the broken previous attempt | [`plan-approved-context.png`](screenshots/plan-approved-context.png) |
| AI planning — approved plan: execution order, verification, risks | [`plan-approved-execution-order.png`](screenshots/plan-approved-execution-order.png) |
| AI planning — final plan with user decisions (TS keyword engine, pure TDD) | [`plan-final-user-decisions.png`](screenshots/plan-final-user-decisions.png) |
| **Agent pipeline table** — who → does what (3 test-writers, 3 doc models, /code-review) | [`plan-agent-pipeline-table.png`](screenshots/plan-agent-pipeline-table.png) |
| Pipeline completion report — TDD stats, review findings, smoke test | [`pipeline-final-summary.png`](screenshots/pipeline-final-summary.png) |

> ⚠️ When pasting this text into the GitHub PR body, **drag-and-drop the key images** (coverage, green run, red run, pipeline table) directly into the PR editor — relative repo paths don't render in PR descriptions. The table above then serves as the index of the committed files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
