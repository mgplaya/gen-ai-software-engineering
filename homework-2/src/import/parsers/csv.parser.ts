import { parse } from 'csv-parse/sync';
import { ImportParseError, RawTicketRecord } from '../import.types';

interface CsvRow {
  customer_id?: string;
  customer_email?: string;
  customer_name?: string;
  subject?: string;
  description?: string;
  category?: string;
  priority?: string;
  assigned_to?: string;
  tags?: string;
  metadata_source?: string;
  metadata_browser?: string;
  metadata_device_type?: string;
}

export function parseCsvTickets(content: string): RawTicketRecord[] {
  let rows: CsvRow[];
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
    category: row.category,
    priority: row.priority,
    assigned_to: row.assigned_to,
    tags: row.tags ? row.tags.split('|').filter((t) => t.length > 0) : [],
    metadata: {
      source: row.metadata_source,
      browser: row.metadata_browser,
      device_type: row.metadata_device_type,
    },
  }));
}
