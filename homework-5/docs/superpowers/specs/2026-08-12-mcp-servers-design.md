# Homework 5 — MCP Server Configuration: Design

**Author**: Mykhailo Gorishnyi (`mgplaya`)
**Date**: 2026-08-12
**Status**: Approved

## Goal

Configure three external MCP servers (GitHub, Filesystem, Jira) and build one custom
FastMCP server, then demonstrate and capture a working interaction with each.

## Decisions

| Decision | Choice | Why |
|---|---|---|
| Task 3 backend | Jira via Atlassian MCP | Already connected and healthy; `playatech.atlassian.net` holds 93 Bug-type issues, the recent ones in project `AI20` |
| GitHub auth | Remote HTTP + OAuth | No PAT to store, no Docker; nothing secret enters git |
| Screenshots | Captured manually by the author | Real terminal captures of live MCP calls, which is what the grader asks for |
| Python deps | `uv` + `pyproject.toml` | `uv` already installed; `uv run` manages the venv transparently |
| Resource shape | Static + templated pair | Expresses both "accepts `word_count`" and "default: 30", which a single URI template cannot |

## Hard constraints

- **Jira is read-only.** No issue creation, editing, transitioning, commenting, or
  worklog writes — the author does not have write access. Only JQL search and
  issue reads are permitted.
- **GitHub is read-only** for this homework. Listing PRs, commits, and issues only;
  no issue or PR creation via MCP.
- **No credentials in git.** Both remote servers use OAuth.

## Layout

```
homework-5/
├── README.md              author, description, MCP resources-vs-tools explainer
├── HOWTORUN.md            install / run / connect / test
├── TASKS.md               (exists)
├── .mcp.json              all four servers
├── custom-mcp-server/
│   ├── server.py
│   ├── lorem-ipsum.md     ~250 words
│   ├── pyproject.toml     fastmcp>=3.4.7, requires-python >=3.10
│   └── tests/test_server.py
└── docs/
    ├── PR_DESCRIPTION.md
    ├── mcp-transcripts.md
    └── screenshots/
        ├── 01-github-mcp-result.png
        ├── 02-filesystem-mcp-result.png
        ├── 03-jira-mcp-last-5-bugs.png
        └── 04-custom-mcp-read-tool.png
```

## MCP configuration

`.mcp.json` registers four servers:

| Name | Transport | Endpoint / command | Auth |
|---|---|---|---|
| `github` | http | `https://api.githubcopilot.com/mcp/` | OAuth (browser, once) |
| `filesystem` | stdio | `npx -y @modelcontextprotocol/server-filesystem <root>` | none |
| `atlassian` | http | `https://mcp.atlassian.com/v1/mcp` | OAuth (already authorized) |
| `lorem-ipsum` | stdio | `uv --directory <dir> run server.py` | none |

Both remote servers authenticate by OAuth, so **no credentials are committed**.
Filesystem and custom-server paths are written as
`${HOME}/development/education/set/gen-ai-software-engineering/...` rather than
hardcoded absolute paths; `HOWTORUN.md` states where a grader adjusts them.

The filesystem root is the whole course repository, so a directory-structure
summary has substantial material.

## Custom MCP server

Transport is stdio via `mcp.run()`. One private helper is the single source of
truth; two resources and one tool delegate to it.

```python
def _read_words(word_count: int = 30) -> str:
    """Single source of truth."""

@mcp.resource("lorem://ipsum")               # the default-30 case
def lorem_default() -> str:
    return _read_words()

@mcp.resource("lorem://ipsum/{word_count}")  # any count
def lorem_n(word_count: int) -> str:
    return _read_words(word_count)

@mcp.tool
def read(word_count: int = 30) -> str:
    return _read_words(word_count)
```

Edge behavior:

- `word_count < 1` raises `ValueError`.
- `word_count` greater than the file's word count returns all available words
  rather than erroring.
- A missing `lorem-ipsum.md` raises an error naming the expected path.

### Resources vs. tools (required explainer, for `README.md`)

- **Resources** are URIs Claude can *read from* — files, API responses, generated
  text. They are addressable and side-effect free.
- **Tools** are actions Claude can *call* to perform an operation — reading a
  file, running a command, mutating state.

## Testing

`custom-mcp-server/tests/test_server.py`, run with `uv run pytest`:

1. Default returns exactly 30 words.
2. An explicit `word_count` returns exactly that many words.
3. A `word_count` beyond the file length clamps to the full file.
4. `0` and negative values raise `ValueError`.

## Capture sequence

Four live interactions, each followed by a pause for a screenshot:

1. **GitHub** — list recent pull requests on `mgplaya/gen-ai-software-engineering`
   (PRs #1–#7 exist). Requires a one-time browser OAuth approval, handed to the
   author when reached.
2. **Filesystem** — summarize the course repository's directory structure.
3. **Jira** — the exact required prompt, *"Give me the tickets of the last 5 bugs
   on a project"*. Expected: `AI20-XXXX`, `AI20-XXXX`, `AI20-XXXX`, `AI20-XXXX`,
   `AI20-XXXX`. **Issue keys and creation dates only** — no summaries,
   descriptions, assignees, or comments, per the TASKS.md warning about sensitive
   information.
4. **Custom** — call `read` with the default, then with `word_count=10`.

`docs/mcp-transcripts.md` records the text request and response for each call as a
written backup to the images, redacted the same way.

## Submission

Branch `homework-5-submission`, PR into `main`, body taken from
`docs/PR_DESCRIPTION.md`. The PR must be detailed — the course rejects one-line
pull requests.

## Out of scope

- Notion MCP (Jira chosen instead; the task requires one, not both).
- Any write operation against GitHub or Jira. All demonstrated interactions are
  read-only.
