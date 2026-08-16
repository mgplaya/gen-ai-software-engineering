#!/usr/bin/env bash
# PreToolUse hook: block `git push` when test coverage is below threshold.
#
# Reads the hook JSON payload from stdin, extracts .tool_input.command, and
# tokenizes it (shell-aware, via python3's shlex) to decide whether it is a
# `git push` invocation — not a naive substring match, so it correctly
# handles `git -C <dir> push`, extra whitespace, and does not false-positive
# on commands that merely mention "git push" inside a quoted string (e.g. a
# commit message). Non-push commands pass through instantly. On a real push,
# runs the test suite with coverage and blocks (exit 2) if coverage is below
# COVERAGE_GATE_MIN (default 80). Fails closed: if the gate cannot even set
# up its own environment (e.g. project dir missing), it blocks rather than
# silently letting the push through.

set -u

INPUT="$(cat)"

VERDICT="$(printf '%s' "$INPUT" | python3 -c '
import json, sys, shlex

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

command = data.get("tool_input", {}).get("command", "") if isinstance(data, dict) else ""

try:
    tokens = shlex.split(command, posix=True)
except ValueError:
    tokens = []  # unbalanced quotes etc. -> treat as "not a push"

is_push = False
n = len(tokens)
for i, tok in enumerate(tokens):
    if tok != "git":
        continue
    # BFS over interpretations of the flags between "git" and its
    # subcommand. Rather than whitelisting every arg-taking git flag
    # (-C, -c, --git-dir, --work-tree, --namespace, ...), treat any
    # unrecognized "-"-prefixed token ambiguously: it might be a bare
    # flag (subcommand is the very next token) or it might consume the
    # next token as its argument (subcommand is two tokens over). If
    # ANY interpretation reaches "push" as the first non-flag token,
    # call it a push -- this fails closed on ambiguity instead of
    # silently skipping the gate for flags we did not anticipate.
    worklist = [i + 1]
    visited = set()
    while worklist:
        idx = worklist.pop()
        if idx in visited or idx >= n:
            continue
        visited.add(idx)
        t = tokens[idx]
        if not t.startswith("-"):
            if t == "push":
                is_push = True
            continue  # first non-flag token is decisive; this path ends here
        if "=" in t:
            worklist.append(idx + 1)  # --flag=value form takes no extra token
        else:
            worklist.append(idx + 1)  # interpretation: bare/boolean flag
            worklist.append(idx + 2)  # interpretation: flag consumes next token
    if is_push:
        break

print("PUSH" if is_push else "SKIP")
' 2>/dev/null)"

if [ "$VERDICT" != "PUSH" ]; then
    exit 0
fi

MIN="${COVERAGE_GATE_MIN:-80}"

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
if ! cd "$PROJECT_DIR"; then
    echo "BLOCKED: coverage gate could not enter project dir $PROJECT_DIR" >&2
    exit 2
fi

LOG_FILE="$(mktemp)" || {
    echo "BLOCKED: coverage gate could not create a temp log file" >&2
    exit 2
}
trap 'rm -f "$LOG_FILE"' EXIT

if uv run pytest --cov=agents --cov=pipeline --cov=mcp --cov=integrator --cov-fail-under="$MIN" -q >"$LOG_FILE" 2>&1; then
    echo "coverage gate passed (>= ${MIN}%) — push allowed"
    exit 0
else
    {
        echo "BLOCKED: test coverage below ${MIN}% — git push denied."
        echo "---- last 20 lines of pytest --cov output ----"
        tail -n 20 "$LOG_FILE"
    } >&2
    exit 2
fi
