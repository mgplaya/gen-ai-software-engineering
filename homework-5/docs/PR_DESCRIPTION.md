# Homework 5: MCP server configuration (GitHub, Filesystem, Jira, custom FastMCP)

**Author:** Mykhailo Gorishnyi (`mgplaya`)
**Course:** GenAI and Agentic AI for Software Engineering

## What this PR delivers

Four Model Context Protocol servers wired into Claude Code and demonstrated end to end: the
three required external servers (GitHub, Filesystem, Atlassian/Jira) plus a custom FastMCP
server built from scratch that exposes a text file as both an MCP **resource** and an MCP
**tool**. All four are registered in a single project-scoped `homework-5/.mcp.json`, so a
grader reproduces the whole setup by launching Claude Code from `homework-5/`.

Everything lives under `homework-5/`:

```
homework-5/
├── .mcp.json                  four servers registered
├── .env.example               documents GITHUB_MCP_TOKEN (real .env is git-ignored)
├── README.md                  description, author, server table, resources-vs-tools
├── HOWTORUN.md                install / run / connect / test
├── custom-mcp-server/
│   ├── server.py              FastMCP: 2 resources + read tool
│   ├── lorem-ipsum.md         272-word source text
│   ├── pyproject.toml         declares fastmcp>=3.4.7
│   └── tests/                 13 tests (unit + in-memory MCP client)
└── docs/
    ├── mcp-transcripts.md     text record of every call below
    ├── screenshots/           4 captured MCP results
    └── superpowers/           design spec + implementation plan
```

## The four servers

| Server | Transport | Endpoint / command | Auth | Demonstrated interaction |
|---|---|---|---|---|
| `github` | http | `https://api.githubcopilot.com/mcp/` | `Authorization: Bearer ${GITHUB_MCP_TOKEN}` + `X-MCP-Readonly: true` | Listed recent pull requests on `mgplaya/gen-ai-software-engineering` |
| `filesystem` | stdio | `npx -y @modelcontextprotocol/server-filesystem ${HOME}/…/gen-ai-software-engineering` | none (path-scoped) | Summarized the `homework-5` project directory structure |
| `atlassian` | http | `https://mcp.atlassian.com/v1/mcp` | OAuth (`/mcp` in Claude Code) | Retrieved the last 5 bug ticket keys from a real Jira project |
| `lorem-ipsum` | stdio | `uv --directory …/custom-mcp-server run server.py` | none (local) | Called the `read` tool with the default and with `word_count=10` |

One finding worth calling out from the `filesystem` row: the command line asks for the
course repository root, but the server's effective allowed directory is `homework-5`.
That is MCP **roots** negotiation rather than a misconfiguration — Claude Code advertises
its working directory as a client root, and recent versions of the filesystem server prefer
client roots over their command-line argument. The narrower scope is the safer one and
still satisfies the task (a valid, project-scoped directory plus a successful interaction);
`claude --mcp-config homework-5/.mcp.json` launched from the repository root would widen it.

## Custom MCP server

`custom-mcp-server/server.py`, built on FastMCP 3.4.7. It exposes the same data three ways,
all delegating to one private helper (`_read_words`) so the word-selection logic exists in
exactly one place:

| Member | Kind | Signature | Behavior |
|---|---|---|---|
| `lorem://ipsum` | Resource | — | First 30 words of `lorem-ipsum.md` (the default slice) |
| `lorem://ipsum/{word_count}` | Resource template | `word_count: int` | First `word_count` words |
| `read` | Tool | `read(word_count: int = 30) -> str` | Same content, callable as an action |

Two resource registrations are needed because a URI template cannot express a default:
`lorem://ipsum` *is* the default-30 case, and `lorem://ipsum/{word_count}` covers every other
count.

**Resources vs. tools**, the distinction the assignment asks to be stated:

> **Resources** are URIs that Claude can read from (for example files or APIs). They are
> addressable and side-effect free.
> **Tools** are actions Claude can call to perform an operation (for example reading a file or
> running a command).

**Edge behavior**, each covered by a test rather than asserted in prose:

- `word_count < 1` raises `ValueError`.
- A `word_count` beyond the file's length clamps to the whole file (272 words) instead of erroring.
- A missing source file raises `FileNotFoundError` naming the expected path.

Built test-first. 13 tests pass — 11 unit tests against the helper, plus 2 integration tests
that drive the real MCP protocol through an in-memory `fastmcp.Client`, verifying that `read`
is registered as a tool, that `lorem://ipsum` appears in `list_resources()`, and that
`lorem://ipsum/{word_count}` appears in `list_resource_templates()`.

```
$ cd homework-5/custom-mcp-server && uv run pytest -q
13 passed
```

## Results

GitHub — recent pull requests on `mgplaya/gen-ai-software-engineering`:

![GitHub MCP](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-5-submission/homework-5/docs/screenshots/01-github-mcp-result.png?raw=1)

Filesystem — the `homework-5` project directory structure:

![Filesystem MCP](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-5-submission/homework-5/docs/screenshots/02-filesystem-mcp-result.png?raw=1)

Atlassian/Jira — **deliberately no screenshot.** The query ran against a production Jira
holding customer and colleague data, and that server returns full issue bodies — summaries,
descriptions, assignee email addresses — no matter which `fields` the request specifies (see
the finding below). Rather than depend on a screen capture staying clean, the response is
transcribed by hand with the issue keys masked. Task 3 does ask for a screenshot and does
allow ticket numbers to represent the response, so this is a considered trade-off in favour
of confidentiality, not an omission: the server's configuration and working state are
evidenced by the transcript, the `atlassian` entry in `.mcp.json`, and its `✔ Connected`
status in `claude mcp list`.

Custom server — the `read` tool, default and `word_count=10`:

![Custom MCP read tool](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-5-submission/homework-5/docs/screenshots/04-custom-mcp-read-tool.png?raw=1)

Text transcripts of all four calls are in
[`docs/mcp-transcripts.md`](../docs/mcp-transcripts.md).

## How to run it

Full instructions in [`HOWTORUN.md`](../HOWTORUN.md). The short version, from the repo root:

```bash
(cd homework-5/custom-mcp-server && uv sync)     # install fastmcp
export GITHUB_MCP_TOKEN=$(gh auth token)         # before launching Claude Code
(cd homework-5 && claude)                        # approve the project-scoped .mcp.json
(cd homework-5 && claude mcp list)               # confirm all four registered
```

`atlassian` shows as needing authentication on first connect — run `/mcp` inside Claude Code
and complete the OAuth flow. A grader whose clone lives at a different path must edit the
`filesystem` and `lorem-ipsum` entries in `.mcp.json` accordingly; this is called out at the
top of `HOWTORUN.md`.

## Safety and privacy notes

These were treated as hard constraints throughout, not afterthoughts.

**Jira output is masked, and its screenshot withheld.** The assignment allows ticket numbers
to represent the response ("use only ticket/page numbers"), but the project queried is a
real internal one whose issue summaries and descriptions are confidential, so this submission
goes a step further: the issue keys are masked as `AI20-XXXX` and no screenshot of the call
is included. What the transcript preserves is the part that actually evidences the request —
five issues, all of type `Bug`, in strictly descending creation order.

Worth flagging for anyone reproducing this: the `fields` parameter **does not** restrict what
the Atlassian MCP server returns. Asking for `["key", "created"]` still yields full
summaries, descriptions, and assignee email addresses. Because the raw result arrives in full
no matter how the request is narrowed, redaction cannot be pushed into the query — it has to
happen after the fact, which is precisely why this one call is transcribed by hand rather
than captured.

**Jira was read-only.** Only `searchJiraIssuesUsingJql` was ever called. No issue was
created, edited, transitioned, commented on, or logged against at any point.

**No credentials are committed.** `atlassian` authenticates by OAuth. `github` references
`${GITHUB_MCP_TOKEN}` — the variable *name* is committed, never its value; the real `.env` is
git-ignored, and `.env.example` documents the variable and the minimum token scope
(`public_repo` for a classic PAT). Paths in `.mcp.json` are `${HOME}`-relative rather than
hardcoded to one machine.

**Both external write-capable servers are read-only by construction.** GitHub read-only is
enforced at the transport with `X-MCP-Readonly: true`, which makes it a property of the
connection instead of a promise: with the header, the server advertises 27 tools instead of 44,
withholding every write tool (`create_pull_request`, `merge_pull_request`,
`update_pull_request`, …) while keeping `list_pull_requests`. Jira was used strictly through
JQL search — no issue was created, edited, transitioned, or commented on.

## One design change from the original plan

The design spec called for **OAuth** on the `github` server. GitHub's auth server rejects
Claude Code's dynamic client registration:

```
✘ Failed to connect — Incompatible auth server: does not support dynamic client registration
```

So OAuth is not achievable for this server. Header auth sourced from the existing `gh` CLI
login replaces it, verified by a direct `initialize` POST to
`https://api.githubcopilot.com/mcp/` with `Authorization: Bearer $(gh auth token)` returning
the server's capabilities. The amendment is recorded in the implementation plan and explained
in both `README.md` and `HOWTORUN.md` rather than left as a silent deviation.
