import { ImportParseError, RawTicketRecord } from '../raw-ticket-record';

/**
 * Parses a JSON file into raw ticket records. Expected shape: a top-level
 * array of ticket objects, each matching the CreateTicketDto shape
 * (nested "metadata" object, "tags" array).
 */
export function parseJsonTickets(content: string): RawTicketRecord[] {
  let data: unknown;
  try {
    data = JSON.parse(content);
  } catch (error) {
    throw new ImportParseError(`Malformed JSON file: ${(error as Error).message}`);
  }

  if (!Array.isArray(data)) {
    throw new ImportParseError('JSON file must contain a top-level array of tickets');
  }

  return data as RawTicketRecord[];
}
