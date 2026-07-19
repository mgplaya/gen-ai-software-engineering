# Clarification Session: Regulated Virtual Card Controls

**Phase**: `/speckit-clarify` (run after `/speckit-specify`, before `/speckit-plan`)
**Date**: 2026-07-15
**Spec**: [spec.md](../spec.md)

The specify phase made informed defaults for most ambiguities (documented in the spec's *Assumptions*
section). One ambiguity had **multiple reasonable interpretations with materially different
security implications** and no safe default, so it was surfaced as a structured question rather than
guessed.

## Q1 — Who may release an operations-initiated freeze?

**Context** (from spec, FR-026): "An operations-initiated restriction MUST NOT be removable by a
cardholder unfreeze." This left open *which internal actor* may release it.

**Why it matters**: This is a separation-of-duties and fraud-control decision. Guessing wrong either
creates an insider-risk hole (self-release) or blocks legitimate recovery (no one can release).

| Option | Answer | Implications |
|--------|--------|--------------|
| A | The original ops placer alone | Fast, but single-actor control over risk-increasing release → insider-risk and audit weakness. |
| B | A second authorized ops/compliance actor (distinct from placer) | Separation of duties; stronger fraud/insider control; slightly more process. **Recommended.** |
| C | Any ops agent with the permission | Simple, but no separation of duties; weakest control. |
| Custom | Provide your own answer | e.g., dual-control with time delay. |

**Decision**: **Option B** — release requires a distinct second authorized ops/compliance actor,
never the original placer alone and never the cardholder.

**Encoded as**: **FR-030** (separation-of-duties release rule) and **NFR-010** (separation of
duties), consistent with Constitution Principle IV (Least Privilege) and NIST SP 800-53 AC-5
(Separation of Duties).

## Other candidate ambiguities — resolved by informed default (no user question needed)

| Topic | Default chosen | Rationale |
|-------|----------------|-----------|
| Idempotency window length | 24 hours | Common retry/settlement horizon; stated as assumed target (SC-008). |
| Limit boundary inclusivity | Inclusive (`amount == limit` approved) | Least-surprise; documented in FR-013/EC-08. |
| Period timezone | Issuer billing calendar, DST-safe | Prevents limit-evasion at boundaries (FR-014/EC-09). |
| History ordering | Most-recent-first, keyset/snapshot | Standard, stable under concurrency (FR-020). |
| Export size bound | Bounded/paginated | Prevents unbounded sensitive dumps (FR-028/EC-21). |

**Outcome**: Spec updated; no `[NEEDS CLARIFICATION]` markers remain. Ready for `/speckit-plan`.
