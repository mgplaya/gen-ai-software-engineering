# Bug Context — expense_splitter (Batch 001)

**From**: Product owner (human seed input) · **To**: Architect (stage 1)

The `expense_splitter` sample app ships with **2 intentional functional bugs** and
**1 intentional security vulnerability**, seeded in real code (not stubs). The
pipeline's job is to expose them with **failing TDD tests (RED)** and then **fix**
them (GREEN), keeping the tests unchanged.

## App under test

- `src/expense_splitter/core.py` — `split_even`, `split_weighted`
- `src/expense_splitter/cli.py` — `parse_amount`, `main`
- Money is `decimal.Decimal` with 2 fractional digits.

## BUG-1 — Even split loses remainder cents (functional)

- **Type**: Functional / correctness
- **Location**: `src/expense_splitter/core.py:26` (`split_even`)
- **Symptom**: `split_even(Decimal("100.00"), 3)` returns `[33.33, 33.33, 33.33]`
  which sums to `99.99`, not `100.00`. Running `expense-splitter 100 3` prints
  `Total: 99.99`.
- **Root cause**: every share is the same independently-rounded value, so the
  remainder cent(s) are dropped.
- **Expected**: the shares MUST sum exactly to `total`; the remainder cent(s) are
  distributed across people.

## BUG-2 — Weighted split uses wrong denominator (functional)

- **Type**: Functional / correctness
- **Location**: `src/expense_splitter/core.py:43` (`split_weighted`)
- **Symptom**: `split_weighted(Decimal("90.00"), [1, 2])` returns `[45.00, 90.00]`
  (sum 135) instead of `[30.00, 60.00]` (sum 90).
- **Root cause**: the denominator is `len(weights)` instead of `sum(weights)`.
- **Expected**: each share equals `total * weight / sum(weights)`.

## SEC-1 — `eval()` on CLI input allows code execution (security)

- **Type**: Security / code injection (CRITICAL)
- **Location**: `src/expense_splitter/cli.py:25` (`parse_amount`)
- **Symptom**: the amount argument is passed to `eval()`, so
  `expense-splitter "__import__('os').system('echo pwned')" 3` executes arbitrary
  code.
- **Root cause**: `return Decimal(str(eval(text)))` evaluates untrusted user input
  as Python.
- **Expected**: parse the amount safely (e.g. `Decimal(text)` with validation);
  reject non-numeric input with a controlled error, never executing it.

## Definition of done

- Failing TDD tests reproduce all three defects (RED) before any fix.
- The fixes make every test pass (GREEN); the tests are not weakened.
- A security review confirms untrusted input is no longer executed.
