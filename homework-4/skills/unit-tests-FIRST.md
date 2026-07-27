# Skill: Unit Tests — FIRST

**ID**: `unit-tests-FIRST`
**Used by**: `agents/unit-test-generator.agent.md` (Stage 4)
**Purpose**: Define the quality bar every generated unit test must meet, and require
the Test Generator to self-assess against it in `test-report.md`.

---

## The FIRST properties

Every generated test MUST satisfy all five FIRST properties:

- **F — Fast**: Tests run in milliseconds. No sleeps, no network, no disk I/O, no
  spawning processes. A developer must be willing to run them on every save.
- **I — Independent**: Tests do not depend on each other or on execution order.
  Each test sets up its own inputs and shares no mutable state. Running a single
  test in isolation gives the same result as running the whole file.
- **R — Repeatable**: Deterministic. Same result on every run and on any machine.
  No reliance on current time, randomness, locale, or environment. Use fixed inputs
  and `pytest.approx`/`math.isclose` for float comparisons rather than `==`.
- **S — Self-validating**: Each test asserts a concrete expected value and passes or
  fails on its own. No manual inspection of printed output, no "eyeball the log".
- **T — Timely**: Tests target the code that just changed (per `fix-summary.md`),
  written alongside the fix — not months later and not for unrelated code.

## Scope rule

Generate tests ONLY for new or changed behavior listed in `fix-summary.md`. Do not
add tests for untouched functions. If a fix changed a function's contract, cover:

- the previously-broken case (now correct),
- at least one boundary/edge case,
- and, for a security fix, a test proving the unsafe behavior is gone (e.g. that a
  malicious input is rejected rather than executed).

## Required result-file sections

`test-report.md` MUST contain, in this order:

1. **Generated Tests** — table: test file, test function, what it covers, which
   fix (BUG-1 / BUG-2 / SEC-1) it protects.
2. **Run Outcome** — the exact test command, pass/fail counts, and confirmation the
   suite was run twice with identical results (Repeatable evidence).
3. **FIRST Assessment** — one row per property (F/I/R/S/T) with a ✅/⚠️ and a short
   justification for these specific tests.
4. **References** — `file:line` of the code under test.

## Anti-patterns to avoid

- Asserting on `print` output instead of return values.
- `assert result == 0.1 + 0.2` style exact float equality → use `approx`.
- Tests that pass only because they run after another test mutated shared state.
- Testing the framework or stdlib instead of the changed code.
- A single giant test that exercises everything (hard to diagnose on failure).
