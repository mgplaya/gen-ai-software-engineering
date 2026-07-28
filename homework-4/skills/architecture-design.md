# Skill: Codebase Research & Fix Planning

**ID**: `architecture-design`
**Used by**: `agents/architect.agent.md` (Stage 1 — Bug Researcher + Bug Planner)
**Purpose**: Give the Architect a fixed rubric for investigating the seeded buggy
codebase and producing verifiable **research** + a **fix plan**, so the Bug Research
Verifier and the human plan gate have something concrete to check.

---

## When to apply

Apply this skill whenever you write `research/codebase-research.md` and
`implementation-plan.md`. The output MUST be concrete enough that (a) a human can
verify the plan, (b) the Bug Research Verifier can check each bug at a real
`file:line`, and (c) the Test Author can write failing tests that reproduce each
bug without guessing.

## Required sections of `research/codebase-research.md`

For **each** seeded bug (expect BUG-1, BUG-2, SEC-1 from `bug-context.md`):

1. **Bug ID & Location** — the id and the exact `file:line`.
2. **Buggy Snippet** — the real line(s) quoted from source (must match the file).
3. **Symptom** — the observable wrong behavior (a concrete example input → wrong
   output).
4. **Root Cause** — why the code is wrong.
5. **Correct Behavior / Invariant** — the rule the fix must satisfy; this is what
   the RED test will assert (e.g. "shares sum exactly to total").
6. **Material?** — yes/no (does a fix depend on this claim).

End with a **References** list of every `file:line` inspected.

## Required sections of `implementation-plan.md`

1. **Test command** — e.g. `.venv/bin/python -m pytest`.
2. **Per-Bug Fix** — for each bug, in order: the file, the exact **Before** block
   and the exact **After** block (so the Bug Fixer can apply it deterministically),
   and the invariant the fix restores.
3. **Build Sequence** — the ordered description of what each downstream stage does
   and which artifact it produces: Bug Research Verifier → Unit Test Generator (RED)
   → Bug Fixer (GREEN) → Security Verifier.

## Quality bar (self-check before finishing)

- Every bug in `bug-context.md` has a research entry confirmed against real source.
- Every research entry has a testable "correct behavior" the RED test can assert.
- Every fix in the plan has exact before/after that matches the current source.
- The security bug's fix removes the unsafe execution path entirely (no `eval`).
- The Build Sequence names all four downstream stages in order.

If any check fails, revise before writing — the human verifies this plan next.

## Hard rules

- Research only — do NOT modify `src/**` or `tests/**` and do NOT write tests.
- Never document a bug you did not open the source to confirm.
