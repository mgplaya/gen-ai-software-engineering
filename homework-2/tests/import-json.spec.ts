import { BadRequestException } from '@nestjs/common';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { ClassificationService } from '../src/classification/classification.service';
import { ImportService } from '../src/import/import.service';
import { TicketsService } from '../src/tickets/tickets.service';

const fixture = (name: string) => readFileSync(join(__dirname, 'fixtures', name), 'utf-8');

function buildServices() {
  const ticketsService = new TicketsService(new ClassificationService());
  const importService = new ImportService(ticketsService);
  return { ticketsService, importService };
}

describe('JSON import (Task 3: test_import_json)', () => {
  it('imports all 20 tickets from sample_tickets.json', async () => {
    const { importService } = buildServices();
    const summary = await importService.import(fixture('sample_tickets.json'), 'json');

    expect(summary.total).toBe(20);
    expect(summary.successful).toBe(20);
    expect(summary.failed).toBe(0);
  });

  it('rejects a JSON file whose top-level value is not an array', async () => {
    const { importService } = buildServices();
    await expect(
      importService.import(JSON.stringify({ not: 'an array' }), 'json'),
    ).rejects.toBeInstanceOf(BadRequestException);
  });

  it('reports per-record errors for invalid_tickets.json without aborting the batch', async () => {
    const { importService } = buildServices();
    const summary = await importService.import(fixture('invalid_tickets.json'), 'json');

    expect(summary.total).toBe(5);
    expect(summary.failed).toBe(4);
    expect(summary.successful).toBe(1);
  });

  it('throws BadRequestException for a malformed JSON file', async () => {
    const { importService } = buildServices();
    await expect(importService.import(fixture('malformed.json'), 'json')).rejects.toBeInstanceOf(
      BadRequestException,
    );
  });

  it('preserves the nested tags array and metadata object from the JSON source', async () => {
    const { importService, ticketsService } = buildServices();
    const summary = await importService.import(fixture('sample_tickets.json'), 'json');

    const ticket = ticketsService.findOne(summary.ticketIds[0]);
    expect(Array.isArray(ticket.tags)).toBe(true);
    expect(ticket.metadata.source).toBeDefined();
  });

  it('rejects an unsupported import format before attempting to parse', async () => {
    const { importService } = buildServices();
    await expect(importService.import('[]', 'yaml' as any)).rejects.toBeInstanceOf(BadRequestException);
  });
});
