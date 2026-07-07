export const SUPPORTED_IMPORT_FORMATS = ['csv', 'json', 'xml'] as const;
export type ImportFormat = (typeof SUPPORTED_IMPORT_FORMATS)[number];

export interface RawTicketRecord {
  customer_id?: string;
  customer_email?: string;
  customer_name?: string;
  subject?: string;
  description?: string;
  category?: string;
  priority?: string;
  assigned_to?: string;
  tags?: string[];
  metadata?: {
    source?: string;
    browser?: string;
    device_type?: string;
  };
}

export class ImportParseError extends Error {}

export interface ImportRowError {
  index: number;
  message: string;
}

export interface ImportSummary {
  total: number;
  successful: number;
  failed: number;
  ticketIds: string[];
  errors: ImportRowError[];
}
