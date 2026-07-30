# Fix Summary — expense_splitter (Batch 001)

**Stage**: 4 — Bug Fixer (GREEN phase)
**Applies**: `context/bugs/001/implementation-plan.md`
**Verified research**: `context/bugs/001/research/verified-research.md` — `PASS`, Quality A
**RED baseline**: `context/bugs/001/test-report.md` — `11 failed, 18 passed`

---

## 1. Changes Made

### BUG-1 — `src/expense_splitter/core.py` (`split_even`)

- **Import** (`core.py:10`): `from decimal import Decimal` → `from decimal import ROUND_HALF_UP, Decimal`.
- **`split_even` body** (was `core.py:26-27`, now `core.py:23-27`):

  Before:
  ```python
  share = (total / people).quantize(Decimal("0.01"))
  return [share for _ in range(people)]
  ```

  After:
  ```python
  cents = int((total * 100).to_integral_value(rounding=ROUND_HALF_UP))
  base, extra = divmod(cents, people)
  shares = [base + (1 if i < extra else 0) for i in range(people)]
  return [(Decimal(c) / 100).quantize(Decimal("0.01")) for c in shares]
  ```

  Applied exactly as specified in the implementation plan.

- **Test result after this change**: `test_split_even_sums_to_total` and
  `test_split_even_divides_100_by_3` now pass (verified via targeted
  `pytest tests/test_core.py::TestSplitEven -v` run, all 6 green).

### BUG-2 — `src/expense_splitter/core.py` (`split_weighted`)

- **Denominator fix** (was `core.py:43`, now `core.py:41-43`), applied exactly per
  the plan:

  Before:
  ```python
  denom = len(weights)
  return [(total * w / denom).quantize(Decimal("0.01")) for w in weights]
  ```

  After (denominator + zero-guard):
  ```python
  denom = sum(weights)
  if denom == 0:
      raise ValueError("weights must sum to a positive value")
  ```

- **Plan-completion addendum (not literal plan text)**: after applying the
  literal plan edit, `pytest` still failed
  `test_split_weighted_uniform_weights` (`split_weighted(Decimal("100.00"),
  [1, 1, 1])` summed to `99.99`, not `100.00`) — the plan's denominator fix
  alone leaves the *same* independently-rounded-share defect as BUG-1 present
  in `split_weighted` whenever `total_cents` doesn't divide evenly by
  `sum(weights)`. This is not a contradiction between the test and the plan
  (the plan's own invariant for `split_weighted` requires proportional,
  summing shares); it is the plan's fix being incomplete for this one case.
  Per the GREEN rule to implement the smallest change that turns RED into
  GREEN, I extended `split_weighted` with the same remainder-distribution
  technique used for `split_even` (largest-remainder method in integer
  cents), added directly after the plan's denominator fix:

  ```python
  total_cents = int((total * 100).to_integral_value(rounding=ROUND_HALF_UP))
  numerators = [total_cents * w for w in weights]
  base = [n // denom for n in numerators]
  remainders = [n % denom for n in numerators]
  leftover = total_cents - sum(base)
  order = sorted(range(len(weights)), key=lambda i: remainders[i], reverse=True)
  shares_cents = list(base)
  for i in order[:leftover]:
      shares_cents[i] += 1
  return [(Decimal(c) / 100).quantize(Decimal("0.01")) for c in shares_cents]
  ```

  This does not change any exact-division test outcome: `[1, 2]` on
  `90.00` and `[3, 5, 2]` on `100.00` both divide evenly (leftover cents = 0),
  so the plan's stated expected outputs (`[30.00, 60.00]` and
  `[30.00, 50.00, 20.00]`) are unaffected and still hold exactly.

- **Test result after this change**: full `TestSplitWeighted` class green (8/8),
  including `test_split_weighted_proportional_to_weights`,
  `test_split_weighted_sums_to_total`, `test_split_weighted_uniform_weights`,
  `test_split_weighted_all_zeros_raises`, and `test_split_weighted_3_5_2_proportions`.

### SEC-1 — `src/expense_splitter/cli.py` (`parse_amount`)

- **Import** (`cli.py:10`): `from decimal import Decimal` → `from decimal import Decimal, InvalidOperation`.
- **`parse_amount` body** (was `cli.py:22-25`), applied exactly per the plan:

  Before:
  ```python
  return Decimal(str(eval(text)))  # noqa: S307 - intentionally vulnerable (seeded)
  ```

  After:
  ```python
  try:
      return Decimal(text.strip())
  except InvalidOperation as exc:
      raise ValueError(f"not a valid amount: {text!r}") from exc
  ```

- **Test result after this change**: all of `TestParseAmount` (9/9) and
  `TestMain` (6/6) pass, including
  `test_parse_amount_security_no_code_execution`,
  `test_parse_amount_rejects_os_system_injection`, and
  `test_main_invalid_amount`.

---

## 2. Test Result

- **RED baseline** (Stage 3): `11 failed, 18 passed`.
- **GREEN — final run**:

  ```
  $ .venv/bin/python -m pytest -v
  tests/test_cli.py ...............                                        [ 51%]
  tests/test_core.py ..............                                        [100%]
  ============================== 29 passed in 0.02s ==============================
  ```

  **29 passed, 0 failed.**

---

## 3. Overall Status

**GREEN**

---

## 4. Manual Verification

Run the full suite:
```
.venv/bin/python -m pytest -v
```

Confirm no `eval`/`exec` remains reachable from `parse_amount`:
```
grep -rn "eval\|exec(" src/expense_splitter/
# (no output — clean)
```

Confirm the injection payload from `verified-research.md` is rejected, not executed:
```
cd src && ../.venv/bin/python -m expense_splitter.cli "__import__('os').system('echo pwned')" 3; echo "exit=$?"
# Invalid amount: not a valid amount: "__import__('os').system('echo pwned')"
# exit=1
# (no "pwned" printed — confirms no code execution)
```

Confirm `split_even` and `split_weighted` sum invariants:
```
.venv/bin/python -c "
from decimal import Decimal
from expense_splitter.core import split_even, split_weighted
print(split_even(Decimal('100.00'), 3), sum(split_even(Decimal('100.00'), 3)))
print(split_weighted(Decimal('90.00'), [1, 2]))
print(split_weighted(Decimal('100.00'), [1, 1, 1]), sum(split_weighted(Decimal('100.00'), [1, 1, 1])))
"
```

---

## 5. References

- `context/bugs/001/implementation-plan.md` — plan applied (BUG-1, BUG-2, SEC-1).
- `context/bugs/001/research/verified-research.md` — `PASS`, Quality A, confirms
  buggy `file:line` locations prior to these edits.
- `context/bugs/001/test-report.md` — RED baseline (11 failed, 18 passed) and the
  test-author's own note that `test_split_weighted_uniform_weights` "inherits
  BUG-1 issue," consistent with the plan-completion addendum above.
- `src/expense_splitter/core.py` — `split_even` (BUG-1 fix), `split_weighted`
  (BUG-2 fix + remainder-distribution addendum).
- `src/expense_splitter/cli.py` — `parse_amount` (SEC-1 fix).
- `tests/test_core.py`, `tests/test_cli.py` — unchanged; all 29 tests pass.
