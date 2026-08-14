# MCP Interaction Transcripts

Text record of each MCP call captured in `docs/screenshots/`. Every call below was made
from a Claude Code session launched in `homework-5/`, so the four servers registered in
`.mcp.json` were the ones serving these requests.

Three of the four calls have screenshots. The Jira call does not: it runs against a
production Jira, and its server returns full issue bodies regardless of the requested
fields, so its response is transcribed by hand with the issue keys masked. See section 3.

---

## 1. GitHub MCP — recent pull requests

**Prompt:** List the recent pull requests on the course repository.

**Tool:** `mcp__github__list_pull_requests`

```json
{
  "owner": "mgplaya",
  "repo": "gen-ai-software-engineering",
  "state": "all",
  "fields": ["number", "title", "state", "merged_at", "created_at", "html_url"],
  "perPage": 10
}
```

**Response:** eight pull requests, all merged except #3.

| PR | Title | State |
|---|---|---|
| #8 | Add Claude Code GitHub Workflow | merged 2026-08-05 |
| #7 | Revert "Revert "Homework 4"" | merged 2026-07-30 |
| #6 | Revert "Homework 4" | merged 2026-07-30 |
| #5 | Homework 4 | merged 2026-07-30 |
| #4 | Homework 3 — Specification-Driven Design for Regulated Virtual Card Controls | merged 2026-07-19 |
| #3 | Homework 3 — Specification-Driven Design for Regulated Virtual Card Controls | closed, not merged |
| #2 | Homework 2: Intelligent Customer Support System | merged 2026-07-14 |
| #1 | Homework 1: Banking Transactions API (NestJS) | merged 2026-07-14 |

Screenshot: `docs/screenshots/01-github-mcp-result.png`

---

## 2. Filesystem MCP — project directory structure

**Prompt:** Summarize the structure of this project directory.

**Tool:** `mcp__filesystem__directory_tree`

```json
{
  "path": "/Users/gorishnyi/development/education/set/gen-ai-software-engineering/homework-5",
  "excludePatterns": [".venv", "__pycache__", ".git", ".pytest_cache", "*.lock"]
}
```

**Response:**

```
homework-5/
├── .claude/settings.local.json
├── .env                      (gitignored — token value never committed)
├── .env.example
├── .mcp.json
├── HOWTORUN.md
├── README.md
├── TASKS.md
├── custom-mcp-server/
│   ├── lorem-ipsum.md
│   ├── pyproject.toml
│   ├── server.py
│   ├── uv.lock
│   └── tests/
│       ├── test_mcp_surface.py
│       └── test_read_words.py
└── docs/
    ├── PR_DESCRIPTION.md
    ├── mcp-transcripts.md
    ├── screenshots/
    └── superpowers/
        ├── plans/2026-08-12-mcp-servers.md
        └── specs/2026-08-12-mcp-servers-design.md
```

### Note: the effective allowed directory is narrower than `.mcp.json` requests

`.mcp.json` passes the course repository root to
`@modelcontextprotocol/server-filesystem` as its allowed directory, but at runtime the
server reports only `homework-5`:

```
$ mcp__filesystem__list_allowed_directories
Allowed directories:
/Users/gorishnyi/development/education/set/gen-ai-software-engineering/homework-5
```

Requesting the repository root is refused:

```
Access denied - path outside allowed directories:
… /gen-ai-software-engineering not in … /gen-ai-software-engineering/homework-5
```

This is **MCP roots negotiation**, not a misconfiguration. Claude Code advertises its
working directory to each server as a client *root*, and recent versions of the filesystem
server prefer client-supplied roots over the directory given on its command line. The
command-line path therefore acts as a fallback for clients that do not send roots, while
the effective sandbox is the directory Claude Code was launched from. The narrower scope is
the safer of the two, and it still satisfies the task: a valid directory, scoped to a
project folder, with a successful structure-summarizing interaction.

To scope the server at the repository root instead, launch Claude Code from the repository
root and point it at this config explicitly:

```bash
claude --mcp-config homework-5/.mcp.json
```

Screenshot: `docs/screenshots/02-filesystem-mcp-result.png`

---

## 3. Jira MCP (Atlassian) — last 5 bugs

**Prompt:** Give me the tickets of the last 5 bugs on a project.

**Tool:** `mcp__atlassian__searchJiraIssuesUsingJql` — a read-only search. No issue was
created, edited, transitioned, or commented on at any point in this homework.

```json
{
  "cloudId": "77aec8f7-83e5-469a-b2f3-e8eb99cd64dd",
  "jql": "issuetype = Bug AND project = AI20 ORDER BY created DESC",
  "fields": ["key", "created"],
  "maxResults": 5
}
```

**Response** — five Bug issues, newest first. The source is a production Jira containing
customer and colleague data, so the issue keys are masked here and no screenshot of this
call is included; only the shape of the response and the creation ordering are reproduced:

| # | Key | Created |
|---|---|---|
| 1 | `AI20-XXXX` | 2026-08-03 |
| 2 | `AI20-XXXX` | 2026-07-28 |
| 3 | `AI20-XXXX` | 2026-07-17 |
| 4 | `AI20-XXXX` | 2026-07-14 |
| 5 | `AI20-XXXX` | 2026-07-14 |

The query returned exactly five issues, all of type `Bug`, in strictly descending `created`
order — which is what the request was verifying. Creation dates are retained because they
demonstrate the `ORDER BY created DESC` clause took effect; the keys themselves add no
evidential value once the count, type, and ordering are shown.

### Note: `fields` does not restrict this server's response

Passing `fields: ["key", "created"]` does **not** narrow the payload. The Atlassian MCP
server ignores the projection and returns `summary`, `description`, `status`, `assignee`
(including work email addresses), and `project` for every matched issue.

Redaction therefore cannot be delegated to the request — it has to happen after the fact.
That is the reason this is the one interaction with no screenshot: the raw tool result is
returned in full regardless of what the request asks for, so the only reliable way to
guarantee nothing confidential reaches the submission was to withhold the image and
transcribe the response by hand, masked.

**No screenshot for this server.** The assignment's Task 3 does ask for one and permits
ticket numbers to stand in for the response, so this is a deliberate, author-approved
deviation on confidentiality grounds, not an oversight. The evidence that the server was
configured and working is: this transcript, the `atlassian` entry in `.mcp.json`, and its
`✔ Connected` status in `claude mcp list`.

---

## 4. Custom MCP (lorem-ipsum) — `read` tool

**Prompt:** Use the lorem-ipsum `read` tool, once with no arguments and once for 10 words.

**Tool:** `mcp__lorem-ipsum__read`

Call 1 — no arguments, exercising the default:

```json
{}
```

Response (exactly 30 words):

```
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt
ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation
ullamco laboris nisi
```

Call 2 — an explicit count:

```json
{"word_count": 10}
```

Response (exactly 10 words):

```
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
```

Both calls delegate to the same `_read_words` helper that backs the two resources, so the
30-word default, the exact-count slice, the clamp beyond the file's 272 words, and the
`ValueError` on a non-positive count are all covered once by the 13-test suite in
`custom-mcp-server/tests/`.

Screenshot: `docs/screenshots/04-custom-mcp-read-tool.png`
