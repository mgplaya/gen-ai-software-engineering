# Homework 3 Collaboration Rules

## Working agreement

- Use specification-driven development: establish intent, document assumptions, plan the work,
  decompose it into traceable tasks, validate the artifacts, and only then consider implementation.
- Keep requirements, decisions, open questions, validation results, and task status in repository
  documents rather than relying on chat history alone.
- Treat the approved specification as the source of truth. If a request conflicts with it, stop and
  resolve the conflict in the specification before continuing.
- Do not interpret silence, partial feedback, or approval of one artifact as approval of later
  artifacts. An approval gate passes only when the user explicitly approves that artifact.
- A material change to an approved artifact invalidates approval of that artifact and all affected
  downstream artifacts. Revalidate and request approval again.

## Homework 3 scope

- `TASKS.md` is the authoritative assignment brief.
- Homework 3 produces documentation only. Source code, application scaffolding, executable API/UI
  implementations, database migrations, and dependency installation are out of scope unless the
  assignment itself is explicitly changed.
- `agents.md` is a graded homework artifact distinct from this operational `AGENTS.md`. Design and
  approve it as part of the Homework 3 specification package.
- Maintain traceability from the high-level objective through mid-level objectives, policy and
  non-functional requirements, implementation notes, verification criteria, and low-level tasks.
- FinTech requirements must explicitly cover relevant edge cases, failure behavior, sensitive-data
  boundaries, authorization, auditability, idempotency/concurrency, measurable performance targets,
  and verification.

## Spec Kit workflow and approval gates

Use the GitHub Spec Kit flow as a baseline and adapt it when that improves the assignment artifacts:

1. Establish or revise governing principles (`constitution`).
2. Draft the feature specification (`specify`).
3. Resolve ambiguity and validate requirement quality (`clarify` and `checklist`).
4. **Gate 1 — Specification approval:** present the completed specification and validation findings;
   wait for explicit user approval.
5. Draft the technical/delivery plan (`plan`) only after Gate 1.
6. **Gate 2 — Plan approval:** validate the plan against the approved specification and wait for
   explicit user approval.
7. Produce the actionable task breakdown (`tasks`) only after Gate 2.
8. Run cross-artifact consistency and coverage analysis (`analyze`), resolve findings, and revalidate
   affected artifacts.
9. **Gate 3 — Final package approval:** present the specification, plan, tasks, checklists, and
   unresolved risks; wait for explicit user approval.
10. Start implementation only after Gate 3 and only when implementation is in scope. For Homework 3,
    stop at the approved documentation package because implementation is explicitly out of scope.

Before an implementation gate has passed, allowed work is limited to discovery, read-only
inspection, research, questions, and creating or editing planning/specification/documentation
artifacts. Do not create implementation code "for illustration," prototypes, generated scaffolding,
or implementation-adjacent changes that bypass the gates.

## Collaboration behavior

- At the start of each phase, state which artifact is being worked on, its inputs, and its exit
  criteria.
- Surface assumptions and unresolved decisions instead of silently choosing requirements that
  materially affect scope or risk.
- Record each agreed decision in the relevant artifact and keep task status current.
- Before requesting approval, summarize validation evidence, inconsistencies found and resolved,
  remaining risks, and the exact scope being approved.

## Agent and model routing

- Decompose work before assigning agents. Split tasks by domain responsibility, risk, required
  context, dependencies, and independently verifiable output—not only by size, complexity, or
  iteration.
- Every task plan must identify at least: task ID, objective/requirement references, assigned agent
  role, recommended model tier, rationale for that tier, inputs, output artifact, dependencies,
  parallel-safety, and acceptance or review criteria.
- Use the least expensive model tier that can reliably complete the task:
  - **Economy:** mechanical extraction, formatting, link and terminology checks, checklist execution,
    task-status updates, and other tightly bounded transformations.
  - **Standard:** first drafts, requirement decomposition, traceability mapping, test-scenario design,
    and focused reviews with clear constraints.
  - **Advanced:** ambiguous product decisions, FinTech/security/compliance judgment, architecture and
    cross-artifact conflict resolution, adversarial review, and approval-gate synthesis.
- Do not assign an advanced model to all tasks by default. Prefer a standard or economy agent to
  prepare bounded artifacts, then use an advanced agent only for high-risk decisions and concise
  review of those artifacts.
- Keep authorship and validation independent for material artifacts: the same agent may revise its
  work, but a separate reviewer role must perform the final domain, security, or consistency check.
- Parallelize only tasks with explicit non-overlapping outputs and no unresolved shared decision.
  Tasks that depend on a product, policy, or architecture choice must wait until that choice is
  approved.
- Agent output is advisory until incorporated into the repository artifact and validated through the
  applicable approval gate.

<!-- SPECKIT START -->
For the current feature's hypothetical technology assumptions, artifact structure, validation flow,
and agent/model allocation, read `specs/001-virtual-card-controls/plan.md`. Product behavior remains
authoritative in the Gate-1-approved `specs/001-virtual-card-controls/spec.md`.
<!-- SPECKIT END -->
