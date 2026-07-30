# Screenshots to capture

The pipeline is gated and reproducible. Capture these live and place the PNGs here.

> The full transcript of a run is saved at
> [`../../context/bugs/001/pipeline-run.log`](../../context/bugs/001/pipeline-run.log).

## 1. Architect + plan gate

```bash
./run-pipeline.sh
```
Capture the Architect banner (model `opus-4-8`, loaded `architecture-design` skill)
and the **PLAN GATE** message telling you to verify the plan. → `01-architect-gate.png`

## 2. The plan to verify

Open `context/bugs/001/research/codebase-research.md` (the bugs) and
`context/bugs/001/implementation-plan.md` (the proposed fixes). → `02-research-plan.png`

## 3. Continue — RED tests

```bash
./run-pipeline.sh --continue
```
Capture the Unit Test Generator stage showing tests **failing (RED)** because the
implementation is missing. → `03-red-tests.png`

## 4. GREEN implementation

In the same run, capture the Bug Fixer stage turning the suite **GREEN**, and/or:
```bash
python -m pytest
```
→ `04-green.png`

## 5. The five artifacts

Screenshot each report:
- `codebase-research.md` → `05-architecture.png`
- `verified-research.md` (quality level) → `06-verified-design.png`
- `test-report.md` (RED evidence) → `07-test-report.png`
- `fix-summary.md` (RED→GREEN) → `08-implementation-summary.png`
- `security-report.md` (requirement PASS + findings) → `09-security-report.png`
