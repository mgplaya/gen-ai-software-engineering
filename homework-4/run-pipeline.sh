#!/usr/bin/env bash
#
# run-pipeline.sh — thin engine for the agentic TDD build workflow.
#
# The WORKFLOW itself (ordered stages, per-stage tools, the human gate) is declared
# in ./pipeline.yaml. This script just reads that file and runs each stage via the
# Claude Code CLI headless (`claude -p`), auto-loading each agent's skills.
#
# Per stage: the model comes from the agent file frontmatter (agents/*.agent.md),
# the skills come from that file's `skills:` list, and the tool boundary comes from
# pipeline.yaml. A stage with `gate_after: true` stops the run for human plan
# verification; `--continue` resumes with the following stage.
#
# Usage:
#   ./run-pipeline.sh                 # run up to and including the gated stage, then STOP
#   ./run-pipeline.sh --continue      # run the stages after the gate
#   ./run-pipeline.sh --all           # run every stage, ignoring the gate
#   ./run-pipeline.sh --only <id>     # run one stage by its pipeline.yaml id
#   ./run-pipeline.sh --list          # list the workflow stages and exit
#   ./run-pipeline.sh --dry-run       # print what would run without calling the CLI
#   ./run-pipeline.sh -h | --help
#
set -euo pipefail

ROOT="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

WORKFLOW="pipeline.yaml"
BUILD_DIR="context/bugs/001"
LOG="$BUILD_DIR/pipeline-run.log"
DRY_RUN=false
MODE="gate"      # gate | continue | all | only | list
ONLY=""

if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON="$ROOT/.venv/bin/python"; else PYTHON="python3"; fi
export PYTHON

while [ $# -gt 0 ]; do
  case "$1" in
    --continue) MODE="continue"; shift ;;
    --all)      MODE="all"; shift ;;
    --only)     MODE="only"; ONLY="${2:-}"; shift 2 ;;
    --list)     MODE="list"; shift ;;
    --dry-run)  DRY_RUN=true; shift ;;
    -h|--help)  sed -n '2,26p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

command -v claude >/dev/null 2>&1 || { echo "ERROR: 'claude' CLI not found on PATH." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 needed to parse $WORKFLOW." >&2; exit 1; }
[ -f "$WORKFLOW" ] || { echo "ERROR: workflow file '$WORKFLOW' not found." >&2; exit 1; }
mkdir -p "$BUILD_DIR"

log() { printf '%s\n' "$*" | tee -a "$LOG"; }
model_of()  { grep -m1 '^model:' "$1" | sed 's/^model:[[:space:]]*//'; }
skills_of() { { grep -oE 'skills/[A-Za-z0-9._-]+\.md' "$1" || true; } | sort -u; }

# ----- parse the declarative workflow ----------------------------------------
# Emits one TAB-separated record per stage: id  name  agent  tools  gate_after  goal
parse_workflow() {
  python3 - "$WORKFLOW" <<'PY'
import sys, re
stages, cur = [], None
for raw in open(sys.argv[1], encoding="utf-8"):
    line = raw.rstrip("\n")
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    m = re.match(r'^\s*-\s*id:\s*(.*)$', line)
    if m:
        if cur: stages.append(cur)
        cur = {"id": m.group(1).strip()}
        continue
    m = re.match(r'^\s*(name|agent|tools|gate_after|goal):\s*(.*)$', line)
    if m and cur is not None:
        k, v = m.group(1), m.group(2).strip()
        if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
            v = v[1:-1]
        cur[k] = v
if cur: stages.append(cur)
for s in stages:
    print("\t".join([s.get("id",""), s.get("name",""), s.get("agent",""),
                     s.get("tools",""), s.get("gate_after","false"), s.get("goal","")]))
PY
}

# Load stages into parallel arrays (process substitution keeps them in this shell).
S_ID=(); S_NAME=(); S_AGENT=(); S_TOOLS=(); S_GATE=(); S_GOAL=()
GATE_IDX=-1
while IFS=$'\t' read -r sid sname sagent stools sgate sgoal; do
  [ -z "$sid" ] && continue
  S_ID+=("$sid"); S_NAME+=("$sname"); S_AGENT+=("$sagent")
  S_TOOLS+=("$stools"); S_GATE+=("$sgate"); S_GOAL+=("$sgoal")
  if [ "$sgate" = "true" ] && [ "$GATE_IDX" -lt 0 ]; then GATE_IDX=$(( ${#S_ID[@]} - 1 )); fi
done < <(parse_workflow)

N=${#S_ID[@]}
[ "$N" -gt 0 ] || { echo "ERROR: no stages parsed from $WORKFLOW." >&2; exit 1; }
LAST=$(( N - 1 ))
[ "$GATE_IDX" -lt 0 ] && GATE_IDX=$LAST   # no gate declared -> behave as one run

# ----- run one stage by index ------------------------------------------------
run_index() {
  local i="$1"
  local name="${S_NAME[$i]}" agent="${S_AGENT[$i]}" tools="${S_TOOLS[$i]}" goal="${S_GOAL[$i]}"
  [ -f "$agent" ] || { echo "ERROR: agent file '$agent' (stage ${S_ID[$i]}) not found." >&2; exit 1; }
  local model; model="$(model_of "$agent")"

  log ""
  log "=================================================================="
  log ">> STAGE $((i+1))/$N: $name   (model: $model)"
  log "=================================================================="

  local sysfile; sysfile="$(mktemp -t pipeline-sys.XXXXXX)"
  {
    echo "You are running as a single pipeline stage. Follow the agent definition"
    echo "below exactly. Your working directory is: $ROOT"
    echo "Use '$PYTHON -m pytest' as the test command."
    echo
    echo "===== AGENT DEFINITION ($agent) ====="
    cat "$agent"
    local skill
    for skill in $(skills_of "$agent"); do
      echo; echo "===== AUTO-LOADED SKILL ($skill) ====="; cat "$skill"
    done
  } > "$sysfile"

  local sk; sk="$(skills_of "$agent" | tr '\n' ' ')"
  log "   auto-loaded skills: ${sk:-(none)}"
  log "   allowed tools: $tools"

  local directive="Execute the '$name' stage now, following the agent definition exactly. Working directory: $ROOT. Stage goal: $goal Read your declared input artifacts, do your work, and write your declared output artifact under $BUILD_DIR. Use '$PYTHON -m pytest' as the test command. Finish by printing only your output artifact path and a one-line status."

  if $DRY_RUN; then
    log "   [dry-run] claude -p --model $model --allowedTools \"$tools\" (sys prompt: $(wc -l <"$sysfile") lines)"
    rm -f "$sysfile"; return 0
  fi

  set +e
  claude -p "$directive" \
    --model "$model" \
    --append-system-prompt-file "$sysfile" \
    --add-dir "$ROOT" \
    --permission-mode acceptEdits \
    --allowedTools "$tools" 2>&1 | tee -a "$LOG"
  local rc=${PIPESTATUS[0]}
  set -e
  rm -f "$sysfile"

  if [ "$rc" -ne 0 ]; then
    log ""; log "!! STAGE FAILED: $name (exit $rc). Pipeline halted."; exit "$rc"
  fi
  log "<< STAGE OK: $name"
}

index_of() {  # id -> index (or -1)
  local want="$1" i
  for i in $(seq 0 $LAST); do [ "${S_ID[$i]}" = "$want" ] && { echo "$i"; return; }; done
  echo "-1"
}

run_range() { local i; for i in $(seq "$1" "$2"); do run_index "$i"; done; }

# ----- list mode -------------------------------------------------------------
if [ "$MODE" = "list" ]; then
  echo "Workflow: $WORKFLOW  ($N stages; human gate after stage $((GATE_IDX+1)))"
  for i in $(seq 0 $LAST); do
    printf "  %d. %-28s model=%-28s tools=[%s]%s\n" \
      "$((i+1))" "${S_ID[$i]}" "$(model_of "${S_AGENT[$i]}")" "${S_TOOLS[$i]}" \
      "$([ "${S_GATE[$i]}" = "true" ] && echo "  <-- GATE (stop for human verify)")"
  done
  exit 0
fi

: > "$LOG"
log "Agentic TDD Build Pipeline — engine over $WORKFLOW — $(uname -s)"
log "Python for tests: $PYTHON   |   stages: $N   |   gate after: $((GATE_IDX+1))   |   mode: ${ONLY:+only=$ONLY }$MODE"

case "$MODE" in
  only)
    idx="$(index_of "$ONLY")"
    [ "$idx" -ge 0 ] || { echo "Unknown stage id: $ONLY (see --list)" >&2; exit 2; }
    run_index "$idx"
    ;;
  gate)
    run_range 0 "$GATE_IDX"
    if [ "$GATE_IDX" -lt "$LAST" ]; then
      log ""
      log "=================================================================="
      log "PLAN GATE — stage '${S_ID[$GATE_IDX]}' finished. Verify the plan now:"
      log "   $BUILD_DIR/research/codebase-research.md   (the bugs)"
      log "   $BUILD_DIR/implementation-plan.md          (the proposed fixes)"
      log "When satisfied, continue with:  ./run-pipeline.sh --continue"
      log "=================================================================="
      exit 0
    fi
    ;;
  continue)
    if [ "$GATE_IDX" -ge "$LAST" ]; then log "No gate in workflow; nothing to continue."; exit 0; fi
    run_range $(( GATE_IDX + 1 )) "$LAST"
    ;;
  all)
    run_range 0 "$LAST"
    ;;
esac

log ""
log "=================================================================="
log "PIPELINE COMPLETE. Artifacts in $BUILD_DIR:"
for f in research/codebase-research.md implementation-plan.md research/verified-research.md test-report.md fix-summary.md security-report.md; do
  if [ -f "$BUILD_DIR/$f" ]; then log "   [ok]   $BUILD_DIR/$f"; else log "   [MISS] $BUILD_DIR/$f"; fi
done
log "Run '$PYTHON -m pytest' to confirm the build is green."
