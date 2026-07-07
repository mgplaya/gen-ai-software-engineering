import { XMLParser, XMLValidator } from 'fast-xml-parser';
import { ImportParseError, RawTicketRecord } from '../import.types';

const xmlParser = new XMLParser({
  ignoreAttributes: true,
  trimValues: true,
  parseTagValue: false,
});

function ensureArray<T>(value: T | T[] | undefined): T[] {
  if (value === undefined) return [];
  return Array.isArray(value) ? value : [value];
}

/** Empty XML elements parse to '' — normalise them to undefined strings. */
function text(value: unknown): string | undefined {
  if (value === undefined || value === null) return undefined;
  const str = String(value);
  return str.length > 0 ? str : undefined;
}

export function parseXmlTickets(content: string): RawTicketRecord[] {
  const validation = XMLValidator.validate(content);
  if (validation !== true) {
    throw new ImportParseError(`Malformed XML file: ${validation.err.msg}`);
  }

  const parsed = xmlParser.parse(content);

  if (!parsed?.tickets || typeof parsed.tickets !== 'object') {
    throw new ImportParseError(
      'Malformed XML file: expected a <tickets> root element containing <ticket> children',
    );
  }

  const tickets = ensureArray(parsed.tickets.ticket);
  if (tickets.length === 0) {
    throw new ImportParseError(
      'Malformed XML file: no <ticket> elements found under the <tickets> root',
    );
  }

  return tickets.map((t: any) => ({
    customer_id: text(t?.customer_id),
    customer_email: text(t?.customer_email),
    customer_name: text(t?.customer_name),
    subject: text(t?.subject),
    description: text(t?.description),
    category: text(t?.category),
    priority: text(t?.priority),
    assigned_to: text(t?.assigned_to),
    tags: ensureArray(t?.tags?.tag)
      .map((tag) => String(tag))
      .filter((tag) => tag.length > 0),
    metadata: {
      source: text(t?.metadata?.source),
      browser: text(t?.metadata?.browser),
      device_type: text(t?.metadata?.device_type),
    },
  }));
}
