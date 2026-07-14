# ▶️ How to Run the Application

Customer Support API — NestJS (Node.js + TypeScript). In-memory storage, no database.

## 📋 Prerequisites

- **Node.js** ≥ 18 (developed on Node 26)
- **npm** ≥ 9
- `curl` if you want to run `demo/sample-requests.sh` (ships with macOS/Linux)

## 🔧 Setup & Run

From the `homework-2/` directory:

```bash
# 1. Install dependencies
npm install

# 2. Build
npm run build

# 3. Start (production)
npm run start:prod
```

The API starts on **http://localhost:3000**. To use a different port:

```bash
PORT=4000 npm run start:prod
```

### Development mode (auto-reload)
```bash
npm run start:dev
```

### One-shot script
```bash
./demo/run.sh          # installs, builds, and starts the API
```

## 🔐 Environment

No environment variables are required. The only optional one is:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3000` | HTTP port the API listens on |

Storage is **in-memory** — all data is cleared when the process restarts.

## 🧪 Testing the API

### Option 1 — automated curl script (server must be running)
```bash
./demo/sample-requests.sh
# or against a custom URL:
./demo/sample-requests.sh http://localhost:4000
```

### Option 2 — VS Code REST Client
Open `demo/sample-requests.http` and click "Send Request" on any block.

### Option 3 — manual curl

```bash
# Create a ticket
curl -X POST http://localhost:3000/tickets \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": "CUST-001",
    "customer_email": "jane.doe@example.com",
    "customer_name": "Jane Doe",
    "subject": "Cannot log in to my account",
    "description": "My password is rejected and I am locked out.",
    "autoClassify": true,
    "metadata": { "source": "web_form", "browser": "Chrome", "device_type": "desktop" }
  }'

# Bulk import (CSV/JSON/XML) with auto-classification
curl -F "file=@tests/fixtures/sample_tickets.csv" \
  "http://localhost:3000/tickets/import?autoClassify=true"

# List with filters
curl "http://localhost:3000/tickets?category=account_access&priority=urgent"

# Auto-classify an existing ticket
curl -X POST http://localhost:3000/tickets/<id>/auto-classify
```

Full endpoint reference with examples: [docs/API_REFERENCE.md](docs/API_REFERENCE.md).

## 📡 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tickets` | Create a ticket (body flag `autoClassify: true` classifies on create) |
| `POST` | `/tickets/import?format=&autoClassify=` | Bulk import CSV/JSON/XML (multipart field `file`) |
| `GET`  | `/tickets?category=&priority=&status=&customer_id=&assigned_to=&tag=` | List with filters |
| `GET`  | `/tickets/:id` | Get one ticket |
| `PUT`  | `/tickets/:id` | Update ticket (status `resolved` sets `resolved_at`) |
| `DELETE` | `/tickets/:id` | Delete ticket (204) |
| `POST` | `/tickets/:id/auto-classify` | Classify: category, priority, confidence, reasoning, keywords |

## 🧪 Running the Test Suite

```bash
npm test               # all 56 tests
npm run test:cov       # with coverage (fails below 85% on any metric)
open coverage/lcov-report/index.html   # HTML coverage report
```

## 🧯 Troubleshooting

- **`EADDRINUSE` (port busy):** another process uses 3000 → run with `PORT=4000 npm run start:prod`.
- **Import returns 400 "Could not determine import format":** the file extension is not `.csv/.json/.xml` → pass `?format=csv|json|xml` explicitly.
- **All data disappeared:** storage is in-memory; it resets on every restart.
