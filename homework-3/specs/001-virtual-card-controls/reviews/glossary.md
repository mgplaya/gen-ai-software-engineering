# Shared Glossary

- **Lifecycle**: `OPEN` or `TERMINATED`, separate from restrictions.
- **Restrictions**: independently sourced `USER_FREEZE`, `OPS_FREEZE`, and `RISK_RESTRICTION`; unknown sources fail safe.
- **Effective status**: derived precedence `TERMINATED` > `RISK_RESTRICTED` > `OPS_FROZEN` > `USER_FROZEN` > `ACTIVE`.
- **Normative results**: `SUCCEEDED`, `PENDING_PROPAGATION`, `DENIED`, `VALIDATION_ERROR`, `CONFLICT`, `IDEMPOTENCY_MISMATCH`, `TEMPORARILY_UNAVAILABLE`.
- **Exact money**: scaled amount plus ISO 4217 currency; never binary floating point.
- **Time**: unambiguous instant plus explicit display timezone/offset; billing timezone/calendar is separate policy metadata.
- **Command identity**: actor/role, card, action, and normalized payload binding retained for the 24-hour assumed window.
- **Audit evidence**: immutable, attributable business evidence; distinct from sanitized time-bounded diagnostics.
- **Freshness**: complete healthy ≤60 seconds is fresh; trusted >60 seconds through 15 minutes or degraded trusted ≤15 minutes is stale; absent or >15 minutes is unavailable.
