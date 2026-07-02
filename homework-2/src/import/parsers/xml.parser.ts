import { XMLParser, XMLValidator } from 'fast-xml-parser';
import { ImportParseError, RawTicketRecord } from '../raw-ticket-record';

function ensureArray<T>(value: T | T[] | undefined | null): T[] {
  if (value === undefined || value === null) return [];
  return Array.isArray(value) ? value : [value];
}

/**
 * Parses an XML file into raw ticket records. Expected shape:
 * <tickets><ticket>...<tags><tag>x</tag></tags><metadata>...</metadata></ticket></tickets>
 */
export function parseXmlTickets(content: string): RawTicketRecord[] {
  const validation = XMLValidator.validate(content);
  if (validation !== true) {
    throw new ImportParseError(`Malformed XML file: ${validation.err.msg}`);
  }

  // parseTagValue: false keeps every leaf as a raw string (e.g. a numeric-looking
  // customer_id like "10023" must not be silently coerced into a number).
  const parser = new XMLParser({ ignoreAttributes: true, trimValues: true, parseTagValue: false });
  const parsed = parser.parse(content);
  const root = parsed?.tickets;
  if (!root || !root.ticket) {
    throw new ImportParseError('XML file must have a root <tickets><ticket>...</ticket></tickets> structure');
  }

  return ensureArray(root.ticket).map((node: Record<string, any>) => ({
    customer_id: node.customer_id,
    customer_email: node.customer_email,
    customer_name: node.customer_name,
    subject: node.subject,
    description: node.description,
    category: node.category || undefined,
    priority: node.priority || undefined,
    assigned_to: node.assigned_to || undefined,
    tags: node.tags ? ensureArray(node.tags.tag).filter((tag) => tag != null && tag !== '') : [],
    metadata: {
      source: node.metadata?.source,
      browser: node.metadata?.browser || undefined,
      device_type: node.metadata?.device_type || undefined,
    },
  }));
}
