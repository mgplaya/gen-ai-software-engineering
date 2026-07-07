# Customer Support API Reference

A REST API for managing customer support tickets with automatic classification and import capabilities. The API uses in-memory storage and provides endpoints for creating, retrieving, updating, and deleting tickets, as well as bulk importing tickets from multiple formats.

**Base URL:** `http://localhost:3000`

---

## Endpoints

| Method | Path | Description | Status Code |
|--------|------|-------------|------------|
| POST | `/tickets` | Create a new ticket | 201 |
| POST | `/tickets/import` | Import tickets from file (CSV, JSON, or XML) | 200 |
| GET | `/tickets` | List tickets with optional filters | 200 |
| GET | `/tickets/:id` | Retrieve a single ticket | 200 |
| PUT | `/tickets/:id` | Update an existing ticket | 200 |
| DELETE | `/tickets/:id` | Delete a ticket | 204 |
| POST | `/tickets/:id/auto-classify` | Auto-classify a ticket | 200 |

---

## POST /tickets

Create a new support ticket.

**Description:**
Creates a new ticket in the system. Requires customer information, ticket content, and metadata about the source. Category and priority may be provided; if omitted, they default to `other` and `medium`. The `autoClassify` flag (when true in the request body) will automatically classify the ticket upon creation.

**Request:**
```json
{
  "customer_id": "cust_12345",
  "customer_email": "john.doe@example.com",
  "customer_name": "John Doe",
  "subject": "Cannot login to my account",
  "description": "I've been trying to reset my password for the past hour but I'm not receiving the reset email. This is urgent as I need to access my account.",
  "category": "account_access",
  "priority": "high",
  "assigned_to": "support_agent_1",
  "tags": ["urgent", "password_reset"],
  "metadata": {
    "source": "web_form",
    "browser": "Chrome 120.0",
    "device_type": "desktop"
  },
  "autoClassify": false
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "cust_12345",
  "customer_email": "john.doe@example.com",
  "customer_name": "John Doe",
  "subject": "Cannot login to my account",
  "description": "I've been trying to reset my password for the past hour but I'm not receiving the reset email. This is urgent as I need to access my account.",
  "category": "account_access",
  "priority": "high",
  "status": "new",
  "created_at": "2026-07-03T10:30:45.123Z",
  "updated_at": "2026-07-03T10:30:45.123Z",
  "resolved_at": null,
  "assigned_to": "support_agent_1",
  "tags": ["urgent", "password_reset"],
  "metadata": {
    "source": "web_form",
    "browser": "Chrome 120.0",
    "device_type": "desktop"
  },
  "classification": null
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust_12345",
    "customer_email": "john.doe@example.com",
    "customer_name": "John Doe",
    "subject": "Cannot login to my account",
    "description": "I'\''ve been trying to reset my password for the past hour but I'\''m not receiving the reset email. This is urgent as I need to access my account.",
    "category": "account_access",
    "priority": "high",
    "assigned_to": "support_agent_1",
    "tags": ["urgent", "password_reset"],
    "metadata": {
      "source": "web_form",
      "browser": "Chrome 120.0",
      "device_type": "desktop"
    },
    "autoClassify": false
  }'
```

---

## POST /tickets/import

Import multiple tickets from a file (CSV, JSON, or XML format).

**Description:**
Uploads and imports a batch of tickets. The file is uploaded as multipart form data. The `format` query parameter can explicitly specify the file format (csv, json, or xml); if not provided, the format is detected from the file extension or MIME type. The `autoClassify` query parameter (values: `true`, `1`, or omitted for false) triggers automatic classification for all successfully imported tickets.

**Request:**
Multipart form-data with field name `file`. Supported query parameters:
- `format` (optional): `csv` | `json` | `xml` — explicitly specify the file format
- `autoClassify` (optional): `true` or `1` to enable auto-classification

**Response (200 OK):**
```json
{
  "total": 3,
  "successful": 2,
  "failed": 1,
  "ticketIds": ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"],
  "errors": [
    {
      "index": 1,
      "message": "customer_email: must be a valid email address"
    }
  ]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/tickets/import?autoClassify=true \
  -F "file=@tests/fixtures/sample_tickets.csv"
```

---

## GET /tickets

Retrieve a list of tickets with optional filtering.

**Description:**
Fetches all tickets or filters them by category, priority, status, customer ID, assigned agent, or tag. All filters are optional and can be combined.

**Query Parameters:**
- `category` (optional): `account_access` | `technical_issue` | `billing_question` | `feature_request` | `bug_report` | `other`
- `priority` (optional): `urgent` | `high` | `medium` | `low`
- `status` (optional): `new` | `in_progress` | `waiting_customer` | `resolved` | `closed`
- `customer_id` (optional): Customer identifier
- `assigned_to` (optional): Name or ID of the assigned support agent
- `tag` (optional): A single tag to filter by

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "customer_id": "cust_12345",
    "customer_email": "john.doe@example.com",
    "customer_name": "John Doe",
    "subject": "Cannot login to my account",
    "description": "I've been trying to reset my password for the past hour but I'm not receiving the reset email. This is urgent as I need to access my account.",
    "category": "account_access",
    "priority": "high",
    "status": "in_progress",
    "created_at": "2026-07-03T10:30:45.123Z",
    "updated_at": "2026-07-03T11:15:22.456Z",
    "resolved_at": null,
    "assigned_to": "support_agent_1",
    "tags": ["urgent", "password_reset"],
    "metadata": {
      "source": "web_form",
      "browser": "Chrome 120.0",
      "device_type": "desktop"
    },
    "classification": {
      "category": "account_access",
      "priority": "high",
      "confidence": 0.98,
      "reasoning": "User reports inability to reset password and access account.",
      "keywords": ["login", "password", "reset", "urgent"],
      "classified_at": "2026-07-03T10:32:10.789Z",
      "manual_override": false
    }
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "customer_id": "cust_67890",
    "customer_email": "jane.smith@example.com",
    "customer_name": "Jane Smith",
    "subject": "Billing discrepancy on latest invoice",
    "description": "I noticed that I was charged twice for my subscription this month. Please investigate and refund the duplicate charge.",
    "category": "billing_question",
    "priority": "medium",
    "status": "new",
    "created_at": "2026-07-03T14:20:10.234Z",
    "updated_at": "2026-07-03T14:20:10.234Z",
    "resolved_at": null,
    "assigned_to": null,
    "tags": ["billing", "duplicate_charge"],
    "metadata": {
      "source": "email",
      "browser": null,
      "device_type": null
    },
    "classification": null
  }
]
```

**cURL Examples:**
```bash
# Get all tickets
curl http://localhost:3000/tickets

# Filter by priority
curl http://localhost:3000/tickets?priority=high

# Filter by status and customer
curl http://localhost:3000/tickets?status=new&customer_id=cust_12345

# Filter by tag
curl http://localhost:3000/tickets?tag=urgent
```

---

## GET /tickets/:id

Retrieve a single ticket by ID.

**Description:**
Fetches detailed information about a specific ticket identified by its UUID.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "cust_12345",
  "customer_email": "john.doe@example.com",
  "customer_name": "John Doe",
  "subject": "Cannot login to my account",
  "description": "I've been trying to reset my password for the past hour but I'm not receiving the reset email. This is urgent as I need to access my account.",
  "category": "account_access",
  "priority": "high",
  "status": "in_progress",
  "created_at": "2026-07-03T10:30:45.123Z",
  "updated_at": "2026-07-03T11:15:22.456Z",
  "resolved_at": null,
  "assigned_to": "support_agent_1",
  "tags": ["urgent", "password_reset"],
  "metadata": {
    "source": "web_form",
    "browser": "Chrome 120.0",
    "device_type": "desktop"
  },
  "classification": {
    "category": "account_access",
    "priority": "high",
    "confidence": 0.98,
    "reasoning": "User reports inability to reset password and access account.",
    "keywords": ["login", "password", "reset", "urgent"],
    "classified_at": "2026-07-03T10:32:10.789Z",
    "manual_override": false
  }
}
```

**cURL Example:**
```bash
curl http://localhost:3000/tickets/550e8400-e29b-41d4-a716-446655440000
```

---

## PUT /tickets/:id

Update an existing ticket.

**Description:**
Updates one or more fields of a ticket. All fields in the request body are optional; only provided fields will be updated.

**Request:**
```json
{
  "subject": "Updated subject",
  "description": "Updated description",
  "category": "technical_issue",
  "priority": "medium",
  "status": "in_progress",
  "assigned_to": "support_agent_2",
  "tags": ["updated", "in_progress"],
  "metadata": {
    "source": "web_form",
    "browser": "Firefox 125.0",
    "device_type": "mobile"
  }
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "cust_12345",
  "customer_email": "john.doe@example.com",
  "customer_name": "John Doe",
  "subject": "Updated subject",
  "description": "Updated description",
  "category": "technical_issue",
  "priority": "medium",
  "status": "in_progress",
  "created_at": "2026-07-03T10:30:45.123Z",
  "updated_at": "2026-07-03T12:45:30.789Z",
  "resolved_at": null,
  "assigned_to": "support_agent_2",
  "tags": ["updated", "in_progress"],
  "metadata": {
    "source": "web_form",
    "browser": "Firefox 125.0",
    "device_type": "mobile"
  },
  "classification": {
    "category": "account_access",
    "priority": "high",
    "confidence": 0.98,
    "reasoning": "User reports inability to reset password and access account.",
    "keywords": ["login", "password", "reset", "urgent"],
    "classified_at": "2026-07-03T10:32:10.789Z",
    "manual_override": false
  }
}
```

**cURL Example:**
```bash
curl -X PUT http://localhost:3000/tickets/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "assigned_to": "support_agent_2",
    "priority": "medium"
  }'
```

---

## DELETE /tickets/:id

Delete a ticket.

**Description:**
Permanently removes a ticket from the system. Returns no content on success.

**Response (204 No Content):**
Empty response body.

**cURL Example:**
```bash
curl -X DELETE http://localhost:3000/tickets/550e8400-e29b-41d4-a716-446655440000
```

---

## POST /tickets/:id/auto-classify

Auto-classify a ticket.

**Description:**
Triggers automatic classification for a specific ticket based on its subject and description. The classification process analyzes the content and assigns appropriate category and priority values, producing a confidence score and reasoning.

**Response (200 OK):**
```json
{
  "category": "account_access",
  "priority": "high",
  "confidence": 0.98,
  "reasoning": "User reports inability to reset password and access account.",
  "keywords": ["login", "password", "reset", "urgent"],
  "classified_at": "2026-07-03T10:32:10.789Z",
  "manual_override": false
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/tickets/550e8400-e29b-41d4-a716-446655440000/auto-classify
```

---

## Data Model

### Ticket

Represents a customer support ticket with its metadata and optional classification.

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Unique identifier, auto-generated |
| `customer_id` | string | Customer identifier (1-100 characters) |
| `customer_email` | string | Valid email address |
| `customer_name` | string | Customer name (1-100 characters) |
| `subject` | string | Ticket subject (1-200 characters) |
| `description` | string | Detailed description (10-2000 characters) |
| `category` | enum | See Category values below |
| `priority` | enum | See Priority values below |
| `status` | enum | See Status values below |
| `created_at` | ISO 8601 string | Timestamp of ticket creation |
| `updated_at` | ISO 8601 string | Timestamp of last update |
| `resolved_at` | ISO 8601 string \| null | When the ticket was resolved; null if unresolved |
| `assigned_to` | string \| null | Name or ID of assigned support agent; null if unassigned |
| `tags` | string[] | Array of tag strings for categorization |
| `metadata` | object | Source and device information |
| `classification` | object \| null | Auto-classification result; null if not classified |

### Category

Enum values for ticket category:
- `account_access` — Account login, access, or permission issues
- `technical_issue` — Technical problems or bugs with the service
- `billing_question` — Billing, invoice, or payment questions
- `feature_request` — Requests for new features or enhancements
- `bug_report` — Bug reports (for customers)
- `other` — Other issues not fitting above categories

### Priority

Enum values for ticket priority:
- `urgent` — Requires immediate action
- `high` — High importance, needs prompt attention
- `medium` — Standard priority
- `low` — Low priority, can be addressed later

### Status

Enum values for ticket status:
- `new` — Newly created, not yet reviewed
- `in_progress` — Currently being worked on
- `waiting_customer` — Awaiting customer response
- `resolved` — Issue has been resolved
- `closed` — Ticket is closed

### TicketMetadata

Additional context about the ticket source and device.

| Field | Type | Notes |
|-------|------|-------|
| `source` | enum | See Source values below |
| `browser` | string \| null | Browser name and version; null if not applicable |
| `device_type` | enum \| null | See DeviceType values below; null if not applicable |

### Source

Enum values for ticket source:
- `web_form` — Submitted via web form
- `email` — Submitted via email
- `api` — Submitted via API
- `chat` — Submitted via chat
- `phone` — Submitted via phone call

### DeviceType

Enum values for device type:
- `desktop` — Desktop computer
- `mobile` — Mobile device
- `tablet` — Tablet device

### ClassificationResult

The automatic classification analysis of a ticket.

| Field | Type | Notes |
|-------|------|-------|
| `category` | enum | Assigned category (see Category values) |
| `priority` | enum | Assigned priority (see Priority values) |
| `confidence` | number | Confidence score (0.0 to 1.0) |
| `reasoning` | string | Human-readable explanation of the classification |
| `keywords` | string[] | Keywords extracted from ticket content |
| `classified_at` | ISO 8601 string | When the classification was performed |
| `manual_override` | boolean | Whether this classification was manually overridden |

---

## Import Summary Format

The response from the import endpoint includes a summary of the import operation.

| Field | Type | Notes |
|-------|------|-------|
| `total` | number | Total records in the import file |
| `successful` | number | Number of tickets successfully created |
| `failed` | number | Number of tickets that failed validation |
| `ticketIds` | string[] | Array of UUIDs for successfully created tickets |
| `errors` | array | Array of error objects for failed records |

### ImportError

| Field | Type | Notes |
|-------|------|-------|
| `index` | number | Zero-based row index in the import file |
| `message` | string | Validation error message(s), semicolon-separated if multiple |

**Example Import Summary:**
```json
{
  "total": 5,
  "successful": 4,
  "failed": 1,
  "ticketIds": [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002",
    "550e8400-e29b-41d4-a716-446655440003",
    "550e8400-e29b-41d4-a716-446655440004"
  ],
  "errors": [
    {
      "index": 2,
      "message": "customer_email: must be a valid email address; metadata.source: must be one of: web_form, email, api, chat, phone"
    }
  ]
}
```

---

## Error Responses

### Validation Error (400 Bad Request)

Returned when request validation fails (e.g., invalid field values, missing required fields).

**Response Body:**
```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "customer_email",
      "message": "must be a valid email address"
    },
    {
      "field": "description",
      "message": "must be between 10 and 2000 characters"
    },
    {
      "field": "metadata.source",
      "message": "must be one of: web_form, email, api, chat, phone"
    }
  ]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust_123",
    "customer_email": "invalid-email",
    "customer_name": "John",
    "subject": "Test",
    "description": "Short",
    "metadata": {
      "source": "invalid_source"
    }
  }'
```

### Malformed File Error (400 Bad Request)

Returned when an import file cannot be parsed (e.g., invalid CSV, malformed JSON, invalid XML).

**Response Body:**
```json
{
  "message": "Invalid JSON format. Expected valid JSON array of ticket objects.",
  "statusCode": 400
}
```

### Import Format Detection Error (400 Bad Request)

Returned when the file format cannot be determined and no explicit format is provided.

**Response Body:**
```json
{
  "message": "Could not determine import format from file \"tickets.txt\". Provide ?format=csv|json|xml.",
  "statusCode": 400
}
```

### Not Found Error (404 Not Found)

Returned when trying to access or modify a ticket that does not exist.

**Response Body:**
```json
{
  "message": "Not Found",
  "statusCode": 404
}
```

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | OK — Request succeeded |
| `201` | Created — Resource created successfully (POST /tickets) |
| `204` | No Content — Request succeeded with no response body (DELETE) |
| `400` | Bad Request — Validation error, malformed file, or format detection error |
| `404` | Not Found — Ticket does not exist |

---

## Notes

- All timestamps are in ISO 8601 format with UTC timezone.
- Ticket IDs are UUIDs (version 4).
- Field names in JSON use snake_case.
- The API supports filtering on GET /tickets; multiple filters are combined with AND logic.
- Import operations are partially successful: valid records are created even if some records fail validation.
- The autoClassify feature in POST /tickets/import runs classification on all successfully created tickets in that batch.
