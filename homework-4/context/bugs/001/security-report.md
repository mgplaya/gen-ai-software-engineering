# Security Report — expense_splitter (Batch 001)

**Stage**: 5 — Security Verifier (final)
**Reviews**: the code produced by the Bug Fixer (Stage 4)
**Inputs read**:
- `context/bugs/001/fix-summary.md`
- `context/bugs/001/implementation-plan.md`
- `src/expense_splitter/cli.py`, `src/expense_splitter/core.py`
**Mode**: report-only — no source or test file was modified.

---

## Scope

Reviewed the implemented files/functions identified in the fix summary, plus all
code reachable from them:

- `src/expense_splitter/cli.py`
  - `parse_amount` (lines 16–27) — the SEC-1 fix site.
  - `main` (lines 30–62) — the CLI entry point and its exception handling, which
    is the trust boundary for all untrusted CLI arguments.
- `src/expense_splitter/core.py`
  - `split_even` (lines 14–27) — BUG-1 fix site.
  - `split_weighted` (lines 30–57) — BUG-2 fix site + remainder-distribution addendum.

Dependencies in scope: standard library only (`decimal`, `sys`, `typing`). No
third-party or network dependencies are imported.

---

## Security Requirement Check

**Requirement** (from `implementation-plan.md` SEC-1): untrusted command-line input
MUST NEVER be executed as code; the `eval()` path in `parse_amount` must be removed so
a payload such as `"__import__('os').system('echo pwned')"` does not execute and is
rejected with a controlled error.

**Verdict: PASS.**

Why:
- `parse_amount` (`cli.py:24-27`) now parses with `Decimal(text.strip())` inside a
  `try/except InvalidOperation`, raising a controlled `ValueError` on bad input. There
  is no `eval`, `exec`, or any dynamic-evaluation call.
- A repository-wide scan of `src/` for `eval`, `exec(`, `os.system`, `subprocess`,
  `shell=True`, `__import__`, and `compile(` returned **no matches** — no
  code-execution sink is reachable from `parse_amount` or anywhere else.
- The controlled-error path is intact: `parse_amount` raises `ValueError`, and
  `main` catches `(ValueError, ArithmeticError)` at `cli.py:43`, printing
  `Invalid amount:` and returning exit code 1. The injection payload is therefore
  rejected, not executed.

> Note: the runtime injection command and `pytest` run could not be re-executed in
> this non-interactive session (Bash approval gating). This verdict rests on direct
> source review and the static scan above, which are conclusive for the code-execution
> requirement. The fix-summary records the full suite at **29 passed, 0 failed**,
> including `test_parse_amount_security_no_code_execution` and
> `test_parse_amount_rejects_os_system_injection`.

---

## Findings

### F1 — Non-finite `Decimal` values reach `split_even` and raise an uncaught `ArithmeticError`
- **Severity**: LOW
- **Location**: `src/expense_splitter/cli.py:25` (accepts value) → `cli.py:53-57`
  (missing catch) via `src/expense_splitter/core.py:24`
- **Description**: `Decimal(text.strip())` accepts the special literals `"Infinity"`,
  `"-Infinity"`, and `"NaN"`, which are not `InvalidOperation` and so pass
  `parse_amount` unchanged. When such a value reaches `split_even`, the call
  `int((total * 100).to_integral_value(...))` raises `InvalidOperation` (a subclass of
  `ArithmeticError`). `main` wraps `split_even` only in `except (ValueError, TypeError)`
  (`cli.py:55`), which does **not** include `ArithmeticError`, so the exception
  propagates uncaught and the CLI crashes with a traceback instead of a clean
  `Invalid input:` message. This is an availability/robustness gap, not a code-execution
  issue — no attacker code runs.
- **Remediation**: reject non-finite input in `parse_amount`, e.g. after parsing add
  `if not value.is_finite(): raise ValueError(f"not a valid amount: {text!r}")`;
  and/or broaden the `split_even` guard in `main` to
  `except (ValueError, TypeError, ArithmeticError)`.

### F2 — Unbounded `people` count allows resource-exhaustion (memory) DoS
- **Severity**: LOW
- **Location**: `src/expense_splitter/cli.py:48` → `src/expense_splitter/core.py:26`
- **Description**: `people = int(people_text)` accepts arbitrarily large integers.
  `split_even` then builds a list of `people` elements
  (`[... for i in range(people)]`, `core.py:26`), so an argument like
  `expense-splitter 100 999999999999` attempts to allocate a list of that length and
  can exhaust memory / hang. For a local single-user CLI this is low impact, but it is
  an unbounded-input-to-allocation path worth noting.
- **Remediation**: enforce a sane upper bound after parsing, e.g.
  `if people > 100_000: raise ValueError("people count too large")`, reported via the
  existing invalid-input path.

### F3 — No injection, hardcoded secrets, or insecure comparisons found (informational)
- **Severity**: INFO
- **Location**: `src/expense_splitter/cli.py`, `src/expense_splitter/core.py`
- **Description**: Checked and confirmed clean:
  - **Injection / code execution**: no `eval`/`exec`/`os.system`/`subprocess`/
    `shell=True`/`__import__`/`compile` (static scan returned no matches).
  - **Hardcoded secrets**: no credentials, API keys, tokens, or passwords present.
  - **Insecure comparisons**: no secret/credential comparison logic exists, so no
    timing-unsafe `==` concern applies.
  - **Input validation**: `split_even` validates `people > 0` (`core.py:20`);
    `split_weighted` validates non-empty (`core.py:35`), non-negative
    (`core.py:37`), and positive weight-sum (`core.py:42`), correctly closing the
    divide-by-zero path that the BUG-2 `sum(weights)` denominator would otherwise open.
  - **Unsafe dependencies**: standard library only.
- **Remediation**: none required.

---

## Summary

| Severity  | Count |
|-----------|-------|
| CRITICAL  | 0     |
| HIGH      | 0     |
| MEDIUM    | 0     |
| LOW       | 2     |
| INFO      | 1     |

**Overall verdict: PASS.** The security-sensitive requirement (SEC-1) is honored — the
`eval()` code-injection sink is fully removed, untrusted CLI input is parsed as data
only, and no code-execution path remains reachable. No CRITICAL/HIGH/MEDIUM issues were
found. The two LOW findings (F1 non-finite `Decimal` crash, F2 unbounded `people`
allocation) are robustness/availability hardening opportunities outside the seeded-bug
scope and do not block sign-off; remediations are provided above for a follow-up.
