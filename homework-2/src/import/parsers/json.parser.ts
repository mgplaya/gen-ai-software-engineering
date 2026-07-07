import { ImportParseError, RawTicketRecord } from '../import.types';

export function parseJsonTickets(content: string): RawTicketRecord[] {
  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch (error) {
    throw new ImportParseError(`Malformed JSON file: ${(error as Error).message}`);
  }

  if (!Array.isArray(parsed)) {
    throw new ImportParseError('Malformed JSON file: expected a top-level array of ticket records');
  }

  return parsed.map((record) => ({
    customer_id: record?.customer_id,
    customer_email: record?.customer_email,
    customer_name: record?.customer_name,
    subject: record?.subject,
    description: record?.description,
    category: record?.category,
    priority: record?.priority,
    assigned_to: record?.assigned_to,
    // Pass non-array tags through so DTO validation reports them instead of silently dropping data.
    tags: record?.tags == null ? [] : record.tags,
    metadata: {
      source: record?.metadata?.source,
      browser: record?.metadata?.browser,
      device_type: record?.metadata?.device_type,
    },
  }));
}
