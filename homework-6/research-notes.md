# Research Notes: context7 Queries

These queries support **Agent 2** (`/generate-pipeline`), which built `mcp/server.py`
(Task 8, a FastMCP server) and `agents/settlement_processor.py` (Task 6, Decimal-based
fee math). Each query was made against the actual context7 MCP server to confirm the
framework/library patterns before/while implementing those files.

**Methodology:** context7 tools were not directly callable inside this Claude Code
session in this pass (the `context7` entry in `mcp.json` requires a session restart to
attach). To make the queries real rather than invented, the same server the project's
`mcp.json` configures — `npx -y @upstash/context7-mcp@latest` — was driven directly:
initialized over stdio with JSON-RPC 2.0 (`initialize` → `notifications/initialized` →
`tools/list` → `tools/call`), anonymously, no API key. The server exposes two tools:
`resolve-library-id` (requires both `libraryName` and `query`) and `query-docs`
(requires `libraryId` and `query`). Both queries below used that live session.

---

## Query 1: FastMCP tool/resource decorator patterns and server run mode
- Search: `resolve-library-id` with `libraryName: "fastmcp"`, `query: "tool and resource decorators, mcp.run() stdio"`
- context7 library ID: `/prefecthq/fastmcp`
- Applied: The docs confirmed the exact pattern `mcp/server.py` uses — instantiate
  `mcp = FastMCP("pipeline-status")` (server.py:31), decorate handler functions with
  bare `@mcp.tool` (server.py:92, 98) and `@mcp.resource("pipeline://summary")`
  (server.py:104), and start the server with a no-argument `mcp.run()` call under
  `if __name__ == "__main__":` (server.py:111). context7's snippet from
  `docs/servers/server.mdx` states STDIO is the default transport for `mcp.run()`,
  matching our server having no `transport=` argument, and the resource-decorator
  reference from `docs/servers/resources.mdx` confirms the function's docstring is
  used as the resource's `description` when one isn't given explicitly — the same
  convention our tool/resource docstrings rely on for descriptions surfaced to clients.

## Query 2: Decimal quantize with ROUND_HALF_UP for currency rounding
- Search: `resolve-library-id` with `libraryName: "python"`, `query: "decimal quantize rounding ROUND_HALF_UP"`, then `query-docs` on the resolved ID with `query: "Decimal quantize with ROUND_HALF_UP for rounding currency amounts to two decimal places"`
- context7 library ID: `/python/cpython`
- Applied: The docs' canonical monetary-rounding example —
  `Decimal('7.325').quantize(Decimal('.01'), rounding=ROUND_DOWN)` — is the same
  `quantize(exp, rounding=...)` call shape used in
  `agents/settlement_processor.py:44-45`:
  `fee = (amount * FEE_RATE).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)` and
  `settled_amount = (amount - fee).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)`,
  where `TWO_PLACES = Decimal("0.01")` (settlement_processor.py:27). context7's
  stdlib source excerpt (`Lib/_pydecimal.py`) also confirmed why the explicit
  rounding mode matters: the module's *default* context rounding is `ROUND_HALF_EVEN`
  (banker's rounding), which would round `0.005` differently than the
  `ROUND_HALF_UP` our fee math explicitly requests — validating that we pass
  `rounding=ROUND_HALF_UP` on every `quantize()` call instead of relying on the
  ambient context default.
