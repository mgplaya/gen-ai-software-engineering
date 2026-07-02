# API Reference

Base URL (local): `http://localhost:3000`

All request/response bodies are JSON unless noted (the import endpoint takes
`multipart/form-data`). All error responses share the shape described in
[Error Responses](#error-responses).

## Data Models

### Ticket

```json
{
  "id": "895cc090-d57c-46fc-97fa-ac042222846c",
  "customer_id": "CUST-001",
  "customer_email": "alice@example.com",
  "customer_name": "Alice Nguyen",
  "subject": "Cannot access my dashboard",
  "description": "I have tried logging in five times and keep getting an error message.",
  "category": "account_access",
  "priority": "urgent",
  "status": "new",
  "created_at": "2026-07-02T12:10:32.134Z",
  "updated_at": "2026-07-02T12:10:32.134Z",
  "resolved_at": null,
  "assigned_to": null,
  "tags": [],
  "metadata": { "source": "web_form", "browser": "Chrome", "device_type": "desktop" },
  "classification": null
}
```

| Field | Type | Notes |
|---|---|---|
| `category` | enum | `account_access \| technical_issue \| billing_question \| feature_request \| bug_report \| other` |
| `priority` | enum | `urgent \| high \| medium \| low` |
| `status` | enum | `new \| in_progress \| waiting_customer \| resolved \| closed` |
| `metadata.source` | enum | `web_form \| email \| api \| chat \| phone` |
| `metadata.device_type` | enum, nullable | `desktop \| mobile \| tablet` |
| `classification` | object, nullable | Set once `POST /tickets/:id/auto-classify` has run — see [Classification result](#classification-result) |

### Classification result

```json
{
  "category": "account_access",
  "priority": "urgent",
  "confidence": 0.85,
  "reasoning": "Matched category keyword(s) [login, password] -> account_access. Matched priority keyword(s) [cannot access, critical] -> urgent.",
  "keywords": ["login", "password", "cannot access", "critical"],
  "classifiedAt": "2026-07-02T12:13:06.988Z"
}
```

---

## Endpoints

### `POST /tickets`

Creates a ticket. `category`/`priority` default to `other`/`medium` if omitted. Set
`"autoClassify": true` in the body to run the classifier immediately after creation.

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

`201 Created` → the created Ticket (see [Data Models](#data-models)).
`400 Bad Request` → validation error (see [Error Responses](#error-responses)).

---

### `POST /tickets/import`

Bulk-imports tickets from a CSV, JSON, or XML file (`multipart/form-data`, field name `file`).

Query params:
- `format` (optional) — `csv | json | xml`. If omitted, inferred from the file extension, then
  from the mimetype.
- `autoClassify` (optional, default `false`) — when `true`, every successfully imported ticket is
  classified immediately.

```bash
curl -X POST "http://localhost:3000/tickets/import?autoClassify=true" \
  -F "file=@tests/fixtures/sample_tickets.csv"
```

Response `200 OK`:

```json
{
  "total": 50,
  "successful": 48,
  "failed": 2,
  "ticketIds": ["...", "..."],
  "errors": [
    { "index": 12, "message": "customer_email must be a valid email address" },
    { "index": 37, "message": "description must be between 10 and 2000 characters" }
  ]
}
```

A file that fails to parse at all (invalid CSV/JSON/XML syntax) returns `400 Bad Request` with a
message describing the parse failure — the whole request fails, since there is nothing to import.
A file that parses but has some invalid *rows* still returns `200 OK`, with those rows reflected
in `errors`.

**File schemas** (see `tests/fixtures/sample_tickets.*` for full working examples):
- **CSV** — flat columns: `customer_id, customer_email, customer_name, subject, description,
  assigned_to, tags, metadata_source, metadata_browser, metadata_device_type`. `tags` is
  `|`-separated (commas are already CSV's delimiter).
- **JSON** — a top-level array of objects matching the `POST /tickets` body shape (nested
  `metadata` object, `tags` array).
- **XML** — `<tickets><ticket>...<tags><tag>x</tag></tags><metadata>...</metadata></ticket></tickets>`.

---

### `GET /tickets`

Lists tickets, optionally filtered (filters combine with AND).

| Query param | Description |
|---|---|
| `category` | exact match |
| `priority` | exact match |
| `status` | exact match |
| `customer_id` | exact match |
| `assigned_to` | exact match |
| `tag` | ticket must include this tag |

```bash
curl "http://localhost:3000/tickets?category=billing_question&priority=urgent"
```

`200 OK` → `Ticket[]`.

---

### `GET /tickets/:id`

```bash
curl http://localhost:3000/tickets/895cc090-d57c-46fc-97fa-ac042222846c
```

`200 OK` → `Ticket`. `404 Not Found` if the id doesn't exist.

---

### `PUT /tickets/:id`

Partial update — any subset of `subject, description, category, priority, status, assigned_to,
tags, metadata`. Setting `category`/`priority` here is how you manually override a classification.
Setting `status` to `resolved` stamps `resolved_at`; moving away from `resolved` clears it.

```bash
curl -X PUT http://localhost:3000/tickets/895cc090-d57c-46fc-97fa-ac042222846c \
  -H 'Content-Type: application/json' \
  -d '{ "status": "resolved" }'
```

`200 OK` → the updated `Ticket`. `404 Not Found` if the id doesn't exist.

---

### `DELETE /tickets/:id`

```bash
curl -X DELETE http://localhost:3000/tickets/895cc090-d57c-46fc-97fa-ac042222846c
```

`204 No Content`. `404 Not Found` if the id doesn't exist.

---

### `POST /tickets/:id/auto-classify`

Runs the rule-based classifier against the ticket's current `subject` + `description`, updates its
`category`/`priority`, stores the full result under `classification`, and logs the decision.

```bash
curl -X POST http://localhost:3000/tickets/895cc090-d57c-46fc-97fa-ac042222846c/auto-classify
```

`200 OK` → the [Classification result](#classification-result). `404 Not Found` if the id doesn't exist.

---

## Error Responses

Validation errors (`400`) from any endpoint that accepts a body/query DTO:

```json
{
  "error": "Validation failed",
  "details": [
    { "field": "customer_email", "message": "customer_email must be a valid email address" },
    { "field": "metadata.source", "message": "metadata.source must be one of: web_form, email, api, chat, phone" }
  ]
}
```

Nested object fields (e.g. `metadata.source`) are flattened into a dotted path. Not-found errors
(`404`) use Nest's default shape: `{ "statusCode": 404, "message": "Ticket with id \"...\" not found" }`.
