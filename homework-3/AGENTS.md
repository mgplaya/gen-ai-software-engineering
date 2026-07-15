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
- `agents.md` is a logically distinct graded section. On this case-insensitive workspace it shares
  one physical file with operational `AGENTS.md`; preserve the delimiters and operational precedence.
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
- For the current Codex model family, route those tiers as follows unless availability requires an
  explicitly recorded substitute: **Economy = `gpt-5.6-luna` with Low/Light reasoning**,
  **Standard = `gpt-5.6-terra` with Medium reasoning**, and **Advanced = `gpt-5.6-sol` with High
  reasoning** (Extra High only for an unusually difficult gate or conflict).
- Treat identifiers such as `AG-E01` and names such as `codex-docs-ops` as stable task-plan roles,
  not model names and not proof that a separate runtime process used the recommended profile. Record
  the selected model/profile in execution evidence when the runtime exposes it; otherwise describe
  the mapping as a recommendation rather than an observed fact.
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

## Active ChatGPT/Codex Repository Rules

This section is the assignment's editor/AI-rules deliverable for the AI actually used in this
repository. Codex reads it directly from `AGENTS.md`; no Copilot-specific file is used.

- Follow canonical `specification.md`; supporting plans/contracts cannot invent behavior.
- Preserve requirement IDs and approval gates. Surface conflicts and material assumptions instead of
  choosing product, policy, security, compliance, or architecture behavior silently.
- Keep Homework 3 documentation-only: no code, API/UI, schemas, migrations, packages, infrastructure,
  prototypes, or `speckit-implement`.
- Apply the composite-state, durable-freeze, fail-closed unfreeze/increase, exact-money/time,
  idempotency/concurrency, stable-pagination, authorization, privacy, audit, and recovery rules in the
  graded section below.
- Never use production/personal data or reveal prohibited categories. Examples and fixtures are
  synthetic, opaque, fictional, and masked.
- Use Economy for mechanical work, Standard for bounded drafting/testing, and Advanced only for
  high-risk FinTech/security/compliance/conflict/gate judgment. Keep material review independent.

<!-- SPECKIT START -->
For the current feature's hypothetical technology assumptions, artifact structure, validation flow,
and agent/model allocation, read `specs/001-virtual-card-controls/plan.md`. Product behavior remains
authoritative in the Gate-1-approved `specs/001-virtual-card-controls/spec.md`.
<!-- SPECKIT END -->

<!-- GRADED AGENTS.MD START -->
# Future Agent Guidance: Regulated Virtual Card Controls

> **Filesystem compatibility note:** this workspace uses a case-insensitive filesystem, so
> `AGENTS.md` and the assignment-required `agents.md` resolve to the same physical file. The section
> above remains the operational collaboration policy; this clearly delimited section is the graded
> future-agent guidance. Both names intentionally resolve to this combined artifact.

## Authority and Future Workflow

- Treat the canonical `specification.md` as product authority after final publication. Until then,
  use approved `specs/001-virtual-card-controls/spec.md`. Plans, research, models, contracts, and
  tasks explain delivery but cannot add product behavior.
- Work specification-first: clarify intent, update the specification, assess impact, validate, and
  pass the applicable human gate before implementation. Never hide a product, policy, architecture,
  security, or compliance decision inside code.
- A material approved-artifact change invalidates that approval and affected downstream artifacts.
  Preserve objective/requirement IDs in task output, tests, and review evidence.
- Homework 3 is documentation-only. Do not create source, API/UI scaffolding, schemas, migrations,
  dependencies, infrastructure, or prototypes, and never run `speckit-implement` for this homework.

## Hypothetical Future Stack

The future-stack vocabulary is Node.js 22, TypeScript 5.7, NestJS 11, Jest 29, Supertest 7, a
PostgreSQL-like ACID relational control store, a modular monolith with ports/adapters, and a
conceptual transactional outbox. Identity/step-up, issuer-policy, processor, ledger, case-authority,
audit, monitoring, and alerting integrations remain vendor-neutral.

These are replaceable assumptions, not installed or mandated technologies. Keep domain logic
independent of framework and adapters. Do not select packages, vendors, transport shapes, schemas,
or deployment topology without impact analysis and approval. The authorization processor must
synchronously honor the durable local block; otherwise escalate the feasibility conflict with
`FR-003` and `NFR-004` instead of weakening the invariant.

## State, Money, and Time Rules

- Model lifecycle (`OPEN`, `TERMINATED`) separately from restriction sources. Derive effective status
  in this precedence: terminated, risk restriction, operations freeze, user freeze, active. Unknown
  restriction sources are restrictive and cannot be removed by this feature.
- A command changes only the restriction it owns. Cardholder unfreeze removes only `USER_FREEZE`;
  operations/risk release is outside this feature.
- Accept a user or operations freeze only when its durable local authorization block is effective in
  the same atomic safety boundary. External propagation can then be confirmed or truthfully
  `PENDING_PROPAGATION`; it never weakens the local restriction.
- Every cardholder unfreeze requires current ownership, lifecycle `OPEN`, an existing user freeze,
  current step-up, expected version, and confirmed policy/dependency outcomes. Fail closed; never
  return pending or success for an ambiguous unfreeze.
- Treat per-transaction, daily, and monthly limits as one atomic versioned set satisfying
  `per-transaction <= daily <= monthly`. A frozen card accepts only a complete non-increasing set
  with at least one decrease; any increase rejects the entire set.
- Represent money as exact scaled amount plus ISO 4217 currency, never binary floating point.
  Authorization holds consume allowance; posting replaces its hold; reversals release matching
  holds; refunds are distinct linked credits and do not replenish historical daily/monthly allowance.
  FX posting adjustment never retroactively changes the authorization decision.
- Represent event time as an unambiguous instant. Keep issuer billing timezone/calendar separate
  from actor display timezone; daily/monthly boundaries must be DST-safe and occur exactly once.
- Keep transaction identity and occurrence time immutable. Status changes are events; refunds are
  distinct linked transactions. Sort by occurrence instant descending, then immutable transaction ID
  descending.

## Idempotency, Concurrency, and Results

- Every state or limit command carries an expected version and identity bound to actor ID/role, card,
  action, and normalized payload.
- The first distinct durably accepted command for an expected version wins. Later distinct commands
  return `CONFLICT` with current sanitized state/version and never overwrite accepted state.
- During the assumed 24-hour window, an exact bound retry returns the original outcome without a
  second transition/event. Changed binding returns `IDEMPOTENCY_MISMATCH`, changes nothing, exposes no
  target detail, and is audited.
- Use only `SUCCEEDED`, `PENDING_PROPAGATION`, `DENIED`, `VALIDATION_ERROR`, `CONFLICT`,
  `IDEMPOTENCY_MISMATCH`, and `TEMPORARILY_UNAVAILABLE`.
- An already-satisfied freeze is an attributable successful no-op: no restriction/version mutation,
  propagation intent, or duplicate transition event.
- Never claim freeze cancels activity authorized earlier; it may later post, reverse, or receive a
  related refund.

## Authorization, Security, Privacy, and Audit

- Re-evaluate ownership or current role, assigned open case, enumerated purpose, expiry, and exact
  permission for every sensitive read/action/page. Cached context or self-asserted purpose is not
  authority. Unauthorized results cannot confirm target existence.
- Keep operations and compliance separate. Operations may perform case-scoped sanitized reads and
  add emergency `OPS_FREEZE` under approved purposes/reasons; it cannot export, change limits, or
  release restrictions. Compliance is read-only and may export one assigned case after step-up, with
  at most 10,000 sanitized records and 24-hour expiry.
- Deny and alert after more than 20 distinct card subjects per operations actor in five minutes;
  deny and alert cross-case or over-10,000-record exports.
- Follow the canonical per-surface allowlists. Compliance export also requires a current approved,
  versioned, purpose-bound field allowlist; when it is absent, stale, or mismatched, fail closed.
  Never expose/log full PAN, CVV, credentials,
  verification material, raw dependency payloads, unrelated-customer/case data, or unredacted
  free-form personal data.
- Never use production, personal, or captured financial data in source, fixtures, tests, prompts,
  examples, logs, snapshots, or documents. Use clearly synthetic opaque IDs, fictional safe labels,
  exact test amounts, and issuer-approved masked representations only.
- Separate append-only, tamper-evident business audit evidence from sanitized diagnostics.
  Diagnostics never replace evidence; corrections are linked events and never rewrite original
  meaning.
- Give every distinct command outcome and privileged outcome one root audit identity, including
  validation, conflict, mismatch, unavailable, no-op, and pending results. An exact bound retry
  references the original identity and creates no second business event. Pending propagation and its
  final reconciliation use immutable linked events under the same root identity. Record durable audit
  intent in the same boundary as every state change or privileged outcome and record non-changing
  attempt evidence without mutating product state. Deliver/replay idempotently by event identity.
  Evidence contains only opaque identities,
  enumerated reasons, sanitized before/after, result, time, policy, case, and correlation.
- When evidence is absent after five seconds, alert security/compliance operations and recover
  duplicate-safely. Keep degraded-safe mode after a five-minute miss and declare an incident at 15
  minutes. Degraded-safe mode rejects unfreeze, increases, exports, and other risk-increasing writes;
  it permits durable freezes and authorized reads only when audit intent can be recorded.
- Treat seven-year audit retention and 24-month cardholder history as assumptions, not legal claims.
  Jurisdiction, hold, deletion, and disposition require policy/legal approval.

## Transaction Reads and Edge Cases

- Recheck ownership on every page/continuation. Bind continuation to owner/card authorization,
  filters, ordering version, snapshot or `as of`, and last sort key. Offset-only paging is prohibited.
- Default to 50 items and cap at 100. Traversal remains stable during arrivals/status changes;
  refresh starts a new snapshot.
- Return fresh or truthful empty only for a healthy, trusted, fully evaluated snapshot no older than
  60 seconds. Return `STALE` with exact `as of` when a trusted snapshot is no older than 15 minutes
  and is degraded or older than 60 seconds. Without a trusted snapshot or above 15 minutes, return
  `UNAVAILABLE`, never empty/stale.
- Freeze propagation alerts operations at 60 seconds and escalates unresolved at 15 minutes.
  Ambiguous non-freeze outcomes fail closed and surface for operations review within five minutes.
- Messages distinguish final, pending, denied, stale, and unavailable without color alone or
  dependency internals.

## Testing and Verification

Future work is incomplete until requirement-linked evidence passes. At minimum, design and run:

- composite lifecycle/restriction and actor-owned transition matrices;
- exact-money, currency-scale, hold/post/reversal/refund, FX, DST, and period-boundary cases;
- duplicate/mismatched commands and 20 concurrent same-version commands, proving exactly one winner
  with no lost accepted update;
- a 100,000-item, 24-month synthetic traversal with ties and concurrent arrivals, proving zero
  duplicates, skips, unauthorized records, prohibited fields, or order drift;
- role x case status/assignment/expiry x purpose x action negatives, including 20/21-search and
  10,000/10,001-export boundaries;
- outcome-to-audit reconciliation, delayed sink, replay, correction, five-minute recovery, and
  15-minute incident cases;
- automated prohibited-category scans and manual per-surface privacy review;
- healthy/degraded measures for two-second interactive p95, five-second propagation/evidence,
  60-second alert, five-minute recovery, 15-minute escalation, and specified 99.9% availability.
  These are assumed targets until validated against production context;
- accessibility/content review for each critical result category.

Use unit/property tests for pure money/state/time rules; contract tests for ports/adapters;
integration tests for atomic state/version/outbox/audit boundaries; end-to-end actor journeys; and
concurrency, recovery, performance, privacy, and manual compliance reviews for their respective
risks. High-risk security, payments, privacy, and compliance evidence requires an independent
reviewer.

## Agent and Model Routing

- Decompose by domain risk, context, dependencies, non-overlapping output, and independently
  verifiable acceptance. Record requirement IDs, role, tier rationale, inputs/output, dependencies,
  parallel-safety, acceptance criteria, and reviewer.
- Use **Economy** for extraction, formatting, link/terminology scans, checklists, and status updates;
  **Standard** for bounded drafts, decomposition, traceability, scenarios, and focused reviews; and
  **Advanced** only for ambiguous architecture/product decisions, FinTech, security/compliance,
  adversarial review, conflict resolution, and gate synthesis.
- Recommended Codex profiles are `gpt-5.6-luna` Low/Light for Economy, `gpt-5.6-terra` Medium for
  Standard, and `gpt-5.6-sol` High for Advanced. Agent IDs are role identifiers, not model names;
  never claim a recommended profile was actually used without runtime evidence.
- Keep authorship and material validation independent. Advanced review does not justify using an
  Advanced model for mechanical preparation.
- Parallelize only non-overlapping outputs after shared terminology/decisions are fixed. Agent output
  is advisory until incorporated, validated, and approved.

## Stop and Escalate

Stop rather than guess when a request conflicts with the approved specification, weakens local freeze
safety or fail-closed behavior, introduces an unapproved result/state, needs prohibited data, changes
authorization/audit semantics, assumes jurisdictional compliance, or makes stable snapshots
infeasible. Record the conflict, impacted requirement IDs, alternatives, and required approver.
<!-- GRADED AGENTS.MD END -->
