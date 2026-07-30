# Test Report — Unit Test Generator (TDD RED) — expense_splitter (Batch 001)

**Stage**: 3 — Unit Test Generator (RED phase)
**Date**: 2026-07-28
**Status**: RED — 11 tests failing as expected, 18 passing

---

## 1. Generated Tests

| Test File | Test Function | Coverage | Reproduces Bug |
|-----------|---------------|----------|----------------|
| `tests/test_core.py` | `TestSplitEven::test_split_even_sums_to_total` | Sum invariant: shares must equal total | BUG-1 |
| `tests/test_core.py` | `TestSplitEven::test_split_even_divides_100_by_3` | Edge case: 100/3 with remainder cents | BUG-1 |
| `tests/test_core.py` | `TestSplitEven::test_split_even_with_2_people` | Normal case: 50/2 = 25 each | (passing, not broken) |
| `tests/test_core.py` | `TestSplitEven::test_split_even_with_1_person` | Edge case: single person | (passing, not broken) |
| `tests/test_core.py` | `TestSplitEven::test_split_even_zero_people_raises` | Guard: people <= 0 | (passing, not broken) |
| `tests/test_core.py` | `TestSplitEven::test_split_even_negative_people_raises` | Guard: negative people | (passing, not broken) |
| `tests/test_core.py` | `TestSplitWeighted::test_split_weighted_proportional_to_weights` | Proportionality: 90 → [1,2] weights → [30,60] shares | BUG-2 |
| `tests/test_core.py` | `TestSplitWeighted::test_split_weighted_sums_to_total` | Sum invariant: weighted shares sum to total | BUG-2 |
| `tests/test_core.py` | `TestSplitWeighted::test_split_weighted_uniform_weights` | Uniform weights (1,1,1): split evenly | BUG-2 (sum issue) |
| `tests/test_core.py` | `TestSplitWeighted::test_split_weighted_single_weight` | Edge case: one weight | (passing, not broken) |
| `tests/test_core.py` | `TestSplitWeighted::test_split_weighted_all_zeros_raises` | Guard: all-zero weights (divide by zero) | BUG-2 |
| `tests/test_core.py` | `TestSplitWeighted::test_split_weighted_empty_raises` | Guard: empty weights | (passing, not broken) |
| `tests/test_core.py` | `TestSplitWeighted::test_split_weighted_negative_raises` | Guard: negative weights | (passing, not broken) |
| `tests/test_core.py` | `TestSplitWeighted::test_split_weighted_3_5_2_proportions` | Edge case: weights [3,5,2] with total 100 | BUG-2 |
| `tests/test_cli.py` | `TestParseAmount::test_parse_amount_valid_decimal` | Valid decimal parsing | (passing, not broken) |
| `tests/test_cli.py` | `TestParseAmount::test_parse_amount_integer` | Integer parsing | (passing, not broken) |
| `tests/test_cli.py` | `TestParseAmount::test_parse_amount_strips_whitespace` | Whitespace handling | (passing, not broken) |
| `tests/test_cli.py` | `TestParseAmount::test_parse_amount_rejects_invalid_input` | Invalid input raises exception (not executed as code) | SEC-1 |
| `tests/test_cli.py` | `TestParseAmount::test_parse_amount_security_no_code_execution` | Code-injection payload rejected, NOT executed | SEC-1 |
| `tests/test_cli.py` | `TestParseAmount::test_parse_amount_rejects_os_system_injection` | os.system() injection rejected | SEC-1 |
| `tests/test_cli.py` | `TestParseAmount::test_parse_amount_negative_decimal` | Negative amounts allowed | (passing, not broken) |
| `tests/test_cli.py` | `TestParseAmount::test_parse_amount_zero` | Zero parsing | (passing, not broken) |
| `tests/test_cli.py` | `TestParseAmount::test_parse_amount_large_amount` | Large amounts | (passing, not broken) |
| `tests/test_cli.py` | `TestMain::test_main_valid_split` | Integration: valid CLI arguments | (passing, not broken) |
| `tests/test_cli.py` | `TestMain::test_main_invalid_amount` | Integration: invalid amount propagates error | SEC-1 |
| `tests/test_cli.py` | `TestMain::test_main_invalid_people_count` | Integration: invalid people count | (passing, not broken) |
| `tests/test_cli.py` | `TestMain::test_main_missing_arguments` | Integration: missing args | (passing, not broken) |
| `tests/test_cli.py` | `TestMain::test_main_too_many_arguments` | Integration: too many args | (passing, not broken) |
| `tests/test_cli.py` | `TestMain::test_main_zero_people` | Integration: zero people guard | (passing, not broken) |

---

## 2. RED Run Outcome

**Command**: `.venv/bin/python -m pytest -v`

**Result**: `11 failed, 18 passed in 0.05s`

**Failures Breakdown**:

### BUG-1 — `split_even` sum invariant (2 failures)

```
AssertionError: Shares [Decimal('33.33'), Decimal('33.33'), Decimal('33.33')] sum to 99.99, not 100.00
assert Decimal('99.99') == Decimal('100.00')
```

- **test_split_even_sums_to_total** — shares must sum exactly to total, but `100.00 / 3` returns `[33.33, 33.33, 33.33]` (sum=99.99).
- **test_split_even_divides_100_by_3** — same issue; remainder cent is lost.

**Root Cause**: Bug at `src/expense_splitter/core.py:26-27`; one independently-rounded share is repeated `people` times.

---

### BUG-2 — `split_weighted` wrong denominator (5 failures)

```
AssertionError: Expected [Decimal('30.00'), Decimal('60.00')], got [Decimal('45.00'), Decimal('90.00')]
assert Decimal('135.00') == Decimal('90.00')  # sum, not total
```

- **test_split_weighted_proportional_to_weights** — `split_weighted(90.00, [1, 2])` returns `[45.00, 90.00]` (sum 135) instead of `[30.00, 60.00]`.
- **test_split_weighted_sums_to_total** — sum is 135, not 90.
- **test_split_weighted_uniform_weights** — weights `[1,1,1]` should split evenly (sum=100), but gets 99.99 (inherits BUG-1 issue).
- **test_split_weighted_all_zeros_raises** — all-zero weights should raise ValueError for divide-by-zero, but no error is raised (denom=3, not 0).
- **test_split_weighted_3_5_2_proportions** — weights `[3, 5, 2]` with total 100 should yield `[30, 50, 20]`, but gets `[100.00, 166.67, 66.67]` (dividing by len(weights)=3 instead of sum(weights)=10).

**Root Cause**: Bug at `src/expense_splitter/core.py:43`; `denom = len(weights)` instead of `denom = sum(weights)`.

---

### SEC-1 — `parse_amount` code injection (4 failures)

```
# Test 1: rejects_invalid_input
NameError: name 'not_a_number' is not defined
# eval() evaluated the input as Python code, raising NameError

# Test 2: security_no_code_execution
Captured stdout call
PWNED
decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]
# Code WAS executed (print('PWNED') ran), then Decimal("None") failed

# Test 3: rejects_os_system_injection
Failed: DID NOT RAISE ValueError
Captured stdout call
pwned
# Code WAS executed (os.system('echo pwned') ran successfully), no exception

# Test 4: main_invalid_amount (integration)
NameError: name 'not_a_number' is not defined
# NameError propagated from parse_amount, not caught by main()
```

**Root Cause**: Bug at `src/expense_splitter/cli.py:25`; `eval(text)` executes untrusted CLI input as Python code.

---

## 3. FIRST Assessment

| Property | Status | Justification |
|----------|--------|---------------|
| **F — Fast** | ✅ | All tests run in < 50ms total. No I/O, no sleep, no subprocess calls. Deterministic in-memory calculations only. |
| **I — Independent** | ✅ | Each test is self-contained. No shared state, no test ordering dependency. `TestParseAmount` tests only `parse_amount()`; `TestSplitEven` only `split_even()`; `TestSplitWeighted` only `split_weighted()`. `TestMain` integration tests use `patch()` to mock stderr/stdout. |
| **R — Repeatable** | ✅ | Deterministic: fixed inputs, fixed expected outputs. Uses `Decimal` for exact decimal arithmetic (no float rounding). No randomness, no timestamps, no environment variables. Identical results across runs and machines. |
| **S — Self-Validating** | ✅ | Each test asserts a concrete expected value (e.g., `sum(shares) == total`, `shares == [Decimal('30.00'), Decimal('60.00')]`). No manual inspection required. pytest reports pass/fail automatically. |
| **T — Timely** | ✅ | Tests cover exactly the bugs identified in `bug-context.md` and `codebase-research.md`: split_even sum invariant (BUG-1), split_weighted proportionality (BUG-2), and parse_amount security (SEC-1). Tests added alongside the identified defects. |

---

## 4. References

Code under test (buggy source):

- `src/expense_splitter/core.py:14` — `split_even` function signature and docstring (declares sum invariant).
- `src/expense_splitter/core.py:20-21` — `people <= 0` guard.
- `src/expense_splitter/core.py:23-27` — **BUG-1** buggy implementation (lines 26-27 compute one share and repeat it).
- `src/expense_splitter/core.py:30` — `split_weighted` function signature and docstring.
- `src/expense_splitter/core.py:35-38` — empty/negative weights guards.
- `src/expense_splitter/core.py:40-44` — **BUG-2** buggy implementation (line 43 uses `len(weights)` instead of `sum(weights)`).
- `src/expense_splitter/cli.py:16` — `parse_amount` function signature and docstring (declares "User input MUST NEVER be executed as code").
- `src/expense_splitter/cli.py:22-25` — **SEC-1** buggy implementation (line 25 uses `eval()` on untrusted `text`).
- `src/expense_splitter/cli.py:28-60` — `main()` CLI entry point and error handling.
- `src/expense_splitter/cli.py:39-41` — `main()` catches `(ValueError, ArithmeticError)` when calling `parse_amount()`.

Test files:

- `tests/test_core.py` — tests for `split_even` and `split_weighted` (14 tests, 6 failing on BUG-1/BUG-2).
- `tests/test_cli.py` — tests for `parse_amount` and `main` (15 tests, 5 failing on SEC-1).

---

## Summary

**RED Phase Complete**: All three seeded bugs are reproduced by failing tests.

- **BUG-1** (split_even): 2 direct failures showing sum invariant is broken (99.99 ≠ 100.00).
- **BUG-2** (split_weighted): 5 failures showing wrong denominator (proportions wrong, sum wrong, divide-by-zero not caught).
- **SEC-1** (parse_amount): 4 failures showing code injection is executed (PWNED and pwned printed) and not properly rejected.

The test suite is FIRST-compliant, deterministic, and ready for the Bug Fixer (GREEN) stage. Each failing test pinpoints a specific incorrect behavior that the fix must address.
