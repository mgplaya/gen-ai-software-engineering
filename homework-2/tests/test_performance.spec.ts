import { INestApplication } from '@nestjs/common';
import request from 'supertest';
import { createApp } from '../src/app.factory';
import { fixture, validPayload } from './helpers';

describe('Performance', () => {
  let app: INestApplication;
  let http: any;

  beforeAll(async () => {
    app = await createApp();
    // Listen on an ephemeral port: concurrent supertest requests against a
    // non-listening server race on listen() and fail with ECONNRESET.
    await app.listen(0);
    http = app.getHttpServer();
  });

  afterAll(async () => {
    await app.close();
  });

  it('creates 100 tickets sequentially in under 2000ms', async () => {
    const start = Date.now();
    for (let i = 0; i < 100; i++) {
      const res = await request(http)
        .post('/tickets')
        .send(validPayload({ customer_id: `PERF-${i}` }));
      expect(res.status).toBe(201);
    }
    const duration = Date.now() - start;

    expect(duration).toBeLessThan(2000);
  }, 30000);

  it('runs 200 sequential auto-classify calls in under 1000ms', async () => {
    const created = await request(http)
      .post('/tickets')
      .send(validPayload({ customer_id: 'PERF-CLASSIFY' }));
    expect(created.status).toBe(201);
    const id = created.body.id;

    const start = Date.now();
    for (let i = 0; i < 200; i++) {
      const res = await request(http).post(`/tickets/${id}/auto-classify`);
      expect(res.status).toBe(200);
    }
    const duration = Date.now() - start;

    expect(duration).toBeLessThan(1000);
  }, 30000);

  it('answers a filtered GET among ~300 stored tickets in under 500ms', async () => {
    // Top up the store created by the previous tests to roughly 300 tickets,
    // including some that match the filter under test.
    const extras = Array.from({ length: 200 }, (_, i) =>
      request(http)
        .post('/tickets')
        .send(
          validPayload({
            customer_id: `PERF-FILTER-${i}`,
            category: i % 2 === 0 ? 'technical_issue' : 'billing_question',
            priority: i % 2 === 0 ? 'medium' : 'low',
          }),
        ),
    );
    const created = await Promise.all(extras);
    for (const res of created) {
      expect(res.status).toBe(201);
    }

    const start = Date.now();
    const res = await request(http).get(
      '/tickets?category=technical_issue&priority=medium',
    );
    const duration = Date.now() - start;

    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
    expect(duration).toBeLessThan(500);
  }, 30000);

  it('imports the 50-row sample CSV in under 2000ms', async () => {
    const start = Date.now();
    const res = await request(http)
      .post('/tickets/import')
      .attach('file', Buffer.from(fixture('sample_tickets.csv')), 'sample_tickets.csv');
    const duration = Date.now() - start;

    expect(res.status).toBe(200);
    expect(res.body.successful).toBe(50);
    expect(duration).toBeLessThan(2000);
  }, 30000);

  it('handles 20 concurrent ticket creations in under 5000ms', async () => {
    const start = Date.now();
    const responses = await Promise.all(
      Array.from({ length: 20 }, (_, i) =>
        request(http)
          .post('/tickets')
          .send(validPayload({ customer_id: `PERF-CONC-${i}` })),
      ),
    );
    const duration = Date.now() - start;

    for (const res of responses) {
      expect(res.status).toBe(201);
    }
    expect(duration).toBeLessThan(5000);
  }, 30000);
});
