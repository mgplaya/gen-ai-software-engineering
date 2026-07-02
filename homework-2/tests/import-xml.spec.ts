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

const SINGLE_TICKET_XML = `<?xml version="1.0" encoding="UTF-8"?>
<tickets>
  <ticket>
    <customer_id>CUST-999</customer_id>
    <customer_email>single@example.com</customer_email>
    <customer_name>Single Ticket</customer_name>
    <subject>Only one ticket in this file</subject>
    <description>This file intentionally contains a single ticket node, not an array.</description>
    <tags><tag>solo</tag></tags>
    <metadata><source>api</source></metadata>
  </ticket>
</tickets>`;

describe('XML import (Task 3: test_import_xml)', () => {
  it('imports all 30 tickets from sample_tickets.xml', async () => {
    const { importService } = buildServices();
    const summary = await importService.import(fixture('sample_tickets.xml'), 'xml');

    expect(summary.total).toBe(30);
    expect(summary.successful).toBe(30);
    expect(summary.failed).toBe(0);
  });

  it('parses the <tag> list under <tags> into a string array', async () => {
    const { importService, ticketsService } = buildServices();
    const summary = await importService.import(fixture('sample_tickets.xml'), 'xml');

    const ticket = ticketsService.findOne(summary.ticketIds[0]);
    expect(Array.isArray(ticket.tags)).toBe(true);
    expect(ticket.tags.length).toBeGreaterThan(0);
  });

  it('reports per-record errors for invalid_tickets.xml without aborting the batch', async () => {
    const { importService } = buildServices();
    const summary = await importService.import(fixture('invalid_tickets.xml'), 'xml');

    expect(summary.total).toBe(5);
    expect(summary.failed).toBe(4);
    expect(summary.successful).toBe(1);
  });

  it('throws BadRequestException for a malformed XML file (unclosed tag)', async () => {
    const { importService } = buildServices();
    await expect(importService.import(fixture('malformed.xml'), 'xml')).rejects.toBeInstanceOf(
      BadRequestException,
    );
  });

  it('handles a single <ticket> node not wrapped in an array by the XML parser', async () => {
    const { importService } = buildServices();
    const summary = await importService.import(SINGLE_TICKET_XML, 'xml');

    expect(summary.total).toBe(1);
    expect(summary.successful).toBe(1);
  });

  it('throws BadRequestException for well-formed XML missing the <tickets><ticket> structure', async () => {
    const { importService } = buildServices();
    await expect(
      importService.import('<?xml version="1.0"?><tickets></tickets>', 'xml'),
    ).rejects.toBeInstanceOf(BadRequestException);
  });
});
