import { parse } from 'csv-parse/sync';
import { ImportParseError, RawTicketRecord } from '../raw-ticket-record';

/** Tag list columns use "|" as separator (commas are already used by CSV itself). */
const TAG_SEPARATOR = '|';

/**
 * Parses a flat CSV file into raw ticket records. Expected columns:
 * customer_id, customer_email, customer_name, subject, description,
 * category, priority, assigned_to, tags, metadata_source, metadata_browser,
 * metadata_device_type.
 */
export function parseCsvTickets(content: string): RawTicketRecord[] {
  let rows: Record<string, string>[];
  try {
    rows = parse(content, {
      columns: true,
      skip_empty_lines: true,
      trim: true,
    });
  } catch (error) {
    throw new ImportParseError(`Malformed CSV file: ${(error as Error).message}`);
  }

  return rows.map((row) => ({
    customer_id: row.customer_id,
    customer_email: row.customer_email,
    customer_name: row.customer_name,
    subject: row.subject,
    description: row.description,
    category: row.category || undefined,
    priority: row.priority || undefined,
    assigned_to: row.assigned_to || undefined,
    tags: row.tags
      ? row.tags
          .split(TAG_SEPARATOR)
          .map((tag) => tag.trim())
          .filter(Boolean)
      : [],
    metadata: {
      source: row.metadata_source,
      browser: row.metadata_browser || undefined,
      device_type: row.metadata_device_type || undefined,
    },
  }));
}
