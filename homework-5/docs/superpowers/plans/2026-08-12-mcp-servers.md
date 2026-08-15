# Homework 5 — MCP Server Configuration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configure three external MCP servers (GitHub, Filesystem, Jira) and build one custom FastMCP server, with captured evidence of a working interaction against each.

**Architecture:** A single `.mcp.json` at `homework-5/` registers all four servers — two remote HTTP servers (one OAuth, one header-authenticated), one stdio server via `npx`, and one stdio server running local Python through `uv`. The custom server keeps one private helper (`_read_words`) as the single source of truth, with two resource URIs and one tool delegating to it, so word-limiting logic is tested once and exposed three ways.

**Tech Stack:** Python 3.10+, FastMCP 3.4.7, `uv`, pytest, Node/`npx` (filesystem server), Claude Code MCP client.

## Progress (updated 2026-08-12)

| Task | Status |
|---|---|
| 1. Custom server core (`_read_words`) | ✅ committed `a809525` — 11 tests |
| 2. MCP surface (2 resources + `read` tool) | ✅ committed `3124315` — 13 tests total, all passing |
| 3. `.mcp.json` with four servers | ✅ committed `115d9a5`, amended `ea2adcf` (header auth) and `2e113a2` (read-only header) |
| 4. Live interactions + screenshots | 🟨 all four interactions run live and transcribed in `docs/mcp-transcripts.md`; screenshots `01`–`02` filed, `03` withheld by author decision (see amendment), `04` pending capture |
| 5. Documentation (README, HOWTORUN) | ✅ committed `4e3db44`, fixed `0dddedb`; `.env.example` in `49d30d1` |
| 6. Pull request | ⬜ `docs/PR_DESCRIPTION.md` written; PR not yet opened (needs Task 4's screenshots) |

> **Amendment (2026-08-15, decided by the author).** **Screenshot `03` (Jira) will not be
> captured, and the issue keys are masked as `AI20-XXXX` in every committed file.** The
> project queried is a production Jira holding customer and colleague data, and the Atlassian
> server returns full issue bodies regardless of the `fields` projection, so no capture
> technique can be trusted to stay clean. Task 3's success criteria do ask for a screenshot
> and do permit ticket numbers to stand in for the response; the author was shown that
> trade-off and chose maximum confidentiality over the credit at stake. `docs/mcp-transcripts.md`
> section 3 therefore records the request, the masked response shape (five `Bug` issues in
> descending `created` order), and the reasoning. Steps 4 and 7 of this task are superseded
> accordingly: three screenshots, not four.

**Task 4 unblocked (2026-08-12).** A session launched from `homework-5/` exposed all four
servers; `atlassian` was authenticated mid-session via `/mcp`. All four interactions ran and
match the expectations recorded below. One deviation was found and documented rather than
worked around: the `filesystem` server's effective allowed directory is `homework-5`, not the
repository root that `.mcp.json` passes on the command line, because Claude Code advertises
its working directory as an MCP *root* and the filesystem server prefers client roots over
its CLI argument. Step 3's expected repo-root listing is therefore unreachable from this
session; the interaction was performed on the `homework-5` tree instead, which still meets
the assignment's bar ("a path to a directory (e.g. a project folder)" plus one successful
interaction). README, HOWTORUN, and the PR body were corrected to match.

**Historical note — why Task 4 was blocked:** the four servers are project-scoped to `homework-5/.mcp.json`, which
Claude Code loads only when launched from that directory. A session started at the repo root
cannot call them — the `mcp__github__*`, `mcp__filesystem__*`, and `mcp__lorem-ipsum__*` tools
are simply absent, and adding them mid-session does not help because a restart is required
either way. Task 4 must therefore run in a session started as:

```bash
export GITHUB_MCP_TOKEN=$(gh auth token)
cd homework-5 && claude
```

**Pre-verified, so the restarted session does not have to rediscover it:**

- `uv run pytest -q` in `custom-mcp-server/` → `13 passed`.
- GitHub MCP header auth works: a direct `initialize` POST with `Authorization: Bearer $(gh auth token)` and `X-MCP-Readonly: true` returns the server's capabilities.
- `filesystem` and `lorem-ipsum` both report `✔ Connected` from `claude mcp list`.
- The Jira "last 5 bugs" query returns the five keys listed in Task 4 Step 4 (confirmed live).
- `github` reports `✘ Failed to connect … Authorization header is badly formatted` whenever `GITHUB_MCP_TOKEN` is unset — that is the missing-env-var symptom, not a config error.

## Global Constraints

- **Working directory** for all commands: `/Users/gorishnyi/development/education/set/gen-ai-software-engineering` (the repo root). The homework lives in `homework-5/`.
- **Branch:** `homework-5-submission`. Already created and checked out. Do not commit to `main`.
- **Jira is read-only.** No `createJiraIssue`, `editJiraIssue`, `transitionJiraIssue`, `addCommentToJiraIssue`, or `addWorklogToJiraIssue`. Search and read only.
- **GitHub is read-only.** List PRs / commits / issues only. No creation via MCP.
- **No credentials in git.** No PAT, token, or secret in any committed file. `atlassian` authenticates by OAuth. `github` authenticates by an `Authorization` header that references the `${GITHUB_MCP_TOKEN}` environment variable — the variable *name* is committed, never its value.

> **Amendment (2026-08-12, ratified by the author).** The plan originally specified OAuth for `github`. GitHub's auth server rejects Claude Code's dynamic client registration (`✘ Failed to connect — Incompatible auth server: does not support dynamic client registration`), so OAuth is not achievable for this server. The author chose header auth sourced from the existing `gh` CLI login. Verified working: a direct `initialize` POST to `https://api.githubcopilot.com/mcp/` with `Authorization: Bearer $(gh auth token)` returns the server's capabilities.
- **Dependency floor:** `fastmcp>=3.4.7`, `requires-python = ">=3.10"`.
- **Paths in `.mcp.json`** use `${HOME}/development/education/set/gen-ai-software-engineering/...`, never a hardcoded `/Users/gorishnyi`.
- **Jira output redaction:** issue keys and creation dates only. No summaries, descriptions, assignees, reporters, or comments in any committed file or screenshot.
- **Author name** in all docs: Mykhailo Gorishnyi (`mgplaya`).

## File Structure

| File | Responsibility |
|---|---|
| `homework-5/.mcp.json` | Registers all four MCP servers |
| `homework-5/custom-mcp-server/pyproject.toml` | Deps (`fastmcp`), Python floor, pytest config |
| `homework-5/custom-mcp-server/lorem-ipsum.md` | Source prose the resource reads (272 words) |
| `homework-5/custom-mcp-server/server.py` | `_read_words` helper + 2 resources + `read` tool |
| `homework-5/custom-mcp-server/tests/test_read_words.py` | Unit tests for the helper |
| `homework-5/custom-mcp-server/tests/test_mcp_surface.py` | In-memory integration tests through a FastMCP `Client` |
| `homework-5/README.md` | Author, description, resources-vs-tools explainer, server table |
| `homework-5/HOWTORUN.md` | Install / run / connect / test instructions |
| `homework-5/docs/mcp-transcripts.md` | Text request+response per server, backing the screenshots |
| `homework-5/docs/PR_DESCRIPTION.md` | PR body |
| `homework-5/docs/screenshots/*.png` | Four captured MCP results |

**Verified API facts** (checked against a live FastMCP 3.4.7 prototype, not assumed):

- `@mcp.tool` works as a bare decorator (its first parameter is `name_or_fn`).
- `@mcp.resource(uri)` requires the URI positionally.
- A static URI appears in `list_resources()`; a `{param}` URI appears in `list_resource_templates()` under `.uriTemplate`, **not** in `list_resources()`.
- FastMCP coerces the URI path segment to the annotated type, so `lorem://ipsum/5` yields `word_count=5` as an `int`.
- **A `ValueError` raised inside a tool reaches the client as `fastmcp.exceptions.ToolError`, not `ValueError`.** Unit tests asserting `ValueError` must call `_read_words` directly rather than going through a `Client`.
- `client.read_resource(uri)` returns a list; use `[0].text`. `client.call_tool(...)` returns a result object; use `.content[0].text`.

---

### Task 1: Custom server core — the `_read_words` helper

Scaffolds the package and builds the word-limiting logic under TDD. Nothing MCP-specific yet, so the logic is tested in isolation.

**Files:**
- Create: `homework-5/custom-mcp-server/pyproject.toml`
- Create: `homework-5/custom-mcp-server/lorem-ipsum.md`
- Create: `homework-5/custom-mcp-server/server.py`
- Test: `homework-5/custom-mcp-server/tests/test_read_words.py`

**Interfaces:**
- Consumes: nothing (first task).
- Produces: `server._read_words(word_count: int = 30) -> str`, the module constants `server.DEFAULT_WORD_COUNT: int = 30` and `server.LOREM_PATH: pathlib.Path`. Task 2 wraps these.

- [ ] **Step 1: Create the package scaffold**

Create `homework-5/custom-mcp-server/pyproject.toml`:

```toml
[project]
name = "lorem-ipsum-mcp"
version = "1.0.0"
description = "Custom FastMCP server exposing lorem-ipsum.md as an MCP resource and a read tool"
requires-python = ">=3.10"
dependencies = ["fastmcp>=3.4.7"]

[dependency-groups]
dev = ["pytest>=8.0"]

[tool.uv]
# Not an installable package — uv only needs to resolve dependencies.
package = false

[tool.pytest.ini_options]
# Lets tests/ import server.py without an installed package.
pythonpath = ["."]
testpaths = ["tests"]
```

`package = false` matters: without it `uv run` tries to build `lorem-ipsum-mcp` as a distribution and fails, since there is no build backend.

- [ ] **Step 2: Create the source text**

Create `homework-5/custom-mcp-server/lorem-ipsum.md` with exactly this content. **No markdown heading** — the file is read by whitespace-splitting, so a `# Lorem Ipsum` title would make `#`, `Lorem`, and `Ipsum` the first three "words" of every response.

```markdown
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium
doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore
veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam
voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur
magni dolores eos qui ratione voluptatem sequi nesciunt.

Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur,
adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et
dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum
exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi
consequatur.

At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis
praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias
excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui
officia deserunt mollitia animi, id est laborum et dolorum fuga.

Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore,
cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod
maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor
repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum
necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non
recusandae.
```

This is 272 whitespace-separated words, so a request for 30, 50, or 100 all return partial content and the clamp test has headroom.

- [ ] **Step 3: Write the failing tests**

Create `homework-5/custom-mcp-server/tests/test_read_words.py`:

```python
"""Unit tests for the word-limiting helper behind the resource and tool."""

import pytest

from server import DEFAULT_WORD_COUNT, LOREM_PATH, _read_words

TOTAL_WORDS = len(LOREM_PATH.read_text(encoding="utf-8").split())


def test_source_file_exists():
    assert LOREM_PATH.is_file(), f"missing source text at {LOREM_PATH}"


def test_default_is_thirty_words():
    assert DEFAULT_WORD_COUNT == 30
    assert len(_read_words().split()) == 30


@pytest.mark.parametrize("count", [1, 10, 50, 100])
def test_explicit_count_returns_exactly_that_many_words(count):
    assert len(_read_words(count).split()) == count


def test_count_beyond_file_length_clamps_to_whole_file():
    assert len(_read_words(TOTAL_WORDS + 500).split()) == TOTAL_WORDS


@pytest.mark.parametrize("bad_count", [0, -1, -100])
def test_non_positive_count_raises(bad_count):
    with pytest.raises(ValueError, match="at least 1"):
        _read_words(bad_count)


def test_output_starts_at_the_beginning_of_the_source():
    assert _read_words(3) == "Lorem ipsum dolor"
```

The clamp test derives `TOTAL_WORDS` from the file instead of hardcoding 272, so editing the prose later does not break the suite.

- [ ] **Step 4: Run the tests to verify they fail**

```bash
cd homework-5/custom-mcp-server && uv run pytest -v
```

Expected: collection error — `ModuleNotFoundError: No module named 'server'`.

- [ ] **Step 5: Write the minimal implementation**

Create `homework-5/custom-mcp-server/server.py`:

```python
"""Custom MCP server exposing lorem-ipsum.md as a resource and a read tool."""

from pathlib import Path

DEFAULT_WORD_COUNT = 30
LOREM_PATH = Path(__file__).parent / "lorem-ipsum.md"


def _read_words(word_count: int = DEFAULT_WORD_COUNT) -> str:
    """Return the first `word_count` whitespace-separated words of the source text.

    Single source of truth for both resources and the `read` tool. A request for
    more words than the file holds returns the whole file rather than erroring.
    """
    if word_count < 1:
        raise ValueError(f"word_count must be at least 1, got {word_count}")
    if not LOREM_PATH.is_file():
        raise FileNotFoundError(f"Source text not found: {LOREM_PATH}")
    words = LOREM_PATH.read_text(encoding="utf-8").split()
    return " ".join(words[:word_count])
```

- [ ] **Step 6: Run the tests to verify they pass**

```bash
cd homework-5/custom-mcp-server && uv run pytest -v
```

Expected: PASS — **11 passed** (1 file-exists + 1 default + 4 parametrized counts + 1 clamp + 3 parametrized invalid + 1 prefix).

If `uv` prints `warning: VIRTUAL_ENV=.../homework-4/.venv does not match the project environment path`, that is harmless — it means homework-4's virtualenv is active in the shell. `uv` correctly ignores it and uses this project's own environment.

- [ ] **Step 7: Commit**

```bash
cd /Users/gorishnyi/development/education/set/gen-ai-software-engineering
git add homework-5/custom-mcp-server
git commit -m "feat(hw5): add word-limiting helper for custom MCP server

Scaffolds the lorem-ipsum-mcp package (uv + pyproject) and implements
_read_words under TDD: default 30, exact counts, clamp beyond file
length, ValueError on non-positive input."
```

---

### Task 2: MCP surface — two resources and the `read` tool

Wraps the tested helper in FastMCP registrations and proves them through an in-memory client, which exercises the real MCP protocol without spawning a subprocess.

**Files:**
- Modify: `homework-5/custom-mcp-server/server.py` (append registrations)
- Test: `homework-5/custom-mcp-server/tests/test_mcp_surface.py`

**Interfaces:**
- Consumes: `server._read_words`, `server.DEFAULT_WORD_COUNT` from Task 1.
- Produces: `server.mcp` (a `FastMCP` instance named `"lorem-ipsum"`), the resource URIs `lorem://ipsum` and `lorem://ipsum/{word_count}`, and the tool `read(word_count: int = 30) -> str`. Task 3 launches this module over stdio; Task 4 calls the `read` tool by name.

- [ ] **Step 1: Write the failing integration tests**

Create `homework-5/custom-mcp-server/tests/test_mcp_surface.py`:

```python
"""Integration tests driving the server through an in-memory MCP client."""

import asyncio

from fastmcp import Client

from server import mcp


def test_tool_and_resources_are_registered():
    async def scenario():
        async with Client(mcp) as client:
            tools = await client.list_tools()
            resources = await client.list_resources()
            templates = await client.list_resource_templates()
            return (
                [t.name for t in tools],
                [str(r.uri) for r in resources],
                [t.uriTemplate for t in templates],
            )

    tool_names, resource_uris, template_uris = asyncio.run(scenario())
    assert tool_names == ["read"]
    assert "lorem://ipsum" in resource_uris
    assert "lorem://ipsum/{word_count}" in template_uris


def test_resources_and_tool_return_word_limited_text():
    async def scenario():
        async with Client(mcp) as client:
            static = await client.read_resource("lorem://ipsum")
            templated = await client.read_resource("lorem://ipsum/5")
            tool_default = await client.call_tool("read", {})
            tool_explicit = await client.call_tool("read", {"word_count": 10})
            return (
                static[0].text,
                templated[0].text,
                tool_default.content[0].text,
                tool_explicit.content[0].text,
            )

    static, templated, tool_default, tool_explicit = asyncio.run(scenario())
    assert len(static.split()) == 30
    assert templated == "Lorem ipsum dolor sit amet,"
    assert len(tool_default.split()) == 30
    assert len(tool_explicit.split()) == 10
    assert tool_explicit.startswith("Lorem ipsum dolor")
```

Note the assertion style: the templated resource is checked against exact text because the URI path segment is coerced to `int` by FastMCP, and that coercion is the thing worth pinning down.

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd homework-5/custom-mcp-server && uv run pytest tests/test_mcp_surface.py -v
```

Expected: collection error — `ImportError: cannot import name 'mcp' from 'server'`.

- [ ] **Step 3: Add the FastMCP registrations**

In `homework-5/custom-mcp-server/server.py`, add the import and instance near the top:

```python
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("lorem-ipsum")

DEFAULT_WORD_COUNT = 30
LOREM_PATH = Path(__file__).parent / "lorem-ipsum.md"
```

Then append below `_read_words`:

```python
@mcp.resource("lorem://ipsum")
def lorem_ipsum_default() -> str:
    """The first 30 words of the source text (the default slice)."""
    return _read_words()


@mcp.resource("lorem://ipsum/{word_count}")
def lorem_ipsum_n(word_count: int) -> str:
    """The first `word_count` words of the source text."""
    return _read_words(word_count)


@mcp.tool
def read(word_count: int = DEFAULT_WORD_COUNT) -> str:
    """Read the lorem ipsum source, limited to `word_count` words (default 30)."""
    return _read_words(word_count)


if __name__ == "__main__":
    mcp.run()
```

Two registrations are needed because a URI template cannot express a default: `lorem://ipsum` *is* the default-30 case, and `lorem://ipsum/{word_count}` covers any other count.

- [ ] **Step 4: Run the full suite to verify it passes**

```bash
cd homework-5/custom-mcp-server && uv run pytest -v
```

Expected: PASS — **13 passed** (11 from Task 1, 2 from this task).

- [ ] **Step 5: Verify the server starts and speaks MCP over stdio**

Do **not** use `timeout` — it is not installed on macOS. Do not pipe `echo ''` either; a bare newline is invalid JSON-RPC and the server will log a parse error that looks like a real failure.

First, confirm a clean startup and shutdown:

```bash
cd homework-5/custom-mcp-server
uv run server.py < /dev/null 2>&1 | grep -Ei 'error|exception|Traceback' && echo "FAILED" || echo "clean startup"
```

Expected: `clean startup`.

Then drive a real handshake. The trailing `sleep 2` matters — without it stdin closes before the server answers `tools/list`, and the response is silently lost:

```bash
cd homework-5/custom-mcp-server
{ printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"1.0"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'; sleep 2; } \
  | uv run server.py 2>/dev/null | cut -c1-160
```

Expected: two JSON-RPC result lines — `id:1` reporting `"serverInfo":{"name":"lorem-ipsum",...}`, and `id:2` listing the `read` tool.

- [ ] **Step 6: Commit**

```bash
cd /Users/gorishnyi/development/education/set/gen-ai-software-engineering
git add homework-5/custom-mcp-server
git commit -m "feat(hw5): expose lorem ipsum as MCP resources and read tool

Adds a static lorem://ipsum resource (default 30 words), a templated
lorem://ipsum/{word_count} resource, and the read tool, all delegating
to _read_words. Covered by in-memory MCP client integration tests."
```

---

### Task 3: Register all four servers in `.mcp.json`

**Files:**
- Create: `homework-5/.mcp.json`

**Interfaces:**
- Consumes: the `uv run server.py` entrypoint from Task 2.
- Produces: four registered server names — `github`, `filesystem`, `atlassian`, `lorem-ipsum` — which Task 4 calls tools against.

- [ ] **Step 1: Write the configuration**

Create `homework-5/.mcp.json`:

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_MCP_TOKEN}"
      }
    },
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "${HOME}/development/education/set/gen-ai-software-engineering"
      ]
    },
    "atlassian": {
      "type": "http",
      "url": "https://mcp.atlassian.com/v1/mcp"
    },
    "lorem-ipsum": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "${HOME}/development/education/set/gen-ai-software-engineering/homework-5/custom-mcp-server",
        "run",
        "server.py"
      ]
    }
  }
}
```

Claude Code expands `${HOME}` and `${GITHUB_MCP_TOKEN}` in `command`, `args`, `url`, `headers`, and `env` values, which keeps the file portable and free of both a hardcoded `/Users/gorishnyi` and any literal secret. `atlassian` uses OAuth; `github` carries only the *name* of an environment variable.

- [ ] **Step 2: Validate the JSON parses**

```bash
cd /Users/gorishnyi/development/education/set/gen-ai-software-engineering
python3 -c "import json; d=json.load(open('homework-5/.mcp.json')); print(sorted(d['mcpServers']))"
```

Expected: `['atlassian', 'filesystem', 'github', 'lorem-ipsum']`

- [ ] **Step 3: Confirm no secrets are present**

```bash
grep -nEi 'token|secret|password|ghp_|Bearer' homework-5/.mcp.json; echo "matches: $?"
```

Expected: no output and `matches: 1` (grep found nothing).

- [ ] **Step 4: Verify the servers connect**

This requires a Claude Code session started in `homework-5/`, which will prompt to approve the project-scoped `.mcp.json`. Approve it, then:

```bash
claude mcp list
```

Expected: `filesystem` and `lorem-ipsum` report `✔ Connected`. `github` connects only when `GITHUB_MCP_TOKEN` is exported in the environment that launched Claude Code (see Task 4 Step 1). `atlassian` may report `! Needs authentication` until its OAuth flow is completed via `/mcp`.

- [ ] **Step 5: Commit**

```bash
cd /Users/gorishnyi/development/education/set/gen-ai-software-engineering
git add homework-5/.mcp.json
git commit -m "feat(hw5): register GitHub, Filesystem, Jira, and custom MCP servers

No credentials enter git: atlassian uses OAuth and github references
\${GITHUB_MCP_TOKEN} by name. \${HOME}-relative paths keep the config portable."
```

---

### Task 4: Live interactions and screenshot capture

**HUMAN-IN-THE-LOOP — do not delegate this task to a subagent.** It requires four screenshots taken by the author. Run it in the main session, pausing after each interaction.

**Files:**
- Create: `homework-5/docs/mcp-transcripts.md`
- Create: `homework-5/docs/screenshots/01-github-mcp-result.png` (author-captured)
- Create: `homework-5/docs/screenshots/02-filesystem-mcp-result.png` (author-captured)
- Create: `homework-5/docs/screenshots/03-jira-mcp-last-5-bugs.png` (author-captured)
- Create: `homework-5/docs/screenshots/04-custom-mcp-read-tool.png` (author-captured)

**Interfaces:**
- Consumes: the four server names registered in Task 3.
- Produces: four PNG files and `docs/mcp-transcripts.md`, both referenced by the README (Task 5) and the PR body (Task 6).

- [ ] **Step 1: Authenticate GitHub**

```bash
claude mcp list
```

`github` authenticates via the `GITHUB_MCP_TOKEN` environment variable, which must be exported in the shell that launches Claude Code:

```bash
export GITHUB_MCP_TOKEN=$(gh auth token)
```

If `atlassian` shows `! Needs authentication`, run `/mcp` and complete its OAuth flow. Re-run `claude mcp list` and confirm both report `✔ Connected` before continuing.

- [ ] **Step 2: GitHub interaction — list recent pull requests**

Call the GitHub MCP server's pull-request listing tool for owner `mgplaya`, repo `gen-ai-software-engineering`, state `all`. Expected (re-confirmed 2026-08-12): PRs **#1 through #8** — #8 "Add Claude Code GitHub Workflow", #7/#6/#5 the "Homework 4" revert chain, #4 and #3 Homework 3 (merged and closed), #2 Homework 2, #1 Homework 1. All merged except #3, which is closed.

**Pause.** Ask the author to screenshot the request and result, saving to `homework-5/docs/screenshots/01-github-mcp-result.png`. Confirm the file exists before moving on:

```bash
ls -la homework-5/docs/screenshots/01-github-mcp-result.png
```

- [ ] **Step 3: Filesystem interaction — summarize the repo structure**

Call the filesystem MCP server's directory-listing tool on `/Users/gorishnyi/development/education/set/gen-ai-software-engineering`. Expected: `homework-1` … `homework-6`, `README.md`, `recommended-agents-skills-pipelines.md`.

**Pause.** Screenshot to `homework-5/docs/screenshots/02-filesystem-mcp-result.png`, then verify:

```bash
ls -la homework-5/docs/screenshots/02-filesystem-mcp-result.png
```

- [ ] **Step 4: Jira interaction — the last 5 bugs**

Use the exact wording the assignment requires: *"Give me the tickets of the last 5 bugs on a project."*

Run it as a **read-only** JQL search against cloudId `77aec8f7-83e5-469a-b2f3-e8eb99cd64dd`:

- JQL: `issuetype = Bug AND project = AI20 ORDER BY created DESC`
- `maxResults`: 5
- `fields`: `["key", "created"]`

> **Amendment (2026-08-12, verified against the live server).** `fields` **does not restrict the
> response.** Passing `["key", "created"]` still returns `summary`, `description`, `assignee`
> (including work email addresses), and `status` for every issue — the Atlassian MCP server
> ignores the projection. Redaction therefore cannot be achieved by narrowing the request; it
> must be achieved at capture time. **The screenshot must show the prompt and Claude's
> keys-and-dates answer with the tool result collapsed** (Claude Code collapses tool output by
> default — do not expand it). Verify nothing confidential is on screen before capturing.

Expected keys and creation dates (confirmed live, 2026-08-12):

| Key | Created |
|---|---|
| `AI20-XXXX` | 2026-08-03 |
| `AI20-XXXX` | 2026-07-28 |
| `AI20-XXXX` | 2026-07-17 |
| `AI20-XXXX` | 2026-07-14 |
| `AI20-XXXX` | 2026-07-14 |

**Pause.** Screenshot to `homework-5/docs/screenshots/03-jira-mcp-last-5-bugs.png`. Before the author captures, confirm no issue summaries, descriptions, or assignee names are visible on screen. Then verify:

```bash
ls -la homework-5/docs/screenshots/03-jira-mcp-last-5-bugs.png
```

- [ ] **Step 5: Custom server interaction — the `read` tool**

Call the `lorem-ipsum` server's `read` tool twice: once with no arguments (expect exactly 30 words beginning "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor…"), then with `word_count: 10` (expect exactly `Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do`).

**Pause.** Screenshot both calls to `homework-5/docs/screenshots/04-custom-mcp-read-tool.png`, then verify:

```bash
ls -la homework-5/docs/screenshots/04-custom-mcp-read-tool.png
```

- [ ] **Step 6: Record the transcripts**

Create `homework-5/docs/mcp-transcripts.md` with one section per server, each containing the prompt issued, the tool invoked with its arguments, and the response — **redacted to the same standard as the screenshots** (Jira: keys and dates only).

Structure:

```markdown
# MCP Interaction Transcripts

Text record of each MCP call captured in `docs/screenshots/`.
Jira output is redacted to issue keys and creation dates, per the assignment's
instruction to represent the response using only ticket numbers.

## 1. GitHub MCP — recent pull requests
**Prompt:** ...
**Tool:** ...
**Response:** ...

## 2. Filesystem MCP — repository structure
...

## 3. Jira MCP (Atlassian) — last 5 bugs
...

## 4. Custom MCP (lorem-ipsum) — read tool
...
```

- [ ] **Step 7: Confirm all four screenshots landed**

```bash
cd /Users/gorishnyi/development/education/set/gen-ai-software-engineering
ls -la homework-5/docs/screenshots/
```

Expected: exactly four `.png` files, each non-zero in size. Do not proceed with a missing or empty file — the submission is rejected without them.

- [ ] **Step 8: Commit**

```bash
cd /Users/gorishnyi/development/education/set/gen-ai-software-engineering
git add homework-5/docs/screenshots homework-5/docs/mcp-transcripts.md
git commit -m "docs(hw5): capture MCP interaction results for all four servers

Screenshots and redacted text transcripts for GitHub (recent PRs),
Filesystem (repo structure), Jira (last 5 bugs, keys only), and the
custom lorem-ipsum read tool."
```

---

### Task 5: Documentation

**Files:**
- Create: `homework-5/README.md`
- Create: `homework-5/HOWTORUN.md`

**Interfaces:**
- Consumes: the server names from Task 3, the screenshot filenames from Task 4.
- Produces: docs referenced by the PR body in Task 6.

- [ ] **Step 1: Write `homework-5/README.md`**

Must contain, at minimum:

- Title and **author name: Mykhailo Gorishnyi (`mgplaya`)**, course name.
- A one-paragraph description of the work.
- A table of the four servers: name, transport, endpoint or command, auth method, and what was demonstrated.
- The **resources-vs-tools explainer** the assignment requires verbatim in substance:
  > **Resources** are URIs that Claude can read from (for example files or APIs). They are addressable and side-effect free.
  > **Tools** are actions Claude can call to perform an operation (for example reading a file or running a command).
- A short "Custom MCP server" section documenting `lorem://ipsum`, `lorem://ipsum/{word_count}`, and `read(word_count=30)`, including the clamp and `ValueError` behavior.
- Embedded screenshots, e.g. `![GitHub MCP](docs/screenshots/01-github-mcp-result.png)`.
- A link to `HOWTORUN.md`.

- [ ] **Step 2: Write `homework-5/HOWTORUN.md`**

Must cover the four things the assignment names — install, run, connect, test:

1. **Prerequisites:** Python ≥3.10, [`uv`](https://docs.astral.sh/uv/), Node.js (for `npx`), Claude Code.
2. **Install dependencies:** `cd homework-5/custom-mcp-server && uv sync`
3. **Run the server standalone:** `uv run server.py` (stdio; the banner confirms startup)
4. **Connect the MCP configuration:** start Claude Code from `homework-5/`, approve the project-scoped `.mcp.json`, run `claude mcp list` to confirm, and export `GITHUB_MCP_TOKEN=$(gh auth token)` before launching, and complete the Atlassian OAuth flow via `/mcp`. **State explicitly that a grader on a different machine must adjust the `${HOME}`-relative paths in `.mcp.json` if the repo lives elsewhere.**
5. **Test the `read` tool:** run `uv run pytest -v` for the automated suite, and ask Claude *"Use the lorem-ipsum read tool to get 10 words"* for a live check.
6. **Troubleshooting:**
   - `lorem-ipsum` failing to connect usually means `uv` is not on `PATH` for the MCP client.
   - `github` failing to connect almost always means `GITHUB_MCP_TOKEN` was not exported in the shell that launched Claude Code. Note that GitHub's auth server does not support Claude Code's dynamic client registration, so plain OAuth is not an option for this server.
   - `atlassian` showing `Needs authentication` means its OAuth flow has not been completed — run `/mcp` in Claude Code.
   - A `warning: VIRTUAL_ENV=... does not match the project environment path` from `uv` is harmless; it appears when another homework's virtualenv is active in the shell, and `uv` correctly ignores it.
   - `timeout: command not found` — `timeout` is not installed on macOS by default; use the `< /dev/null` form shown above instead.

- [ ] **Step 3: Verify every referenced path exists**

```bash
cd /Users/gorishnyi/development/education/set/gen-ai-software-engineering/homework-5
grep -oE '\(docs/screenshots/[^)]+\)' README.md | tr -d '()' | while read -r p; do
  [ -f "$p" ] && echo "OK   $p" || echo "MISS $p"
done
```

Expected: every line prefixed `OK`. Any `MISS` is a broken image in the graded README.

- [ ] **Step 4: Commit**

```bash
cd /Users/gorishnyi/development/education/set/gen-ai-software-engineering
git add homework-5/README.md homework-5/HOWTORUN.md
git commit -m "docs(hw5): add README and HOWTORUN

README documents all four servers, the resources-vs-tools distinction, and
the custom server's URIs. HOWTORUN covers install, run, connect, and test."
```

---

### Task 6: Pull request

**Files:**
- Create: `homework-5/docs/PR_DESCRIPTION.md`

**Interfaces:**
- Consumes: everything from Tasks 1–5.
- Produces: the submitted PR.

- [ ] **Step 1: Write `homework-5/docs/PR_DESCRIPTION.md`**

The course rejects bare or one-line PRs, so this must be substantial. Cover: what was built; a table of the four servers and what each demonstrated; the custom server's resources, tool, and edge-case behavior; how to run and test it; the four embedded screenshots; a note that Jira output is redacted to issue keys per the assignment; and a note that no credentials are committed — atlassian uses OAuth and github references `${GITHUB_MCP_TOKEN}` by name — and an explanation of why header auth replaced OAuth for GitHub.

- [ ] **Step 2: Confirm the working tree is clean and tests still pass**

```bash
cd /Users/gorishnyi/development/education/set/gen-ai-software-engineering
git status --short
cd homework-5/custom-mcp-server && uv run pytest -q
```

Expected: no unexpected untracked files; 13 tests pass.

- [ ] **Step 3: Commit and push**

```bash
cd /Users/gorishnyi/development/education/set/gen-ai-software-engineering
git add homework-5/docs/PR_DESCRIPTION.md
git commit -m "docs(hw5): add PR description"
git push -u origin homework-5-submission
```

- [ ] **Step 4: Open the pull request**

```bash
cd /Users/gorishnyi/development/education/set/gen-ai-software-engineering
gh pr create --base main --head homework-5-submission \
  --title "Homework 5: MCP server configuration (GitHub, Filesystem, Jira, custom FastMCP)" \
  --body-file homework-5/docs/PR_DESCRIPTION.md
```

- [ ] **Step 5: Verify the PR renders**

```bash
gh pr view --web
```

Confirm the four screenshots render in the PR body. Images referenced by relative path resolve on the branch, so check them rather than assuming.

---

## Self-Review

**Spec coverage** — every spec section maps to a task:

| Spec requirement | Task |
|---|---|
| GitHub MCP configured + interaction + screenshot | 3, 4 |
| Filesystem MCP configured + interaction + screenshot | 3, 4 |
| Jira MCP + "last 5 bugs" request + screenshot | 3, 4 |
| Custom FastMCP `server.py` with resource + `read` tool | 1, 2 |
| `word_count` parameter, default 30 | 1, 2 |
| `lorem-ipsum.md` source | 1 |
| `fastmcp` in dependencies | 1 |
| `.mcp.json` with all four servers | 3 |
| Startup command verified | 2 (step 5), 3 (step 4) |
| Resources-vs-tools explainer | 5 |
| `README.md` with author name | 5 |
| `HOWTORUN.md` install/run/connect/test | 5 |
| Screenshots in `docs/screenshots/` | 4 |
| Detailed PR | 6 |
| Jira read-only; no writes | Global Constraints, 4 (step 4) |
| No credentials in git | Global Constraints, 3 (step 3) |

No gaps.

**Placeholder scan:** No TBD/TODO. Every code step carries real code; every verification step carries a runnable command and an expected result. The only intentionally author-supplied artifacts are the four PNGs, which cannot be generated and have explicit existence checks.

**Type consistency:** `_read_words(word_count: int = DEFAULT_WORD_COUNT) -> str` is defined in Task 1 and referenced under that exact name in Task 2's registrations and both test files. `DEFAULT_WORD_COUNT` and `LOREM_PATH` are consistent across Tasks 1, 2, and their tests. `mcp` is the `FastMCP` instance in Task 2 and is what `tests/test_mcp_surface.py` imports. Server names `github`, `filesystem`, `atlassian`, `lorem-ipsum` are identical in Task 3's config and Task 4's interactions.
