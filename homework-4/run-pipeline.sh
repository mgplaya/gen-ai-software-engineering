#!/usr/bin/env bash
#
# run-pipeline.sh — single-command driver for the architect-led TDD build pipeline.
#
# Design-first, test-driven. Five agents in a fixed order, with a HUMAN PLAN GATE
# after the Architect (Constitution III & VII):
#
#   1. Architect            (opus-4-8)   -> architecture.md + src/ stubs
#      -------- HUMAN VERIFIES THE PLAN (stop here by default) --------
#   2. Design Verifier      (opus-4-8)   -> verified-design.md         (read-only)
#   3. Unit Test Generator  (haiku-4-5)  -> tests/ + test-report.md    (TDD RED)
#   4. Implementer          (sonnet-5)   -> src/ + implementation-summary.md (GREEN)
#   5. Security Verifier    (opus-4-8)   -> security-report.md         (read-only)
#
# Each stage runs via the Claude Code CLI headless (`claude -p`). The agent's
# definition (agents/*.agent.md) and its skill files (skills/*.md) are concatenated
# into the stage's system prompt, so skills load with no manual step. Each stage gets
# only the tools its role permits (verifiers: no Edit/Bash).
#
# Usage:
#   ./run-pipeline.sh                 # run the Architect, then STOP for human verify
#   ./run-pipeline.sh --continue      # after verifying the plan, run stages 2..5
#   ./run-pipeline.sh --all           # run all 5 stages without stopping at the gate
#   ./run-pipeline.sh --only <stage>  # run one stage:
#                                     #   architect | design-verifier | test-author
#                                     #   | implementer | security-verifier
#   ./run-pipeline.sh --dry-run       # print what would run without calling the CLI
#   ./run-pipeline.sh -h | --help
#
set -euo pipefail

ROOT="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

BUILD_DIR="context/build/001"
LOG="$BUILD_DIR/pipeline-run.log"
DRY_RUN=false
MODE="gate"      # gate | continue | all
ONLY=""

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi
export PYTHON

# ----- arg parsing -----------------------------------------------------------
while [ $# -gt 0 ]; do
  case "$1" in
    --continue) MODE="continue"; shift ;;
    --all)      MODE="all"; shift ;;
    --only)     ONLY="${2:-}"; shift 2 ;;
    --dry-run)  DRY_RUN=true; shift ;;
    -h|--help)  sed -n '2,32p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

# ----- prerequisites ---------------------------------------------------------
if ! command -v claude >/dev/null 2>&1; then
  echo "ERROR: the 'claude' CLI is required but was not found on PATH." >&2
  exit 1
fi
mkdir -p "$BUILD_DIR"
: > "$LOG"

log() { printf '%s\n' "$*" | tee -a "$LOG"; }
model_of()  { grep -m1 '^model:' "$1" | sed 's/^model:[[:space:]]*//'; }
# `|| true` so an agent with no skills (grep no-match -> exit 1) doesn't trip pipefail.
skills_of() { { grep -oE 'skills/[A-Za-z0-9._-]+\.md' "$1" || true; } | sort -u; }

# run_stage <human-name> <agent-file> <user-directive> <allowed-tools>
# <allowed-tools> encodes the role's permission boundary (Constitution II):
#   verifiers get read/report tools only (no Edit, no Bash).
run_stage() {
  local name="$1" agent_file="$2" directive="$3" allowed="$4"
  local model; model="$(model_of "$agent_file")"

  log ""
  log "=================================================================="
  log ">> STAGE: $name   (model: $model)"
  log "=================================================================="

  local sysfile; sysfile="$(mktemp -t pipeline-sys.XXXXXX)"
  {
    echo "You are running as a single pipeline stage. Follow the agent definition"
    echo "below exactly. Your working directory is: $ROOT"
    echo "Use '$PYTHON -m pytest' as the test command."
    echo
    echo "===== AGENT DEFINITION ($agent_file) ====="
    cat "$agent_file"
    local skill
    for skill in $(skills_of "$agent_file"); do
      echo
      echo "===== AUTO-LOADED SKILL ($skill) ====="
      cat "$skill"
    done
  } > "$sysfile"

  local sk; sk="$(skills_of "$agent_file" | tr '\n' ' ')"
  log "   auto-loaded skills: ${sk:-(none)}"
  log "   allowed tools: $allowed"

  if $DRY_RUN; then
    log "   [dry-run] would call: claude -p --model $model --allowedTools \"$allowed\" (system prompt: $(wc -l <"$sysfile") lines)"
    rm -f "$sysfile"; return 0
  fi

  set +e
  claude -p "$directive" \
    --model "$model" \
    --append-system-prompt-file "$sysfile" \
    --add-dir "$ROOT" \
    --permission-mode acceptEdits \
    --allowedTools "$allowed" 2>&1 | tee -a "$LOG"
  local rc=${PIPESTATUS[0]}
  set -e
  rm -f "$sysfile"

  if [ "$rc" -ne 0 ]; then
    log ""; log "!! STAGE FAILED: $name (exit $rc). Pipeline halted."
    exit "$rc"
  fi
  log "<< STAGE OK: $name"
}

# ----- tool sets -------------------------------------------------------------
RO_TOOLS="Read Glob Grep Write"               # verifiers: report-only
RW_TOOLS="Read Glob Grep Edit Write Bash"     # test author + implementer
ARCH_TOOLS="Read Glob Grep Edit Write"        # architect: scaffolds stubs, no Bash

# ----- stage directives ------------------------------------------------------
D_ARCH="Execute the Architect stage. Read $BUILD_DIR/feature-request.md, design the expense_splitter library + CLI, scaffold stub interfaces under src/expense_splitter/ (exact signatures + docstrings + 'raise NotImplementedError', NO logic), and write $BUILD_DIR/architecture.md including a Build Sequence section, applying the loaded architecture-design skill. Do NOT write tests or real implementation. Finish by printing the output path, the stub files created, and that a human must verify the plan next."

D_DESIGN="Execute the Design Verifier stage. Read $BUILD_DIR/architecture.md and $BUILD_DIR/feature-request.md, verify every interface reference against the scaffolded stubs under src/, and write $BUILD_DIR/verified-design.md using the loaded research-quality-measurement skill. Do NOT edit any code. Finish by printing only the output path and the design-quality level."

D_TEST="Execute the Unit Test Generator stage (TDD RED). Read $BUILD_DIR/architecture.md and $BUILD_DIR/verified-design.md, write FIRST-compliant tests under tests/ against the designed interfaces, run the tests and confirm they FAIL because the implementation is still missing, and write $BUILD_DIR/test-report.md. Do NOT implement logic in src/. Finish by printing only the output path and 'RED — N tests failing as expected'."

D_IMPL="Execute the Implementer stage (TDD GREEN). Read $BUILD_DIR/architecture.md, $BUILD_DIR/verified-design.md, $BUILD_DIR/test-report.md, and the tests under tests/. Replace the stub bodies under src/expense_splitter/ with minimal correct implementations so all tests pass, run the tests until GREEN, and write $BUILD_DIR/implementation-summary.md. Do NOT edit anything under tests/. Finish by printing only the output path and the Overall Status."

D_SEC="Execute the Security Verifier stage. Read $BUILD_DIR/implementation-summary.md and $BUILD_DIR/architecture.md and the implemented files under src/, confirm the Architect's security-sensitive requirement is honored, scan for injection/secrets/insecure-comparisons/missing-validation/unsafe-deps, and write $BUILD_DIR/security-report.md ONLY. Do NOT modify code. Finish by printing only the output path and a severity summary."

run_one() {
  case "$1" in
    architect)         run_stage "Architect"               agents/architect.agent.md           "$D_ARCH"   "$ARCH_TOOLS" ;;
    design-verifier)   run_stage "Design Verifier"         agents/research-verifier.agent.md   "$D_DESIGN" "$RO_TOOLS" ;;
    test-author)       run_stage "Unit Test Generator RED" agents/unit-test-generator.agent.md "$D_TEST"   "$RW_TOOLS" ;;
    implementer)       run_stage "Implementer GREEN"       agents/bug-fixer.agent.md           "$D_IMPL"   "$RW_TOOLS" ;;
    security-verifier) run_stage "Security Verifier"       agents/security-verifier.agent.md   "$D_SEC"    "$RO_TOOLS" ;;
    *) echo "Unknown stage: $1" >&2; exit 2 ;;
  esac
}

# ----- orchestration ---------------------------------------------------------
log "Architect-Led TDD Build Pipeline — $(uname -s) — root: $ROOT"
log "Python for tests: $PYTHON   |   mode: ${ONLY:+only=$ONLY }$MODE"

if [ -n "$ONLY" ]; then
  run_one "$ONLY"
  exit 0
fi

case "$MODE" in
  gate)
    run_one architect
    log ""
    log "=================================================================="
    log "PLAN GATE — the Architect finished. Review the plan now:"
    log "   $BUILD_DIR/architecture.md   (+ the stub files under src/)"
    log "When you are satisfied, continue the pipeline with:"
    log "   ./run-pipeline.sh --continue"
    log "=================================================================="
    exit 0
    ;;
  continue)
    run_one design-verifier
    run_one test-author
    run_one implementer
    run_one security-verifier
    ;;
  all)
    run_one architect
    run_one design-verifier
    run_one test-author
    run_one implementer
    run_one security-verifier
    ;;
esac

log ""
log "=================================================================="
log "PIPELINE COMPLETE. Artifacts in $BUILD_DIR:"
for f in architecture.md verified-design.md test-report.md implementation-summary.md security-report.md; do
  if [ -f "$BUILD_DIR/$f" ]; then log "   [ok]   $BUILD_DIR/$f"; else log "   [MISS] $BUILD_DIR/$f"; fi
done
log "Run '$PYTHON -m pytest' to confirm the build is green."
