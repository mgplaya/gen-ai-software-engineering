import { BadRequestException, Injectable, Logger } from '@nestjs/common';
import { plainToInstance } from 'class-transformer';
import { validate } from 'class-validator';
import { flattenValidationErrors } from '../app.factory';
import { CreateTicketDto } from '../tickets/dto/create-ticket.dto';
import { TicketsService } from '../tickets/tickets.service';
import {
  ImportFormat,
  ImportParseError,
  ImportSummary,
  RawTicketRecord,
  SUPPORTED_IMPORT_FORMATS,
} from './import.types';
import { parseCsvTickets } from './parsers/csv.parser';
import { parseJsonTickets } from './parsers/json.parser';
import { parseXmlTickets } from './parsers/xml.parser';

/** CSV parsing yields '' for blank cells — treat those as absent so DTO defaults apply. */
function emptyToUndefined(value: string | undefined): string | undefined {
  return value === '' ? undefined : value;
}

@Injectable()
export class ImportService {
  private readonly logger = new Logger(ImportService.name);

  constructor(private readonly ticketsService: TicketsService) {}

  async import(content: string, format: string, autoClassify = false): Promise<ImportSummary> {
    if (!(SUPPORTED_IMPORT_FORMATS as readonly string[]).includes(format)) {
      throw new BadRequestException(
        `Unsupported import format "${format}". Supported formats: ${SUPPORTED_IMPORT_FORMATS.join(', ')}`,
      );
    }

    let records: RawTicketRecord[];
    try {
      records = this.parse(content, format as ImportFormat);
    } catch (error) {
      if (error instanceof ImportParseError) {
        throw new BadRequestException(error.message);
      }
      throw error;
    }

    const summary: ImportSummary = {
      total: records.length,
      successful: 0,
      failed: 0,
      ticketIds: [],
      errors: [],
    };

    for (const [index, record] of records.entries()) {
      const dto = plainToInstance(CreateTicketDto, {
        customer_id: record.customer_id,
        customer_email: record.customer_email,
        customer_name: record.customer_name,
        subject: record.subject,
        description: record.description,
        category: emptyToUndefined(record.category),
        priority: emptyToUndefined(record.priority),
        assigned_to: emptyToUndefined(record.assigned_to),
        tags: record.tags ?? [],
        metadata: {
          source: emptyToUndefined(record.metadata?.source),
          browser: emptyToUndefined(record.metadata?.browser),
          device_type: emptyToUndefined(record.metadata?.device_type),
        },
      });

      const validationErrors = await validate(dto);
      if (validationErrors.length > 0) {
        summary.failed += 1;
        const message = flattenValidationErrors(validationErrors)
          .map((d) => `${d.field}: ${d.message}`)
          .join('; ');
        summary.errors.push({ index, message });
        continue;
      }

      const ticket = this.ticketsService.create(dto);
      if (autoClassify) {
        this.ticketsService.autoClassify(ticket.id);
      }
      summary.successful += 1;
      summary.ticketIds.push(ticket.id);
    }

    this.logger.log(
      `Import (${format}) finished: total=${summary.total} successful=${summary.successful} failed=${summary.failed}`,
    );
    return summary;
  }

  private parse(content: string, format: ImportFormat): RawTicketRecord[] {
    switch (format) {
      case 'csv':
        return parseCsvTickets(content);
      case 'json':
        return parseJsonTickets(content);
      case 'xml':
        return parseXmlTickets(content);
    }
  }
}
