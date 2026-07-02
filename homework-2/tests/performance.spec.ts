import { INestApplication } from '@nestjs/common';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import * as request from 'supertest';
import { ClassificationService } from '../src/classification/classification.service';
import { ImportService } from '../src/import/import.service';
import { createApp } from '../src/main';
import { TicketsService } from '../src/tickets/tickets.service';

const fixture = (name: string) => readFileSync(join(__dirname, 'fixtures', name), 'utf-8');

const validPayload = (overrides: Record<string, unknown> = {}) => ({
  customer_id: 'CUST-001',
  customer_email: 'alice@example.com',
  customer_name: 'Alice Nguyen',
  subject: 'Cannot access my dashboard',
  description: 'I have tried logging in five times and keep getting an error message.',
  metadata: { source: 'web_form', browser: 'Chrome', device_type: 'desktop' },
  ...overrides,
});

// Generous thresholds — these guard against gross regressions (e.g. an
// accidental O(n^2) scan), not micro-benchmark precision on shared CI hardware.
describe('Performance benchmarks (Task 5: test_performance)', () => {
  it('creates 100 tickets in under 2 seconds', () => {
    const service = new TicketsService(new ClassificationService());
    const start = Date.now();
    for (let i = 0; i < 100; i++) {
      service.create(validPayload({ customer_id: `CUST-${i}` }) as any);
    }
    expect(Date.now() - start).toBeLessThan(2000);
  });

  it('classifies 200 ticket texts in under 500ms', () => {
    const classifier = new ClassificationService();
    const start = Date.now();
    for (let i = 0; i < 200; i++) {
      classifier.classify(`t${i}`, 'Cannot log in', 'I forgot my password, this is critical and urgent.');
    }
    expect(Date.now() - start).toBeLessThan(500);
  });

  it('filters 500 in-memory tickets by combined category+priority in under 200ms', () => {
    const service = new TicketsService(new ClassificationService());
    for (let i = 0; i < 500; i++) {
      service.create(
        validPayload({
          customer_id: `CUST-${i}`,
          category: i % 2 === 0 ? 'billing_question' : 'technical_issue',
          priority: i % 3 === 0 ? 'urgent' : 'medium',
        }) as any,
      );
    }

    const start = Date.now();
    const results = service.findAll({ category: 'billing_question' as any, priority: 'urgent' as any });
    expect(Date.now() - start).toBeLessThan(200);
    expect(results.length).toBeGreaterThan(0);
  });

  it('imports the 50-row sample_tickets.csv in under 1 second', async () => {
    const ticketsService = new TicketsService(new ClassificationService());
    const importService = new ImportService(ticketsService);

    const start = Date.now();
    const summary = await importService.import(fixture('sample_tickets.csv'), 'csv');
    expect(Date.now() - start).toBeLessThan(1000);
    expect(summary.successful).toBe(50);
  });

  it('resolves 20 concurrent POST /tickets requests in under 3 seconds', async () => {
    const app: INestApplication = await createApp();
    await app.init();
    await app.listen(0);
    try {
      const start = Date.now();
      const responses = await Promise.all(
        Array.from({ length: 20 }, (_, i) =>
          request(app.getHttpServer())
            .post('/tickets')
            .send(validPayload({ customer_id: `CUST-PERF-${i}` })),
        ),
      );
      expect(Date.now() - start).toBeLessThan(3000);
      expect(responses.every((r) => r.status === 201)).toBe(true);
    } finally {
      await app.close();
    }
  });
});
