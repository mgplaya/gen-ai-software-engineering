#!/usr/bin/env bash
# Walks through every Customer Support API endpoint with curl.
# The server must already be running (./demo/run.sh or npm run start:prod).
# Usage: ./demo/sample-requests.sh [base-url]     default: http://localhost:3000
set -euo pipefail

BASE_URL="${1:-http://localhost:3000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FIXTURES="$PROJECT_DIR/tests/fixtures"

step() { echo; echo "=== $1 ==="; }

step "1. Create a ticket (auto-classified on create)"
CREATED=$(curl -sS -X POST "$BASE_URL/tickets" \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": "DEMO-001",
    "customer_email": "jane.doe@example.com",
    "customer_name": "Jane Doe",
    "subject": "Cannot log in to my account",
    "description": "My password is rejected and now I am locked out, this is critical.",
    "autoClassify": true,
    "tags": ["demo"],
    "metadata": { "source": "web_form", "browser": "Chrome", "device_type": "desktop" }
  }')
echo "$CREATED"
TICKET_ID=$(echo "$CREATED" | sed -E 's/.*"id":"([^"]+)".*/\1/')
echo "→ created ticket: $TICKET_ID"

step "2. Validation error demo (bad email → 400)"
curl -sS -X POST "$BASE_URL/tickets" \
  -H 'Content-Type: application/json' \
  -d '{"customer_id":"DEMO-002","customer_email":"not-an-email","customer_name":"Bad Email","subject":"Broken payload","description":"This payload has an invalid email.","metadata":{"source":"api"}}' || true
echo

step "3. Bulk import CSV (50 rows) with auto-classification"
curl -sS -F "file=@$FIXTURES/sample_tickets.csv" "$BASE_URL/tickets/import?autoClassify=true"
echo

step "4. Bulk import JSON (20 records)"
curl -sS -F "file=@$FIXTURES/sample_tickets.json" "$BASE_URL/tickets/import"
echo

step "5. Bulk import XML (30 tickets)"
curl -sS -F "file=@$FIXTURES/sample_tickets.xml" "$BASE_URL/tickets/import"
echo

step "6. Import with per-row failures (4 of 5 CSV rows invalid)"
curl -sS -F "file=@$FIXTURES/invalid_tickets.csv" "$BASE_URL/tickets/import"
echo

step "7. Malformed file → 400"
curl -sS -F "file=@$FIXTURES/malformed.json" "$BASE_URL/tickets/import" || true
echo

step "8. List tickets filtered by category + priority"
FILTERED=$(curl -sS "$BASE_URL/tickets?category=account_access&priority=urgent")
echo "${FILTERED:0:800} ..."

step "9. Get one ticket"
curl -sS "$BASE_URL/tickets/$TICKET_ID"
echo

step "10. Re-run auto-classification explicitly"
curl -sS -X POST "$BASE_URL/tickets/$TICKET_ID/auto-classify"
echo

step "11. Update: assign + resolve (sets resolved_at)"
curl -sS -X PUT "$BASE_URL/tickets/$TICKET_ID" \
  -H 'Content-Type: application/json' \
  -d '{"assigned_to":"agent.petrenko","status":"resolved"}'
echo

step "12. Delete the ticket (204)"
curl -sS -o /dev/null -w "HTTP %{http_code}\n" -X DELETE "$BASE_URL/tickets/$TICKET_ID"

echo
echo "✅ Demo finished."
