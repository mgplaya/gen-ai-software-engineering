import { INestApplication } from '@nestjs/common';
import request from 'supertest';
import { createApp } from '../src/app.factory';
import { fixture, validPayload } from './helpers';

const ISO_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/;

describe('Integration scenarios', () => {
  let app: INestApplication;
  let http: any;

  beforeEach(async () => {
    app = await createApp();
    // Listen on an ephemeral port: concurrent supertest requests against a
    // non-listening server race on listen() and fail with ECONNRESET.
    await app.listen(0);
    http = app.getHttpServer();
  });

  afterEach(async () => {
    await app.close();
  });

  it('supports the full ticket lifecycle: create, classify, progress, resolve, delete', async () => {
    const created = await request(http)
      .post('/tickets')
      .send(validPayload())
      .expect(201);
    const id = created.body.id;
    expect(created.body.classification).toBeNull();

    const classified = await request(http).post(`/tickets/${id}/auto-classify`);
    expect(classified.status).toBe(200);
    expect(classified.body.category).toBeDefined();
    expect(classified.body.priority).toBeDefined();

    const inProgress = await request(http)
      .put(`/tickets/${id}`)
      .send({ status: 'in_progress' });
    expect(inProgress.status).toBe(200);
    expect(inProgress.body.status).toBe('in_progress');

    const resolved = await request(http)
      .put(`/tickets/${id}`)
      .send({ status: 'resolved' });
    expect(resolved.status).toBe(200);
    expect(resolved.body.status).toBe('resolved');
    expect(resolved.body.resolved_at).not.toBeNull();
    expect(resolved.body.resolved_at).toMatch(ISO_RE);

    await request(http).delete(`/tickets/${id}`).expect(204);
    await request(http).get(`/tickets/${id}`).expect(404);
  });

  it('imports the sample CSV with auto-classification applied to every ticket', async () => {
    const res = await request(http)
      .post('/tickets/import?autoClassify=true')
      .attach('file', Buffer.from(fixture('sample_tickets.csv')), 'sample_tickets.csv');

    expect(res.status).toBe(200);
    expect(res.body.successful).toBe(50);
    expect(res.body.failed).toBe(0);
    expect(res.body.ticketIds).toHaveLength(50);

    const list = await request(http).get('/tickets');
    expect(list.status).toBe(200);
    expect(list.body).toHaveLength(50);
    for (const ticket of list.body) {
      expect(ticket.classification).not.toBeNull();
    }
  });

  it('handles 25 concurrent ticket creations with distinct ids', async () => {
    const responses = await Promise.all(
      Array.from({ length: 25 }, (_, i) =>
        request(http)
          .post('/tickets')
          .send(validPayload({ customer_id: `CUST-${100 + i}` })),
      ),
    );

    for (const res of responses) {
      expect(res.status).toBe(201);
    }
    const ids = new Set(responses.map((res) => res.body.id));
    expect(ids.size).toBe(25);
  });

  it('imports JSON and XML formats and supports combined filtering across them', async () => {
    const jsonImport = await request(http)
      .post('/tickets/import')
      .attach('file', Buffer.from(fixture('sample_tickets.json')), 'sample_tickets.json');
    expect(jsonImport.status).toBe(200);
    expect(jsonImport.body.successful).toBe(20);

    const xmlImport = await request(http)
      .post('/tickets/import')
      .attach('file', Buffer.from(fixture('sample_tickets.xml')), 'sample_tickets.xml');
    expect(xmlImport.status).toBe(200);
    expect(xmlImport.body.successful).toBe(30);

    const all = await request(http).get('/tickets');
    expect(all.status).toBe(200);
    expect(all.body).toHaveLength(50);

    const filtered = await request(http).get(
      '/tickets?category=account_access&priority=urgent',
    );
    expect(filtered.status).toBe(200);
    expect(filtered.body.length).toBeGreaterThanOrEqual(1);
    for (const ticket of filtered.body) {
      expect(ticket.category).toBe('account_access');
      expect(ticket.priority).toBe('urgent');
    }
  });

  it('rejects malformed files and unknown formats with meaningful 400 errors', async () => {
    const malformed = await request(http)
      .post('/tickets/import')
      .attach('file', Buffer.from(fixture('malformed.csv')), 'malformed.csv');
    expect(malformed.status).toBe(400);
    expect(typeof malformed.body.message).toBe('string');
    expect(malformed.body.message.length).toBeGreaterThan(0);

    const unknownFormat = await request(http)
      .post('/tickets/import')
      .attach('file', Buffer.from('some plain text content'), {
        filename: 'data.txt',
        contentType: 'text/plain',
      });
    expect(unknownFormat.status).toBe(400);

    const noFile = await request(http).post('/tickets/import');
    expect(noFile.status).toBe(400);
    expect(noFile.body.message).toContain('file');
  });
});
