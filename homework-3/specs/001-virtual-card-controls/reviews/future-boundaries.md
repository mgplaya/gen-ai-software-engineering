# Hypothetical Future Boundaries

| Boundary | Responsibility | Dependencies | Safe failure |
|----------|----------------|--------------|--------------|
| Control Application | Orchestrate ownership, state, versions, idempotency, and results | Identity, policy, store | No ambiguous risk-increasing success |
| Authorization and Policy | Enforce local restrictions and exact allowance decisions | Control state, issuer policy | Durable freeze remains restrictive |
| Control Store and Outbox | Atomically retain state, outcome, audit, and propagation intent | ACID relational semantics | Roll back incomplete acceptance |
| Processor Propagation | Deliver idempotent freeze intent | Processor boundary | Pending plus retry/escalation |
| Transaction Query | Return owned sanitized snapshot traversal | Ledger or read projection | Stale/unavailable, never false empty |
| Internal Access | Enforce current role/case/purpose/action | Identity and case authority | Deny without target disclosure |
| Audit and Reconciliation | Publish evidence and repair mismatches | Evidence store, monitoring | Degraded-safe mode and incident timeline |

These are responsibility seams only; no transport, schema, class, endpoint, or vendor is selected.
