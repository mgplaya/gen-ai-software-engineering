import { BadRequestException, Injectable, Logger } from '@nestjs/common';
import { plainToInstance } from 'class-transformer';
import { validate } from 'class-validator';
import { CreateTicketDto } from '../tickets/dto/create-ticket.dto';
import { Ticket } from '../tickets/entities/ticket.entity';
import { TicketsService } from '../tickets/tickets.service';
import { ImportFormat, ImportSummary, SUPPORTED_IMPORT_FORMATS } from './import-summary';
import { parseCsvTickets } from './parsers/csv.parser';
import { parseJsonTickets } from './parsers/json.parser';
import { parseXmlTickets } from './parsers/xml.parser';
import { ImportParseError, RawTicketRecord } from './raw-ticket-record';

@Injectable()
export class ImportService {
  private readonly logger = new Logger(ImportService.name);

  constructor(private readonly ticketsService: TicketsService) {}

  async import(content: string, format: ImportFormat, autoClassify = false): Promise<ImportSummary> {
    if (!SUPPORTED_IMPORT_FORMATS.includes(format)) {
      throw new BadRequestException(
        `Unsupported import format "${format}". Supported formats: ${SUPPORTED_IMPORT_FORMATS.join(', ')}`,
      );
    }

    let records: RawTicketRecord[];
    try {
      records = this.parse(content, format);
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
        category: record.category || undefined,
        priority: record.priority || undefined,
        assigned_to: record.assigned_to || undefined,
        tags: record.tags ?? [],
        metadata: {
          source: record.metadata?.source,
          browser: record.metadata?.browser || undefined,
          device_type: record.metadata?.device_type || undefined,
        },
      });

      const validationErrors = await validate(dto);
      if (validationErrors.length > 0) {
        summary.failed += 1;
        const messages = validationErrors.flatMap((e) => Object.values(e.constraints ?? {}));
        summary.errors.push({ index, message: messages.join('; ') });
        continue;
      }

      const ticket: Ticket = this.ticketsService.create(dto);
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
