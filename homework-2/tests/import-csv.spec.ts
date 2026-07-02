import { BadRequestException } from '@nestjs/common';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { ClassificationService } from '../src/classification/classification.service';
import { ImportService } from '../src/import/import.service';
import { TicketCategory, TicketPriority } from '../src/tickets/entities/ticket.entity';
import { TicketsService } from '../src/tickets/tickets.service';

const fixture = (name: string) => readFileSync(join(__dirname, 'fixtures', name), 'utf-8');

function buildServices() {
  const ticketsService = new TicketsService(new ClassificationService());
  const importService = new ImportService(ticketsService);
  return { ticketsService, importService };
}

describe('CSV import (Task 3: test_import_csv)', () => {
  it('imports all 50 tickets from sample_tickets.csv', async () => {
    const { importService } = buildServices();
    const summary = await importService.import(fixture('sample_tickets.csv'), 'csv');

    expect(summary.total).toBe(50);
    expect(summary.successful).toBe(50);
    expect(summary.failed).toBe(0);
  });

  it('splits the pipe-separated tags column into an array', async () => {
    const { importService, ticketsService } = buildServices();
    const summary = await importService.import(fixture('sample_tickets.csv'), 'csv');

    const ticket = ticketsService.findOne(summary.ticketIds[0]);
    expect(Array.isArray(ticket.tags)).toBe(true);
    expect(ticket.tags.length).toBeGreaterThan(0);
  });

  it('reports per-row errors for invalid_tickets.csv without aborting the batch', async () => {
    const { importService } = buildServices();
    const summary = await importService.import(fixture('invalid_tickets.csv'), 'csv');

    expect(summary.total).toBe(5);
    expect(summary.failed).toBe(4);
    expect(summary.successful).toBe(1);
    expect(summary.errors).toHaveLength(4);
    expect(summary.errors[0]).toEqual(expect.objectContaining({ index: 0, message: expect.any(String) }));
  });

  it('throws BadRequestException for a malformed CSV file', async () => {
    const { importService } = buildServices();
    await expect(importService.import(fixture('malformed.csv'), 'csv')).rejects.toBeInstanceOf(
      BadRequestException,
    );
  });

  it('defaults category and priority when the columns are empty', async () => {
    const { importService, ticketsService } = buildServices();
    const summary = await importService.import(fixture('sample_tickets.csv'), 'csv');

    const ticket = ticketsService.findOne(summary.ticketIds[0]);
    expect(ticket.category).toBe(TicketCategory.OTHER);
    expect(ticket.priority).toBe(TicketPriority.MEDIUM);
  });

  it('runs auto-classification on every imported ticket when autoClassify=true', async () => {
    const { importService, ticketsService } = buildServices();
    const summary = await importService.import(fixture('sample_tickets.csv'), 'csv', true);

    for (const id of summary.ticketIds) {
      expect(ticketsService.findOne(id).classification).not.toBeNull();
    }
  });

  it('leaves optional metadata columns (browser/device_type) unset when blank', async () => {
    const csv = [
      'customer_id,customer_email,customer_name,subject,description,assigned_to,tags,metadata_source,metadata_browser,metadata_device_type',
      'CUST-500,minimal@example.com,Minimal Row,Minimal ticket subject,This description is long enough to pass validation.,,,web_form,,',
    ].join('\n');

    const { importService, ticketsService } = buildServices();
    const summary = await importService.import(csv, 'csv');

    const ticket = ticketsService.findOne(summary.ticketIds[0]);
    expect(ticket.metadata.browser).toBeNull();
    expect(ticket.metadata.device_type).toBeNull();
  });
});
