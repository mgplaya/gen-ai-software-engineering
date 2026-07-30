# Codebase Research — expense_splitter (Batch 001)

**Stage**: 1 — Architect (Bug Researcher)
**Inputs**: `context/bugs/001/bug-context.md`, `src/expense_splitter/core.py`, `src/expense_splitter/cli.py`
**Method**: Each bug below was confirmed by opening the file and quoting the real line. Line numbers match the current source.

---

## BUG-1 — Even split loses remainder cents (functional)

1. **Bug ID & Location**: BUG-1 — `src/expense_splitter/core.py:26` (function `split_even`).
2. **Buggy Snippet** (quoted from source, lines 26–27):
   ```python
   share = (total / people).quantize(Decimal("0.01"))
   return [share for _ in range(people)]
   ```
3. **Symptom**: `split_even(Decimal("100.00"), 3)` returns `[Decimal("33.33"), Decimal("33.33"), Decimal("33.33")]`, which sums to `Decimal("99.99")` — one cent short of `100.00`. Running `expense-splitter 100 3` prints `Total: 99.99`.
4. **Root Cause**: The per-person share is computed once as a single independently-rounded value and then repeated `people` times. The remainder cent(s) produced by `total / people` rounding down (`100.00 / 3 = 33.3333… → 33.33`) are never distributed, so money is destroyed by rounding.
5. **Correct Behavior / Invariant**: The returned shares MUST sum exactly to `total` (`sum(split_even(total, people)) == total`). The remainder cents are distributed across people (e.g. `100.00 / 3 → [33.34, 33.33, 33.33]`), and each share is quantized to 2 decimal places. Shares differ by at most one cent.
6. **Material?**: Yes — a fix depends on this claim; the RED test asserts the sum invariant.

---

## BUG-2 — Weighted split uses wrong denominator (functional)

1. **Bug ID & Location**: BUG-2 — `src/expense_splitter/core.py:43` (function `split_weighted`).
2. **Buggy Snippet** (quoted from source, lines 43–44):
   ```python
   denom = len(weights)
   return [(total * w / denom).quantize(Decimal("0.01")) for w in weights]
   ```
3. **Symptom**: `split_weighted(Decimal("90.00"), [1, 2])` returns `[Decimal("45.00"), Decimal("90.00")]` (sum `135.00`) instead of `[Decimal("30.00"), Decimal("60.00")]` (sum `90.00`). The result only equals `total` when every weight is `1`.
4. **Root Cause**: The denominator is `len(weights)` (the number of weights) instead of `sum(weights)` (the total weight). Each share is therefore `total * w / count` rather than `total * w / total_weight`, so proportions and the overall total are wrong for any non-uniform weights.
5. **Correct Behavior / Invariant**: Each share equals `total * weight / sum(weights)`; the shares sum exactly to `total`. For `total=90.00, weights=[1, 2]` the result is `[30.00, 60.00]`.
6. **Material?**: Yes — a fix depends on this claim; the RED test asserts the correct proportional split and the sum invariant.

---

## SEC-1 — `eval()` on CLI input allows code execution (security, CRITICAL)

1. **Bug ID & Location**: SEC-1 — `src/expense_splitter/cli.py:25` (function `parse_amount`).
2. **Buggy Snippet** (quoted from source, line 25):
   ```python
   return Decimal(str(eval(text)))  # noqa: S307 - intentionally vulnerable (seeded)
   ```
3. **Symptom**: The untrusted CLI amount argument is passed to `eval()`, so `expense-splitter "__import__('os').system('echo pwned')" 3` executes arbitrary Python — a code-injection vulnerability. Any attacker-controlled string is run with the process's privileges.
4. **Root Cause**: `eval(text)` evaluates the raw argument as a Python expression before it is wrapped in `Decimal`. Untrusted input is treated as executable code.
5. **Correct Behavior / Invariant**: The amount is parsed safely with no code execution — `Decimal(text.strip())` — and invalid/non-numeric input is rejected via a caught exception (`InvalidOperation`/`ValueError` → controlled "Invalid amount" error, exit code 1). A malicious payload like `"__import__('os').system('echo pwned')"` MUST NOT execute and MUST be rejected. The `eval` execution path is removed entirely.
6. **Material?**: Yes — a fix depends on this claim; the RED test asserts that a code-injection payload does not execute and is rejected.

---

## References (every `file:line` inspected)

- `src/expense_splitter/core.py:14` — `def split_even(total, people)` signature.
- `src/expense_splitter/core.py:20-21` — `people <= 0` guard.
- `src/expense_splitter/core.py:26` — **BUG-1** buggy share computation.
- `src/expense_splitter/core.py:27` — repeated-share return.
- `src/expense_splitter/core.py:30` — `def split_weighted(total, weights)` signature.
- `src/expense_splitter/core.py:35-38` — empty/negative weights guards.
- `src/expense_splitter/core.py:43` — **BUG-2** wrong denominator.
- `src/expense_splitter/core.py:44` — weighted-share return.
- `src/expense_splitter/cli.py:16` — `def parse_amount(text)` signature.
- `src/expense_splitter/cli.py:25` — **SEC-1** `eval()` on untrusted input.
- `src/expense_splitter/cli.py:39-43` — `parse_amount` called; `(ValueError, ArithmeticError)` caught in `main`.
