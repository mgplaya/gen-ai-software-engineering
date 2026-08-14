# How to Run

Instructions to install, run, connect, and test the MCP servers for Homework 5. All paths
below assume the repository is cloned at
`~/development/education/set/gen-ai-software-engineering` — the same path baked into
`${HOME}`-relative entries in `.mcp.json`. **If your clone lives elsewhere, edit the
`filesystem` and `lorem-ipsum` entries in `homework-5/.mcp.json` to point at your actual
path before continuing.**

Every command block below assumes your shell's working directory is the **repository root**
(the directory that contains `homework-5/`). Directory changes are wrapped in a subshell —
`(cd path && command)` — so running a block never changes your shell's actual working
directory; you can run the blocks below in order in a single shell, or independently, and
either way each one still finds `homework-5/...` relative to the repo root.

## 1. Prerequisites

- Python >= 3.10
- [`uv`](https://docs.astral.sh/uv/) (manages the custom server's virtualenv and runs it)
- Node.js (provides `npx`, used to launch the filesystem MCP server)
- [Claude Code](https://claude.com/claude-code)
- [`gh`](https://cli.github.com/) CLI, logged in (`gh auth status`) — used to source the
  GitHub MCP token

## 2. Install dependencies (custom server)

```bash
(cd homework-5/custom-mcp-server && uv sync)
```

This creates `.venv/` and installs `fastmcp` (and `pytest` for the dev group) from
`pyproject.toml`.

## 3. Run the server standalone

```bash
(cd homework-5/custom-mcp-server && uv run server.py)
```

The server speaks stdio and blocks waiting for a client, so it will not exit on its own. A
FastMCP startup banner (`FastMCP 3.4.7`, server name `lorem-ipsum`) confirms it started
correctly. Stop it with Ctrl-C. To check the banner non-interactively without installing
`timeout` (not present on macOS by default), redirect stdin from `/dev/null` and pipe through
`head`:

```bash
(cd homework-5/custom-mcp-server && uv run server.py < /dev/null 2>&1 | head -20)
```

## 4. Connect the MCP configuration

1. Make `GITHUB_MCP_TOKEN` visible to Claude Code.

   **Claude Code does not auto-load `.env` files.** `.mcp.json` expands `${GITHUB_MCP_TOKEN}`
   from the *process environment* of the Claude Code process, so simply creating
   `homework-5/.env` has no effect — the variable has to reach that environment before the
   client starts. Any one of these three works; all were verified against `claude mcp list`:

   | Method | Command | Notes |
   |---|---|---|
   | Source `.env` | `set -a && . ./.env && set +a && claude` (from `homework-5/`) | Uses the `.env` you already created; per-shell |
   | Settings file | add an `"env"` key to `homework-5/.claude/settings.local.json` (below) | Persists across launches, no per-launch step; git-ignored |
   | Plain export | `export GITHUB_MCP_TOKEN=$(gh auth token)` | No `.env` needed; per-shell |

   The settings-file form:

   ```json
   {
     "env": {
       "GITHUB_MCP_TOKEN": "your_token_here"
     }
   }
   ```

   `.claude/settings.local.json` is git-ignored (see `.gitignore`), so the token stays local.
   Never put it in `.claude/settings.json`, which *is* committed.

   **Required token scope.** This homework only reads from a *public* repository, so the
   minimum is:

   | Token type | Scope / permission |
   |---|---|
   | Classic PAT | `public_repo` |
   | Fine-grained PAT | `Metadata: Read` (mandatory) plus `Pull requests: Read`, `Issues: Read`, `Contents: Read` |

   The `gh` CLI token used above carries the broader `repo` scope, which also grants write
   access to your private repositories. That authority is never exercised here — the
   `github` entry in `.mcp.json` sends `X-MCP-Readonly: true`, so the server withholds
   every write tool (27 tools offered instead of 44). If you prefer least privilege, mint a
   `public_repo` classic PAT or a fine-grained PAT limited to this one repository and export
   that value instead.

2. Start Claude Code from `homework-5/`:

   ```bash
   (cd homework-5 && claude)
   ```

3. Claude Code detects the project-scoped `.mcp.json` and prompts to approve it. Approve it.
4. Confirm all four servers registered (this also works from a separate shell, without an
   active interactive session):

   ```bash
   (cd homework-5 && claude mcp list)
   ```

5. `atlassian` uses OAuth and will show as needing authentication on first connect. Run
   `/mcp` inside Claude Code and follow the browser flow to authenticate.

## 5. Test the `read` tool

Automated suite:

```bash
(cd homework-5/custom-mcp-server && uv run pytest -v)
```

Expect `13 passed`.

Live check inside Claude Code (with the MCP configuration connected as above), ask:

> Use the lorem-ipsum read tool to get 10 words

Claude should call the `read` tool with `word_count=10` and return the first 10 words of
`lorem-ipsum.md`.

## 6. Troubleshooting

- **`filesystem` refuses a path that `.mcp.json` clearly allows** — e.g.
  `Access denied - path outside allowed directories`. The server's effective sandbox is the
  directory Claude Code was launched from, not the path on its command line: Claude Code
  advertises its working directory as an MCP *root*, and recent versions of the filesystem
  server prefer client roots over their command-line argument. Confirm the real scope with
  the server's `list_allowed_directories` tool. To widen it to the repository root, launch
  from there with `claude --mcp-config homework-5/.mcp.json` instead of `cd homework-5`.

- **`lorem-ipsum` fails to connect** — usually means `uv` is not on `PATH` for the process
  that launches Claude Code (MCP clients don't always inherit an interactive shell's `PATH`).
- **`github` fails to connect** with `HTTP 400: … Authorization header is badly formatted` —
  `GITHUB_MCP_TOKEN` never reached Claude Code's environment. Creating `homework-5/.env` alone
  does **not** do this; `.env` is not auto-loaded. Confirm with `claude mcp list`, which names
  the cause outright:

  ```
  [Warning] [github] mcpServers.github: Missing environment variables: GITHUB_MCP_TOKEN
  ```

  Fix it with any method from step 4.1, then restart Claude Code from that same shell. Plain
  OAuth is not an option for this server: GitHub's auth server does not support Claude Code's
  dynamic client registration.
- **`atlassian` shows `Needs authentication`** — its OAuth flow has not been completed yet;
  run `/mcp` in Claude Code and authenticate.
- **`warning: VIRTUAL_ENV=... does not match the project environment path`** from `uv` — this
  is harmless. It appears when another homework's virtualenv is active in the current shell;
  `uv` correctly ignores it and uses the project's own `.venv`.
- **`timeout: command not found`** — `timeout` is not installed on macOS by default; use the
  `< /dev/null` redirection form shown in step 3 instead.
