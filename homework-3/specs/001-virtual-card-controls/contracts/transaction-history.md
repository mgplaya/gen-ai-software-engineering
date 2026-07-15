# Conceptual Contract: Transaction History

**Contract type**: Technology-neutral query, item, snapshot, freshness, and privacy behavior
**Not included**: Endpoint, query language, response serialization, database, or UI

## Query Preconditions

- Actor is the currently authenticated owner of the requested virtual card.
- Ownership is re-evaluated for every request and continuation; cached screen context is insufficient.
- Date range and status filters are within approved bounds and bound into continuation context.
- Default page size is 50 and maximum is 100.

An unauthorized query returns no confirmation that the card or transactions exist.

## Snapshot and Continuation

The first page establishes an immutable query context containing card/owner authorization context,
filters, ordering version, source snapshot or `as of` instant, and last sort key. A continuation is
valid only for the same bound context and moves after the last
`authorization_or_occurrence_instant DESC, transaction_id DESC` key.

Newly arriving transactions or later status events MUST NOT cause duplicates, gaps, or reordering
inside that traversal. Refresh begins a new query context. Offset-only pagination is prohibited.

## Transaction Item

| Field/meaning | Contract requirement |
|---------------|----------------------|
| Transaction ID | Immutable opaque identity and deterministic tie-breaker |
| Masked card identity | Issuer-approved masked form only |
| Safe merchant label | Sanitized; no raw processor/free-form payload |
| Occurrence/authorization time | Immutable instant, displayed with timezone/offset |
| Latest status-event time | Separate instant; does not change primary ordering |
| Billing amount/currency | Exact signed value and scale |
| Original amount/currency | Exact value when different |
| Status | Pending, posted, declined, or reversed from status events |
| Related original ID | Present on a distinct refund credit transaction |
| Freshness | Exact source `as of` instant and derived freshness category |

Full PAN, CVV, credentials, verification material, other-customer data, raw dependency payloads, and
unredacted personal/free-form data are prohibited by the canonical taxonomy.

## Status and Relationship Rules

- Posting, decline, and full/partial reversal are timestamped events on the original identity.
- A refund is a distinct linked credit transaction with its own identity.
- A transaction authorized before freeze may later post/reverse or receive a related refund; this is
  not by itself a freeze-bypass event.
- Status changes preserve the original occurrence time and traversal position.

## Freshness and Availability

| Source condition | Required category |
|------------------|-------------------|
| Healthy, trusted snapshot age ≤60 seconds, and requested range completely evaluated | Fresh data or truthful empty result |
| Trusted snapshot age ≤15 minutes and either source health is degraded or age is >60 seconds | `STALE` with exact `as of` instant |
| No trusted snapshot or snapshot age >15 minutes, regardless of source-health label | `UNAVAILABLE`; never empty or stale |

Unavailable/internal/dependency failures count as availability failures under `NFR-007`.

## Verification Oracles

- Traverse 100,000 synthetic transactions with tied times and concurrent arrivals: zero duplicate,
  skip, unauthorized item, or order drift.
- Exercise pending→posted/reversed and linked refund: original identity/order remains immutable.
- Exercise DST/display timezone: original instant remains unchanged and display is unambiguous.
- Exercise healthy empty, degraded stale, and unavailable: exactly one truthful category appears.
- Scan every item/context for canonical taxonomy-prohibited categories.

## Traceability

`OBJ-003`, `OBJ-006`; `FR-022–FR-030`; `NFR-002`, `NFR-006–NFR-007`, `NFR-010`, `NFR-014`;
`EC-001`, `EC-011–EC-015`, `EC-022`, `EC-026`; `SC-004`.
