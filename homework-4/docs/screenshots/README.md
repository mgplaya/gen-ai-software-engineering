# Screenshots to capture

The pipeline is gated and reproducible. Capture these live and place the PNGs here.

> The full transcript of a run is saved at
> [`../../context/build/001/pipeline-run.log`](../../context/build/001/pipeline-run.log).

## 1. Architect + plan gate

```bash
./run-pipeline.sh
```
Capture the Architect banner (model `opus-4-8`, loaded `architecture-design` skill)
and the **PLAN GATE** message telling you to verify the plan. → `01-architect-gate.png`

## 2. The design to verify

Open `context/build/001/architecture.md` and a stub file under
`src/expense_splitter/` (showing `raise NotImplementedError`). → `02-design-stubs.png`

## 3. Continue — RED tests

```bash
./run-pipeline.sh --continue
```
Capture the Unit Test Generator stage showing tests **failing (RED)** because the
implementation is missing. → `03-red-tests.png`

## 4. GREEN implementation

In the same run, capture the Implementer stage turning the suite **GREEN**, and/or:
```bash
python -m pytest
```
→ `04-green.png`

## 5. The five artifacts

Screenshot each report:
- `architecture.md` → `05-architecture.png`
- `verified-design.md` (quality level) → `06-verified-design.png`
- `test-report.md` (RED evidence) → `07-test-report.png`
- `implementation-summary.md` (RED→GREEN) → `08-implementation-summary.png`
- `security-report.md` (requirement PASS + findings) → `09-security-report.png`
