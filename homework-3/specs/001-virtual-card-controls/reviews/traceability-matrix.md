# Traceability Matrix: Regulated Virtual Card Controls

**Date**: 2026-07-15 · Chain: **Objective → Requirements → Tasks → Success/Edge coverage**

## Objective → Requirements → Tasks

| OBJ | Description | Functional Reqs | Tasks | User story |
|-----|-------------|-----------------|-------|------------|
| OBJ-1 | Instant, safe freeze | FR-001..FR-005 | T008, T009 (+T003–T007) | US1 |
| OBJ-2 | Fail-closed unfreeze | FR-006..FR-010, FR-030 | T010, T011, T012 | US2 |
| OBJ-3 | Exact, atomic limits | FR-011..FR-018 | T013, T014, T015 | US3 |
| OBJ-4 | Stable history | FR-019..FR-024 | T016, T017 | US4 |
| OBJ-5 | Least-privilege oversight | FR-025..FR-030 | T018, T019 | US5 |
| OBJ-6 | Audit/idempotency/privacy/recovery | FR-031..FR-040 | T004, T005, T007, T020, T022 | US-ALL |

## Non-functional → where enforced

| NFR | Enforced by |
|-----|-------------|
| NFR-001 step-up | FR-009; T010 |
| NFR-002 privacy / NFR-003 sensitive data | FR-021/037/038; T007 |
| NFR-004 auditability | FR-033; T005; SC-003 |
| NFR-005 reliability | FR-002/003; T008; SC-007 |
| NFR-006 consistency | EC-24; SC-002 |
| NFR-007 concurrency | FR-017; T004; SC-005 |
| NFR-008 performance | SC-001/002; T022 |
| NFR-009 least privilege | FR-025/040; T006, T018 |
| NFR-010 separation of duties | FR-030; T011 |
| NFR-011 idempotency | FR-031/032; T004; SC-008 |
| NFR-012 observability split | FR-033; T005 |
| NFR-013 verification | T022; quickstart.md |
| NFR-014 availability | SC-007 |

## Success Criteria → validating scenario/task

| SC | Validated by |
|----|--------------|
| SC-001, SC-002 | quickstart Scenario 1; T008 |
| SC-003 | quickstart 1/7/8; T005 |
| SC-004 | quickstart 6; T016 |
| SC-005 | quickstart 4; T015 |
| SC-006 | quickstart 2; T010 |
| SC-007 | quickstart 9; T020 |
| SC-008 | quickstart 5; T004 |

## Edge case → requirement/task

All EC-01..EC-26 are referenced by at least one FR and one task (see tasks.md acceptance criteria).
Representative: EC-03→T008, EC-05→T010, EC-08/09→T014, EC-10→T015, EC-12→T004, EC-14/15→T016,
EC-16→T017, EC-18/19→T018, EC-20/21→T019, EC-22→T020, EC-23→T021.

## Coverage summary

- **6/6 OBJ** map to requirements and tasks.
- **40/40 FR**, **14/14 NFR** covered by ≥1 task.
- **26/26 EC** referenced by ≥1 task acceptance criterion.
- **8/8 SC** validated by ≥1 documented scenario.
- **0** orphan tasks; **0** requirements without a parent objective.
