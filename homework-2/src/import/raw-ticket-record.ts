/**
 * Common intermediate shape produced by every format parser (CSV/JSON/XML)
 * before it is converted into a CreateTicketDto and validated.
 */
export interface RawTicketRecord {
  customer_id?: unknown;
  customer_email?: unknown;
  customer_name?: unknown;
  subject?: unknown;
  description?: unknown;
  category?: unknown;
  priority?: unknown;
  assigned_to?: unknown;
  tags?: unknown;
  metadata?: {
    source?: unknown;
    browser?: unknown;
    device_type?: unknown;
  };
}

/** Raised when a file's content cannot be parsed at all (bad syntax). */
export class ImportParseError extends Error {}
