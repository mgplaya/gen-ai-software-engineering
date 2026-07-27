# Skill: TDD Red-Green Discipline

**ID**: `tdd-red-green`
**Used by**: `agents/unit-test-generator.agent.md` (RED) and
`agents/bug-fixer.agent.md` (GREEN)
**Purpose**: Enforce the test-driven discipline across the two agents that share it,
so tests are genuinely written first and drive the implementation.

---

## The cycle

```
RED  →  GREEN  →  (REFACTOR)
```

- **RED** (Unit Test Generator): write a failing test that encodes a piece of the
  designed contract. It MUST fail now, because the implementation is only a stub that
  raises `NotImplementedError`. A test that passes before any implementation exists
  is a broken test.
- **GREEN** (Implementer): write the *minimal* code that makes the failing tests
  pass — nothing more. No speculative features, no behavior the tests don't require.
- **REFACTOR** (Implementer, optional): once green, tidy the implementation without
  changing behavior; the tests must stay green.

## Rules for the RED agent (Test Author)

1. Tests are the specification — derive them from `architecture.md`, not from any
   implementation (there isn't one yet).
2. Each test must fail for the *right reason*: the function is unimplemented or the
   asserted contract is not yet met — not because of an import error or a typo.
3. Never write or stub implementation logic to make a test pass. Your deliverable is
   a suite that is RED.
4. Cover the normal contract, edge cases, and every security-sensitive requirement
   named in the design.

## Rules for the GREEN agent (Implementer)

1. Do NOT modify the tests. If a test seems wrong, report it — the tests are the
   contract you must satisfy.
2. Implement the smallest change that turns RED into GREEN. Resist gold-plating.
3. Run the suite after each function; the stage is done only when the whole suite is
   GREEN.
4. If a test genuinely contradicts the verified design, STOP and report `BLOCKED`
   rather than hacking either side.

## Evidence to record

- RED report: the failing pytest output, showing the tests fail because the code is
  not implemented yet.
- GREEN report: the passing pytest output (RED→GREEN), with final pass counts.
- Together these two artifacts prove the code was driven by tests, not the reverse.
