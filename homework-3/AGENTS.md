# AGENTS.md — Agent Guidance for Regulated Virtual Card Controls

> This is the assignment's required `agents.md` deliverable. On this case-insensitive filesystem
> (APFS), `agents.md` and `AGENTS.md` resolve to the same file; `AGENTS.md` is the conventional name
> that AI coding tools (including Claude Code and Codex) read. It operationalizes the project
> [Constitution](.specify/memory/constitution.md) for any AI collaborator working on this feature.

## 0. Prime directive

You are working on a **specification package**, not an application. **Do not write application code,
APIs, UIs, database schemas, migrations, package manifests, or infrastructure.** Produce and refine
documentation only (Constitution VII). If asked to implement, stop and confirm scope — the graded
deliverable is the specification.

## 1. Tech stack assumptions (hypothetical, do not install)

- Assume an existing card platform, downstream processor, and identity/step-up service — all
  pre-existing and integrated internally. Never scaffold or install them.
- If a future implementation is discussed, assume a strongly-typed backend service with a
  decimal/integer money type, a transactional store for state, and a separate append-only audit
  store. State these as assumptions; never add a dependency, lockfile, or build config.

## 2. Domain rules (banking / FinTech — non-negotiable)

- **Money**: integer minor units + explicit ISO-4217 currency. **Never use floating point for
  money**, even in examples or fixtures.
- **Time**: immutable UTC occurrence instants; assign daily/monthly periods by the **issuer billing
  calendar**, DST-safe. Never use the viewer's locale for period boundaries.
- **Safety asymmetry**: risk-*reducing* actions (freeze, lower limit) may succeed on a durable local
  block with propagation `pending`; risk-*increasing* actions (unfreeze, raise limit, export) **fail
  closed** on any ambiguity — never return `success` or `pending`.
- **Composite state**: lifecycle × restriction sources; strongest restriction governs; a cardholder
  action can never clear an ops/fraud restriction.
- **Idempotency**: every state-changing command has an idempotency key bound to
  `actor+card+action+payload`; prefer idempotent writes; identical replay returns the original
  outcome; same key + different payload → `conflict`.
- **Concurrency**: optimistic version checks; exactly one winner; losers get a deterministic
  `conflict`; never a lost update.
- **Least privilege**: re-evaluate ownership/role, open case, purpose, grant expiry, step-up
  freshness, and exact permission at the moment of every sensitive action. Separation of duties for
  ops-restriction release.

## 3. Sensitive-data handling (highest severity)

- **Never** emit full PAN, CVV, track/chip data, credentials/secrets, raw downstream-processor
  payloads, unrelated case data, or unredacted free text — in views, logs, audit, exports, fixtures,
  test data, prompts, or examples.
- Reference cards by **token** or masked PAN (≤ first-6/last-4, only where justified).
- Exports use a **versioned field allowlist** and are size-bounded.
- **Never log PAN.** Sanitize all notes/free-text. Keep audit evidence separate from diagnostics;
  neither may contain prohibited data.

## 4. Code style & documentation conventions

- Use the stable ID scheme everywhere: `OBJ-*`, `FR-*`, `NFR-*`, `EC-*`, `SC-*`, `T*`. New
  requirements get the next unused number; never renumber existing IDs.
- Requirements use RFC-2119 keywords (MUST/SHOULD/MAY) and must be testable and unambiguous.
- Every low-level task ends with checkable **acceptance criteria** and a **Traces:** line to the
  requirements it serves.
- Keep Markdown clean: no trailing whitespace; wrap prose near ~100 chars; tables render correctly;
  `git diff --check` must pass.
- Internal links must resolve; when you add an artifact, link it from the relevant index.

## 5. Testing & verification expectations (documented, not executed)

- Describe test categories — unit / integration / e2e — **as documentation**, with **synthetic
  fixtures only**. Do not create runnable test code for this deliverable.
- Each mid-level objective must have a documented review checkpoint and validation scenario
  (see [`quickstart.md`](specs/001-virtual-card-controls/quickstart.md)).
- Maintain 100% traceability (OBJ→FR/NFR→task→SC/EC); zero orphan tasks. Re-run the coverage check
  in [`reviews/analyze.md`](specs/001-virtual-card-controls/reviews/analyze.md) after edits.
- Performance numbers are **assumed targets** — always label them as such and keep them consistent
  between `spec.md`, `specification.md`, and the README.

## 6. Edge-case handling posture

- Treat empty states, partial/downstream failures, concurrency, invalid limits, stale reads,
  permission boundaries, and fraud-ish velocity as first-class — each with an expected user-visible
  outcome **and** an audit/compliance implication.
- When in doubt on a risk-increasing path, **fail closed** and audit the denial with a non-leaking
  reason.
- Audit **denials**, not just successes.

## 7. Spec Kit workflow discipline

- Follow the gated flow: constitution → specify → clarify → checklist → plan → tasks → analyze.
  **Stop before `speckit-implement`** (no code).
- Surface genuine ambiguities as structured clarifications (max 3, prioritized scope >
  security/privacy > UX > technical); otherwise use documented informed defaults.
- Keep the constitution authoritative: if any artifact conflicts with a principle, fix the artifact.

## 8. Review & collaboration

- Author roles and review roles are independent; a final independent analysis must confirm coverage,
  consistency, constitution alignment, and the no-code boundary before the package is "done".
- Route work cost-aware: mechanical/formatting work at low effort; bounded drafting at medium;
  security/compliance/adversarial review and gate synthesis at high effort. Do not use the most
  expensive tier for every task.
- No certification, jurisdiction-specific legal-compliance, accessibility-conformance, or
  production-readiness claims. Reference frameworks (PCI DSS, NIST SP 800-53 / 800-63B, NIST Privacy
  Framework, OWASP ASVS) are used as vocabulary/control references only.
