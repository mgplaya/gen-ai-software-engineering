import { BadRequestException } from '@nestjs/common';
import { ClassificationService } from '../src/classification/classification.service';
import { ImportService } from '../src/import/import.service';
import { TicketsService } from '../src/tickets/tickets.service';
import { fixture } from './helpers';

const SINGLE_TICKET_XML = `<?xml version="1.0" encoding="UTF-8"?>
<tickets>
  <ticket>
    <customer_id>CUST-500</customer_id>
    <customer_email>solo.user@example.com</customer_email>
    <customer_name>Solo User</customer_name>
    <subject>Single ticket import check</subject>
    <description>This description is long enough to satisfy the import validation rules.</description>
    <category>technical_issue</category>
    <priority>high</priority>
    <assigned_to></assigned_to>
    <tags>
      <tag>single</tag>
    </tags>
    <metadata>
      <source>api</source>
      <browser>Firefox</browser>
      <device_type>desktop</device_type>
    </metadata>
  </ticket>
</tickets>`;

describe('ImportService — XML', () => {
  let ticketsService: TicketsService;
  let importService: ImportService;

  beforeEach(() => {
    ticketsService = new TicketsService(new ClassificationService());
    importService = new ImportService(ticketsService);
  });

  it('imports all 30 valid tickets from sample_tickets.xml', async () => {
    const summary = await importService.import(fixture('sample_tickets.xml'), 'xml');

    expect(summary.total).toBe(30);
    expect(summary.successful).toBe(30);
    expect(summary.failed).toBe(0);
    expect(summary.ticketIds).toHaveLength(30);
    expect(summary.errors).toEqual([]);
  });

  it('imports a document containing exactly one ticket element', async () => {
    const summary = await importService.import(SINGLE_TICKET_XML, 'xml');

    expect(summary.total).toBe(1);
    expect(summary.successful).toBe(1);
    expect(summary.failed).toBe(0);
    expect(summary.ticketIds).toHaveLength(1);
    expect(summary.errors).toEqual([]);
  });

  it('reports per-ticket errors for invalid_tickets.xml while importing the valid ticket', async () => {
    const summary = await importService.import(fixture('invalid_tickets.xml'), 'xml');

    expect(summary.total).toBe(4);
    expect(summary.successful).toBe(1);
    expect(summary.failed).toBe(3);
    expect(summary.ticketIds).toHaveLength(1);
    expect(summary.errors).toHaveLength(3);
  });

  it('rejects malformed.xml with BadRequestException', async () => {
    await expect(importService.import(fixture('malformed.xml'), 'xml')).rejects.toBeInstanceOf(
      BadRequestException,
    );
  });

  it('rejects an XML document with a wrong root element', async () => {
    const wrongRoot = '<?xml version="1.0"?><items><item></item></items>';

    await expect(importService.import(wrongRoot, 'xml')).rejects.toBeInstanceOf(
      BadRequestException,
    );

    // a <tickets> root without any <ticket> children is also malformed
    const emptyRoot = '<?xml version="1.0"?><tickets></tickets>';
    await expect(importService.import(emptyRoot, 'xml')).rejects.toBeInstanceOf(
      BadRequestException,
    );
  });
});
