# Skill: Architecture Design

**ID**: `architecture-design`
**Used by**: `agents/architect.agent.md` (Stage 1)
**Purpose**: Give the Architect a fixed rubric for turning a feature request into a
verifiable design + interface scaffold + build sequence, so the Design Verifier and
the human plan gate have something concrete to check.

---

## When to apply

Apply this skill whenever you write `architecture.md` and scaffold stub interfaces.
The design MUST be concrete enough that (a) a human can verify the plan, (b) the
Design Verifier can check each interface against a real stub `file:line`, and (c)
the Test Author can write tests without guessing signatures.

## Required sections of `architecture.md`

Write these sections, in this order:

1. **Overview** — one paragraph: what the system does and its boundaries.
2. **Public Interface** — a table of every public function: module, signature,
   inputs, return, and a one-line contract. This is the API the tests and
   implementation depend on.
3. **Behaviors & Invariants** — the testable rules (e.g. "even split shares sum
   exactly to the total"; "weighted shares are proportional to sum(weights)").
4. **Edge Cases** — boundary/error conditions each function must handle.
5. **Security-Sensitive Requirements** — at least ONE explicit requirement (e.g.
   "CLI amount parsing MUST NOT evaluate input as code"). The Security Verifier will
   check this by name.
6. **Project Structure** — the file/module layout, and where stubs live.
7. **Build Sequence** — the ordered description of what each downstream agent does
   and which artifact it produces: Design Verifier → Unit Test Generator (RED) →
   Implementer (GREEN) → Security Verifier. This is the sequence the Architect is
   responsible for describing.
8. **References** — `file:line` of each scaffolded stub, so the design maps to code.

## Stub-scaffolding rules

- Create one stub per public function: exact signature + a precise docstring
  describing the contract + a body of `raise NotImplementedError("<name>")`.
- Include `__init__.py` exporting the public names.
- NO business logic anywhere. A reader must be able to tell what each function will
  do from the docstring alone.
- Keep the surface small (a handful of functions) so one TDD pass can complete.

## Quality bar (self-check before finishing)

- Every capability in the feature request maps to at least one public function.
- Every public function has a testable contract and named edge cases.
- At least one security-sensitive requirement is stated explicitly.
- Every interface in the doc has a matching stub at a real `file:line`.
- The build sequence names all four downstream stages in order.

If any check fails, revise before writing — the human verifies this plan next.
