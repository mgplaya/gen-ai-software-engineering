# 🏦 Homework 1 — Banking Transactions API

> **Student**: Mykhailo Gorishnyi
> **Stack**: NestJS (Node.js + TypeScript), in-memory storage (no DB)
> **AI tool**: Claude Code (Opus 4.8)

A minimal REST API for banking transactions: create/query transactions, account balances, request validation with structured error messages, filtering, and **all four** optional Task 4 features (summary, interest, CSV export, rate limiting).

---

## ✅ Scope — what's implemented

### Task 1 — Core API
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/transactions` | Create a transaction (`201`) |
| `GET`  | `/transactions` | List / filter transactions |
| `GET`  | `/transactions/:id` | Get by id (`404` if missing) |
| `GET`  | `/accounts/:accountId/balance` | Current account balance |

### Task 2 — Validation
- **Amount**: positive number, ≤ 2 decimal places.
- **Accounts**: must match `ACC-XXXXX`; `fromAccount` required for withdrawals/transfers, `toAccount` for deposits/transfers.
- **Currency**: valid ISO 4217 code; **Type**: `deposit | withdrawal | transfer`; unknown fields rejected.
- Errors returned in the required shape: `{ "error": "Validation failed", "details": [{ "field", "message" }] }`.

### Task 3 — Transaction history (filtering)
`GET /transactions` supports combinable query params: `?accountId=` (matches `fromAccount` **or** `toAccount`), `?type=`, `?from=&to=` (inclusive date range; date-only `to` covers end of day).

### Task 4 — Additional features (all four)
| Feature | Endpoint |
|---------|----------|
| **A. Summary** | `GET /accounts/:accountId/summary` — totals, count, most recent date, balance |
| **B. Interest** | `GET /accounts/:accountId/interest?rate=0.05&days=30` — `principal × rate × days / 365` |
| **C. CSV export** | `GET /transactions/export?format=csv` — honours the same filters |
| **D. Rate limiting** | 100 req/min/IP via `@nestjs/throttler`, returns `429` when exceeded |

---

## 🏗️ Key architecture decisions

- **NestJS** — modular structure (modules/controllers/services), first-class DTO validation via decorators, built-in throttler.
- **In-memory storage** — a simple array in `TransactionsService`, per the spec; data resets on restart.
- **Validation** — `class-validator` DTOs + global `ValidationPipe` with a custom `exceptionFactory` (`src/main.ts`) that reshapes errors into the required `{ error, details[] }` format.
- **Balance model** — derived from **completed** transactions only; monetary values rounded to 2 decimals to avoid floating-point drift.
- **Route ordering** — `GET /transactions/export` declared before `GET /transactions/:id` so `export` isn't captured as an id.
- **Accounts reuse Transactions** — `AccountsModule` derives balance/summary/interest from the single source of truth.

---

## 🤖 How AI was used

Built end-to-end with **Claude Code**:

1. **Requirements analysis** — Claude read `TASKS.md` and clarified two decisions with me: the tech stack (I chose NestJS) and which Task 4 features to build (I chose all four).
2. **Scaffolding & implementation** — Claude generated the module/controller/service structure, DTOs with `class-validator` rules, the in-memory service, and the custom validation-error formatter.
3. **Verification** — Claude installed dependencies, built the project, started the server, and ran a 13+ case `curl` suite (happy paths, validation errors, filters, `404`, and a 105-request burst confirming the `429` rate limit). All assertions passed (e.g. balance `500 − 100.5 − 50 = 349.5`, interest `349.5 × 0.05 × 30/365 = 1.44`).
4. **Documentation** — README, HOWTORUN, and demo scripts generated and reviewed.

I reviewed the generated code rather than accepting it blindly — e.g. confirming the conditional account validation and the route-ordering fix for `/export`.

---

## 🚀 How to run

```bash
cd homework-1
npm install && npm run build
npm run start:prod          # terminal 1 — API on http://localhost:3000
./demo/sample-requests.sh   # terminal 2 — seeds data + exercises every endpoint
```

Full instructions: [`homework-1/HOWTORUN.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-1/homework-1/HOWTORUN.md). Postman/REST Client collection: `demo/sample-requests.http`.

---

## 📸 Screenshots

### 1. AI interaction — working with Claude Code

Initial session: Claude explores the repo, summarises the homework structure, and asks which task to start with:

![AI interaction — repo exploration and planning](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/a6ff9d9ea22f21ed36e2cd36d6b86b7699d0d479/homework-1/docs/screenshots/Screenshot%202026-07-01%20at%2018.28.23.png)

End of the build session: Claude lists what was generated (+5,415 lines) and the remaining manual steps (screenshots, PR):

![AI interaction — summary of generated work and next steps](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/a6ff9d9ea22f21ed36e2cd36d6b86b7699d0d479/homework-1/docs/screenshots/Screenshot%202026-07-01%20at%2018.27.50.png)

### 2. Running application — full demo suite

`./demo/sample-requests.sh` against the live server: seeding from `sample-data.json`, listing, type filter, balance (`824.25`), Task 4A summary, Task 4B interest (`3.39`), Task 4C CSV export, and a validation-error example in the required `{ error, details[] }` format:

![Running app — demo script exercising every endpoint](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/a6ff9d9ea22f21ed36e2cd36d6b86b7699d0d479/homework-1/docs/screenshots/Screenshot%202026-07-01%20at%2018.30.28.png)

### 3. Request/response example — curl

Raw `curl -s http://localhost:3000/transactions` request and JSON response from the running API:

![curl request/response example](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/a6ff9d9ea22f21ed36e2cd36d6b86b7699d0d479/homework-1/docs/screenshots/Screenshot%202026-07-01%20at%2018.35.22.png)

---

## 📂 Changes in this PR

- `homework-1/src/` — NestJS application (transactions + accounts modules, DTOs, CSV util)
- `homework-1/demo/` — `run.sh`, `sample-requests.sh` (curl smoke test), `sample-requests.http`, `sample-data.json`
- `homework-1/docs/screenshots/` — AI interaction + running-app evidence
- `homework-1/README.md`, `homework-1/HOWTORUN.md` — documentation
