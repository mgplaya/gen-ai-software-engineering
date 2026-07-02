export interface ImportRecordError {
  index: number;
  message: string;
}

export interface ImportSummary {
  total: number;
  successful: number;
  failed: number;
  ticketIds: string[];
  errors: ImportRecordError[];
}

export type ImportFormat = 'csv' | 'json' | 'xml';

export const SUPPORTED_IMPORT_FORMATS: ImportFormat[] = ['csv', 'json', 'xml'];
