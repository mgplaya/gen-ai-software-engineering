# How to Run

## Prerequisites

- Node.js 18+ and npm

## Setup

```bash
cd homework-2
npm install
```

No environment variables or database are required — storage is entirely in-memory and resets on
every restart (by design, per the assignment spec).

## Run the API

```bash
npm run start        # production build + run: http://localhost:3000
# or, during development (auto-restarts on file changes):
npm run start:dev
```

You should see:

```
🎧 Customer Support Ticket API is running on http://localhost:3000
```

## Try it

```bash
curl -X POST http://localhost:3000/tickets \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": "CUST-001",
    "customer_email": "alice@example.com",
    "customer_name": "Alice Nguyen",
    "subject": "Cannot access my dashboard",
    "description": "I forgot my password and cannot access my account, this is critical.",
    "metadata": { "source": "web_form", "browser": "Chrome", "device_type": "desktop" },
    "autoClassify": true
  }'
```

```bash
curl -X POST "http://localhost:3000/tickets/import?autoClassify=true" \
  -F "file=@tests/fixtures/sample_tickets.csv"
```

See [API_REFERENCE.md](API_REFERENCE.md) for every endpoint with examples.

## Run the Tests

```bash
npm test            # all 66 tests
npm run test:cov    # with a coverage report
```

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for the full breakdown and a manual testing checklist.

## Build

```bash
npm run build        # compiles TypeScript to dist/ via the Nest CLI
npm run start:prod   # runs the compiled output: node dist/main.js
```
