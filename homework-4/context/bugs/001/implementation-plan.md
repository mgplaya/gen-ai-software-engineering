# Implementation Plan — expense_splitter (Batch 001)

**Stage**: 1 — Architect (Bug Planner)
**Companion**: `context/bugs/001/research/codebase-research.md`
**Gate**: A human MUST verify this plan before any code is changed.

## Test command

```
.venv/bin/python -m pytest
```

Run from the repo root (`homework-4/`). The Unit Test Generator's RED tests must
fail against the current seeded source; after the Bug Fixer applies the Before→After
edits below, every test must pass (GREEN) with the tests unchanged.

---

## Per-Bug Fix

### BUG-1 — `src/expense_splitter/core.py` (`split_even`)

**Before** (lines 23–27, exact):
```python
    # BUG-1: every share is the same independently-rounded value, so the shares
    # do NOT sum back to ``total`` when the split is not exact
    # (e.g. 100.00 / 3 -> 33.33 * 3 = 99.99, one cent lost).
    share = (total / people).quantize(Decimal("0.01"))
    return [share for _ in range(people)]
```

**After**:
```python
    # Distribute the remainder cents so the shares sum back to ``total`` exactly.
    cents = int((total * 100).to_integral_value(rounding=ROUND_HALF_UP))
    base, extra = divmod(cents, people)
    shares = [base + (1 if i < extra else 0) for i in range(people)]
    return [(Decimal(c) / 100).quantize(Decimal("0.01")) for c in shares]
```

**Also add the import** at the top of `src/expense_splitter/core.py`:

**Before** (line 10):
```python
from decimal import Decimal
```
**After**:
```python
from decimal import ROUND_HALF_UP, Decimal
```

**Invariant restored**: `sum(split_even(total, people)) == total`; remainder cents
are distributed across the first `extra` people; each share is quantized to
2 decimals and shares differ by at most one cent.

---

### BUG-2 — `src/expense_splitter/core.py` (`split_weighted`)

**Before** (lines 40–44, exact):
```python
    # BUG-2: the denominator is len(weights) instead of sum(weights); the shares
    # are only correct when every weight is 1. For any other weights the
    # proportions are wrong (e.g. total=90, weights=[1, 2] -> [45, 90]).
    denom = len(weights)
    return [(total * w / denom).quantize(Decimal("0.01")) for w in weights]
```

**After**:
```python
    # Denominator is the total weight so shares are proportional to the weights.
    denom = sum(weights)
    if denom == 0:
        raise ValueError("weights must sum to a positive value")
    return [(total * w / denom).quantize(Decimal("0.01")) for w in weights]
```

**Invariant restored**: each share equals `total * weight / sum(weights)`;
`split_weighted(Decimal("90.00"), [1, 2]) == [Decimal("30.00"), Decimal("60.00")]`.
(The `denom == 0` guard handles all-zero weights, which the existing
non-negative-weights check alone would let divide by zero.)

---

### SEC-1 — `src/expense_splitter/cli.py` (`parse_amount`)

**Before** (lines 22–25, exact):
```python
    # SEC-1: eval() runs arbitrary attacker-controlled Python from a CLI arg,
    # e.g. `expense-splitter "__import__('os').system('rm -rf ~')" 3`.
    # This is a critical code-injection vulnerability.
    return Decimal(str(eval(text)))  # noqa: S307 - intentionally vulnerable (seeded)
```

**After**:
```python
    # Parse the amount safely: never execute user input as code. Non-numeric
    # input raises InvalidOperation, which main() reports as an invalid amount.
    try:
        return Decimal(text.strip())
    except InvalidOperation as exc:
        raise ValueError(f"not a valid amount: {text!r}") from exc
```

**Also add the import** in `src/expense_splitter/cli.py`:

**Before** (line 10):
```python
from decimal import Decimal
```
**After**:
```python
from decimal import Decimal, InvalidOperation
```

**Invariant restored**: no `eval`/code execution path remains; a malicious payload
such as `"__import__('os').system('echo pwned')"` does not execute and is rejected
with a controlled error (`ValueError` → `main` prints `Invalid amount:` and returns
exit code 1, since `main` already catches `(ValueError, ArithmeticError)` at
`cli.py:41`).

---

## Build Sequence (downstream stages)

1. **Bug Research Verifier** — reads `research/codebase-research.md` and confirms
   each bug (BUG-1, BUG-2, SEC-1) exists at the stated `file:line` in the current
   source, and that each "correct behavior / invariant" is testable. Produces a
   verification note approving (or rejecting) the research.
2. **Unit Test Generator (RED)** — writes failing tests under `tests/` that
   reproduce each defect against the stated invariants: `split_even` sum-to-total,
   `split_weighted` proportional split, and a `parse_amount` code-injection test
   asserting a payload does not execute and is rejected. These tests MUST fail on
   the current seeded code. Produces the RED test suite.
3. **Bug Fixer (GREEN)** — applies exactly the Before→After edits above to
   `src/expense_splitter/core.py` and `src/expense_splitter/cli.py` (including the
   two import changes), turning the RED tests GREEN without weakening any test.
   Produces the fixed source.
4. **Security Verifier** — confirms untrusted input is no longer executed (no
   `eval`/`exec` reachable from `parse_amount`), that the injection test passes, and
   that the full suite (`.venv/bin/python -m pytest`) is GREEN. Produces the final
   security sign-off.
