import { INestApplication } from '@nestjs/common';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import * as request from 'supertest';
import { createApp } from '../src/main';

const fixture = (name: string) => readFileSync(join(__dirname, 'fixtures', name));

const validPayload = (overrides: Record<string, unknown> = {}) => ({
  customer_id: 'CUST-001',
  customer_email: 'alice@example.com',
  customer_name: 'Alice Nguyen',
  subject: 'Cannot access my dashboard',
  description: 'I have tried logging in five times and keep getting an error message.',
  metadata: { source: 'web_form', browser: 'Chrome', device_type: 'desktop' },
  ...overrides,
});

describe('End-to-end workflows (Task 5: test_integration)', () => {
  let app: INestApplication;

  beforeEach(async () => {
    app = await createApp();
    await app.init();
    // Concurrent requests below need the server actually listening up front —
    // supertest's lazy listen-on-first-request races when calls start in parallel.
    await app.listen(0);
  });

  afterEach(async () => {
    await app.close();
  });

  it('runs the complete ticket lifecycle: create -> classify -> progress -> resolve -> delete', async () => {
    const server = app.getHttpServer();

    const created = await request(server)
      .post('/tickets')
      .send(validPayload({ subject: "Can't access account", description: 'This is critical, I cannot access my account at all.' }));
    expect(created.status).toBe(201);

    const classified = await request(server).post(`/tickets/${created.body.id}/auto-classify`);
    expect(classified.status).toBe(200);
    expect(classified.body.category).toBeDefined();

    const inProgress = await request(server).put(`/tickets/${created.body.id}`).send({ status: 'in_progress' });
    expect(inProgress.body.status).toBe('in_progress');

    const resolved = await request(server).put(`/tickets/${created.body.id}`).send({ status: 'resolved' });
    expect(resolved.body.status).toBe('resolved');
    expect(resolved.body.resolved_at).not.toBeNull();

    const deleted = await request(server).delete(`/tickets/${created.body.id}`);
    expect(deleted.status).toBe(204);

    const finalGet = await request(server).get(`/tickets/${created.body.id}`);
    expect(finalGet.status).toBe(404);
  });

  it('bulk-imports a CSV file with autoClassify=true and verifies every ticket was classified', async () => {
    const server = app.getHttpServer();

    const res = await request(server)
      .post('/tickets/import')
      .query({ autoClassify: 'true' })
      .attach('file', fixture('sample_tickets.csv'), 'sample_tickets.csv');

    expect(res.status).toBe(200);
    expect(res.body.successful).toBe(50);

    const list = await request(server).get('/tickets');
    expect(list.body).toHaveLength(50);
    expect(list.body.every((t: any) => t.classification !== null)).toBe(true);
  });

  it('handles 20+ concurrent ticket creations without id collisions or dropped requests', async () => {
    const server = app.getHttpServer();

    const requests = Array.from({ length: 25 }, (_, i) =>
      request(server).post('/tickets').send(validPayload({ customer_id: `CUST-CONC-${i}` })),
    );
    const responses = await Promise.all(requests);

    expect(responses.every((r) => r.status === 201)).toBe(true);
    const ids = new Set(responses.map((r) => r.body.id));
    expect(ids.size).toBe(25);

    const list = await request(server).get('/tickets');
    expect(list.body).toHaveLength(25);
  });

  it('filters combined by category and priority together', async () => {
    const server = app.getHttpServer();

    await request(server).post('/tickets').send(validPayload({ category: 'billing_question', priority: 'urgent' }));
    await request(server).post('/tickets').send(validPayload({ category: 'billing_question', priority: 'low' }));
    await request(server).post('/tickets').send(validPayload({ category: 'technical_issue', priority: 'urgent' }));

    const res = await request(server).get('/tickets').query({ category: 'billing_question', priority: 'urgent' });

    expect(res.status).toBe(200);
    expect(res.body).toHaveLength(1);
    expect(res.body[0].category).toBe('billing_question');
    expect(res.body[0].priority).toBe('urgent');
  });

  it('persists only the records that pass validation from a mixed-validity import', async () => {
    const server = app.getHttpServer();

    const res = await request(server)
      .post('/tickets/import')
      .attach('file', fixture('invalid_tickets.json'), 'invalid_tickets.json');

    expect(res.body).toEqual(
      expect.objectContaining({ total: 5, successful: 1, failed: 4 }),
    );

    const list = await request(server).get('/tickets');
    expect(list.body).toHaveLength(res.body.successful);
  });
});
