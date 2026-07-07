import { BadRequestException } from '@nestjs/common';
import { ClassificationService } from '../src/classification/classification.service';
import { ImportService } from '../src/import/import.service';
import { TicketsService } from '../src/tickets/tickets.service';
import { fixture } from './helpers';

describe('ImportService — JSON', () => {
  let ticketsService: TicketsService;
  let importService: ImportService;

  beforeEach(() => {
    ticketsService = new TicketsService(new ClassificationService());
    importService = new ImportService(ticketsService);
  });

  it('imports all 20 valid records from sample_tickets.json', async () => {
    const summary = await importService.import(fixture('sample_tickets.json'), 'json');

    expect(summary.total).toBe(20);
    expect(summary.successful).toBe(20);
    expect(summary.failed).toBe(0);
    expect(summary.ticketIds).toHaveLength(20);
    expect(summary.errors).toEqual([]);
  });

  it('reports per-record errors for invalid_tickets.json while importing the valid record', async () => {
    const summary = await importService.import(fixture('invalid_tickets.json'), 'json');

    expect(summary.total).toBe(4);
    expect(summary.successful).toBe(1);
    expect(summary.failed).toBe(3);
    expect(summary.ticketIds).toHaveLength(1);
    expect(summary.errors).toHaveLength(3);
    for (const error of summary.errors) {
      expect(typeof error.index).toBe('number');
      expect(typeof error.message).toBe('string');
      expect(error.message.length).toBeGreaterThan(0);
    }
  });

  it('rejects malformed.json with BadRequestException mentioning "Malformed"', async () => {
    const promise = importService.import(fixture('malformed.json'), 'json');

    await expect(promise).rejects.toBeInstanceOf(BadRequestException);
    await expect(importService.import(fixture('malformed.json'), 'json')).rejects.toThrow(
      /Malformed/i,
    );
  });

  it('rejects a non-array JSON top level with BadRequestException', async () => {
    await expect(importService.import('{"customer_id":"X"}', 'json')).rejects.toBeInstanceOf(
      BadRequestException,
    );

    // unsupported format strings are rejected up front with the supported list
    await expect(importService.import('[]', 'yaml')).rejects.toThrow(/csv, json, xml/);
  });

  it('preserves tags arrays and nested metadata on imported tickets', async () => {
    const summary = await importService.import(fixture('sample_tickets.json'), 'json');

    const ticket = ticketsService.findOne(summary.ticketIds[0]);
    expect(ticket.customer_id).toBe('CUST-100');
    expect(ticket.tags).toEqual(['login', 'password']);
    expect(ticket.metadata.source).toBe('web_form');
    expect(ticket.metadata.browser).toBe('Chrome');
    expect(ticket.metadata.device_type).toBe('desktop');
  });
});
