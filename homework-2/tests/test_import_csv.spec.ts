import { BadRequestException } from '@nestjs/common';
import { ClassificationService } from '../src/classification/classification.service';
import { ImportService } from '../src/import/import.service';
import { TicketsService } from '../src/tickets/tickets.service';
import { fixture } from './helpers';

describe('ImportService — CSV', () => {
  let ticketsService: TicketsService;
  let importService: ImportService;

  beforeEach(() => {
    ticketsService = new TicketsService(new ClassificationService());
    importService = new ImportService(ticketsService);
  });

  it('imports all 50 valid rows from sample_tickets.csv', async () => {
    const summary = await importService.import(fixture('sample_tickets.csv'), 'csv');

    expect(summary.total).toBe(50);
    expect(summary.successful).toBe(50);
    expect(summary.failed).toBe(0);
    expect(summary.ticketIds).toHaveLength(50);
    expect(summary.errors).toEqual([]);
  });

  it('splits pipe-separated tags into string arrays', async () => {
    const summary = await importService.import(fixture('sample_tickets.csv'), 'csv');

    const ticket = ticketsService.findOne(summary.ticketIds[0]);
    expect(ticket.tags).toEqual(['login', 'password']);
  });

  it('reports per-row errors for invalid_tickets.csv while importing the valid row', async () => {
    const summary = await importService.import(fixture('invalid_tickets.csv'), 'csv');

    expect(summary.total).toBe(5);
    expect(summary.successful).toBe(1);
    expect(summary.failed).toBe(4);
    expect(summary.ticketIds).toHaveLength(1);
    expect(summary.errors).toHaveLength(4);

    const indexes = summary.errors.map((error) => error.index).sort((a, b) => a - b);
    expect(indexes).toEqual([0, 1, 2, 3]);
    for (const error of summary.errors) {
      expect(typeof error.index).toBe('number');
      expect(typeof error.message).toBe('string');
      expect(error.message.length).toBeGreaterThan(0);
    }
  });

  it('rejects malformed.csv with BadRequestException', async () => {
    await expect(importService.import(fixture('malformed.csv'), 'csv')).rejects.toBeInstanceOf(
      BadRequestException,
    );
  });

  it('applies default category and priority when the row leaves them empty', async () => {
    const summary = await importService.import(fixture('sample_tickets.csv'), 'csv');

    const ticket = ticketsService.findOne(summary.ticketIds[0]);
    expect(ticket.category).toBe('other');
    expect(ticket.priority).toBe('medium');
    expect(ticket.classification).toBeNull();
  });

  it('classifies every imported ticket when autoClassify is true', async () => {
    const summary = await importService.import(fixture('sample_tickets.csv'), 'csv', true);

    expect(summary.successful).toBe(50);
    for (const id of summary.ticketIds.slice(0, 5)) {
      const ticket = ticketsService.findOne(id);
      expect(ticket.classification).not.toBeNull();
    }

    const first = ticketsService.findOne(summary.ticketIds[0]);
    expect(first.subject).toBe("Can't access my account after password reset");
    expect(first.classification).not.toBeNull();
    expect(first.classification!.category).toBe('account_access');
    expect(first.classification!.priority).toBe('urgent');
  });
});
