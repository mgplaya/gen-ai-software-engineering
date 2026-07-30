# Verified Research — expense_splitter (Batch 001)

**Stage**: 2 — Bug Research Verifier
**Verifies**: `context/bugs/001/research/codebase-research.md`
**Against**: `src/expense_splitter/core.py`, `src/expense_splitter/cli.py`
**Coverage checked against**: `context/bugs/001/bug-context.md`
**Method**: Every referenced `file:line` was opened in the actual seeded source and
each quoted snippet and stated root cause was compared to the code. Read-only.

---

## 1. Verification Summary

`PASS` — Research Quality **A (Verified)**.

All three seeded defects (BUG-1, BUG-2, SEC-1) are researched, every `file:line`
reference resolves, every quoted buggy snippet matches the source (whitespace-
insensitive), and every root cause is consistent with the code.

---

## 2. Verified Claims

| Claim | `file:line` | Result | Note |
|-------|-------------|--------|------|
| BUG-1 location — `split_even` buggy share computation | `src/expense_splitter/core.py:26` | match | `share = (total / people).quantize(Decimal("0.01"))` — exact. |
| BUG-1 snippet — repeated-share return | `src/expense_splitter/core.py:27` | match | `return [share for _ in range(people)]` — exact. |
| BUG-1 root cause — one independently-rounded share repeated, remainder cents dropped | `src/expense_splitter/core.py:26-27` | match | `100.00/3 → 33.33`, ×3 = `99.99`; sum invariant broken. Confirmed by code + inline comment lines 23–25. |
| BUG-2 location — wrong denominator | `src/expense_splitter/core.py:43` | match | `denom = len(weights)` — exact. |
| BUG-2 snippet — weighted-share return | `src/expense_splitter/core.py:44` | match | `return [(total * w / denom).quantize(Decimal("0.01")) for w in weights]` — exact. |
| BUG-2 root cause — `len(weights)` used instead of `sum(weights)`; correct only when all weights `1` | `src/expense_splitter/core.py:43-44` | match | `total=90.00, weights=[1,2] → [45.00, 90.00]` (sum 135) confirmed; should be `[30.00, 60.00]`. |
| SEC-1 location — `eval()` on untrusted CLI input | `src/expense_splitter/cli.py:25` | match | `return Decimal(str(eval(text)))  # noqa: S307 - intentionally vulnerable (seeded)` — exact. |
| SEC-1 root cause — raw arg evaluated as Python before wrapping in `Decimal` | `src/expense_splitter/cli.py:25` | match | `parse_amount` (line 16) returns `eval(text)` on untrusted `text`; code-injection path confirmed. |
| SEC-1 fix path context — `parse_amount` called; `(ValueError, ArithmeticError)` caught in `main` | `src/expense_splitter/cli.py:39-43` | match | Call at line 40; `except (ValueError, ArithmeticError)` at line 41 → "Invalid amount", `return 1`. |
| Ref — `split_even` signature | `src/expense_splitter/core.py:14` | match | `def split_even(total: Decimal, people: int) -> List[Decimal]:` (research drops type hints — paraphrase, non-material). |
| Ref — `people <= 0` guard | `src/expense_splitter/core.py:20-21` | match | `if people <= 0: raise ValueError("people must be positive")`. |
| Ref — `split_weighted` signature | `src/expense_splitter/core.py:30` | match | `def split_weighted(total: Decimal, weights: List[int]) -> List[Decimal]:` (paraphrased, non-material). |
| Ref — empty/negative weights guards | `src/expense_splitter/core.py:35-38` | match | `if not weights` (35–36); `if any(w < 0 …)` (37–38). |
| Ref — `parse_amount` signature | `src/expense_splitter/cli.py:16` | match | `def parse_amount(text: str) -> Decimal:` (paraphrased, non-material). |

---

## 3. Discrepancies Found

- **Function-signature references are paraphrased.** The research writes signatures
  without type annotations (e.g. `def split_even(total, people)`), while the source
  carries full type hints (`def split_even(total: Decimal, people: int) -> List[Decimal]:`).
  These appear only in the References list, not as quoted buggy snippets. **Non-material** —
  no fix depends on the annotation text, and the function name and location are correct.

No other discrepancies. Every quoted buggy snippet (the material ones a fix depends
on) matches the source byte-for-byte, whitespace aside.

---

## 4. Research Quality Assessment

**Level A — Verified.**

Applying the decision rule top to bottom: there is research content (not D); no
material claim is wrong or unverifiable — all three buggy `file:line` references
(`core.py:26`, `core.py:43`, `cli.py:25`) resolve and their snippets match the source
exactly, and each root cause is consistent with the code (so not C); the only
discrepancy is paraphrased function signatures in the reference list, which are
non-material. Per rule 4, everything material checks out exactly, so the rating is A.
Coverage is complete: BUG-1, BUG-2, and SEC-1 from `bug-context.md` are all researched
with correct locations, symptoms, and invariants.

---

## 5. References (exact `file:line` locations checked)

- `src/expense_splitter/core.py:14` — `split_even` signature.
- `src/expense_splitter/core.py:20-21` — `people <= 0` guard.
- `src/expense_splitter/core.py:26` — **BUG-1** buggy share computation.
- `src/expense_splitter/core.py:27` — repeated-share return.
- `src/expense_splitter/core.py:30` — `split_weighted` signature.
- `src/expense_splitter/core.py:35-38` — empty/negative weights guards.
- `src/expense_splitter/core.py:43` — **BUG-2** wrong denominator.
- `src/expense_splitter/core.py:44` — weighted-share return.
- `src/expense_splitter/cli.py:16` — `parse_amount` signature.
- `src/expense_splitter/cli.py:25` — **SEC-1** `eval()` on untrusted input.
- `src/expense_splitter/cli.py:39-43` — `parse_amount` call and `(ValueError, ArithmeticError)` handling in `main`.
