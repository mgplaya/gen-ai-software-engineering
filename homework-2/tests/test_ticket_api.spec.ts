import { INestApplication } from '@nestjs/common';
import { randomUUID } from 'node:crypto';
import request from 'supertest';
import { createApp } from '../src/app.factory';
import { validPayload } from './helpers';

const UUID_RE = /^[0-9a-f-]{36}$/;
const ISO_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/;

describe('Ticket API', () => {
  let app: INestApplication;
  let http: any;

  beforeEach(async () => {
    app = await createApp();
    await app.init();
    http = app.getHttpServer();
  });

  afterEach(async () => {
    await app.close();
  });

  it('POST /tickets creates a ticket with UUID id, status new and sensible defaults', async () => {
    const res = await request(http).post('/tickets').send(validPayload());

    expect(res.status).toBe(201);
    expect(res.body.id).toMatch(UUID_RE);
    expect(res.body.status).toBe('new');
    expect(res.body.category).toBe('other');
    expect(res.body.priority).toBe('medium');
    expect(res.body.resolved_at).toBeNull();
    expect(res.body.assigned_to).toBeNull();
    expect(res.body.created_at).toMatch(ISO_RE);
    expect(res.body.updated_at).toMatch(ISO_RE);
    expect(Array.isArray(res.body.tags)).toBe(true);
    expect(res.body.metadata).toMatchObject({
      source: 'web_form',
      browser: 'Chrome',
      device_type: 'desktop',
    });
    expect(res.body.classification).toBeNull();
  });

  it('POST /tickets with an invalid email returns 400 with a validation detail for customer_email', async () => {
    const res = await request(http)
      .post('/tickets')
      .send(validPayload({ customer_email: 'not-an-email' }));

    expect(res.status).toBe(400);
    expect(res.body.error).toBe('Validation failed');
    expect(Array.isArray(res.body.details)).toBe(true);
    const fields = res.body.details.map((d: any) => d.field);
    expect(fields).toContain('customer_email');

    // nested metadata errors are reported with a dotted field path
    const nested = await request(http)
      .post('/tickets')
      .send(validPayload({ metadata: { source: 'carrier-pigeon' } }));
    expect(nested.status).toBe(400);
    const nestedFields = nested.body.details.map((d: any) => d.field);
    expect(nestedFields).toContain('metadata.source');
  });

  it('POST /tickets with an unknown extra property is rejected with 400', async () => {
    const res = await request(http)
      .post('/tickets')
      .send(validPayload({ hacker: 'x' }));

    expect(res.status).toBe(400);
  });

  it('POST /tickets with autoClassify:true classifies an account-access ticket as urgent', async () => {
    const res = await request(http)
      .post('/tickets')
      .send(
        validPayload({
          autoClassify: true,
          subject: "Can't access my account",
          description: 'I am locked out and cannot access the dashboard.',
        }),
      );

    expect(res.status).toBe(201);
    expect(res.body.classification).not.toBeNull();
    expect(res.body.classification).toMatchObject({
      category: 'account_access',
      priority: 'urgent',
      manual_override: false,
    });
    expect(res.body.category).toBe('account_access');
    expect(res.body.priority).toBe('urgent');
  });

  it('GET /tickets returns all created tickets', async () => {
    for (let i = 0; i < 3; i++) {
      await request(http)
        .post('/tickets')
        .send(validPayload({ customer_id: `CUST-00${i + 1}` }))
        .expect(201);
    }

    const res = await request(http).get('/tickets');

    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
    expect(res.body).toHaveLength(3);
  });

  it('GET /tickets?category=billing_question&priority=high returns only matching tickets', async () => {
    await request(http)
      .post('/tickets')
      .send(validPayload({ category: 'billing_question', priority: 'high' }))
      .expect(201);
    await request(http)
      .post('/tickets')
      .send(validPayload({ category: 'billing_question', priority: 'low' }))
      .expect(201);
    await request(http)
      .post('/tickets')
      .send(validPayload({ category: 'technical_issue', priority: 'high' }))
      .expect(201);

    const res = await request(http).get(
      '/tickets?category=billing_question&priority=high',
    );

    expect(res.status).toBe(200);
    expect(res.body).toHaveLength(1);
    for (const ticket of res.body) {
      expect(ticket.category).toBe('billing_question');
      expect(ticket.priority).toBe('high');
    }
  });

  it('GET /tickets filters by status and by assigned_to', async () => {
    await request(http)
      .post('/tickets')
      .send(validPayload({ assigned_to: 'agent.x' }))
      .expect(201);
    await request(http).post('/tickets').send(validPayload()).expect(201);

    const byStatus = await request(http).get('/tickets?status=new');
    expect(byStatus.status).toBe(200);
    expect(byStatus.body).toHaveLength(2);
    for (const ticket of byStatus.body) {
      expect(ticket.status).toBe('new');
    }

    const byAssignee = await request(http).get('/tickets?assigned_to=agent.x');
    expect(byAssignee.status).toBe(200);
    expect(byAssignee.body).toHaveLength(1);
    expect(byAssignee.body[0].assigned_to).toBe('agent.x');
  });

  it('GET /tickets/:id returns the ticket, and 404 for an unknown id', async () => {
    const created = await request(http)
      .post('/tickets')
      .send(validPayload())
      .expect(201);

    const found = await request(http).get(`/tickets/${created.body.id}`);
    expect(found.status).toBe(200);
    expect(found.body.id).toBe(created.body.id);

    const missing = await request(http).get(`/tickets/${randomUUID()}`);
    expect(missing.status).toBe(404);
  });

  it('PUT /tickets/:id updates fields, sets resolved_at on resolve, and rejects invalid enums', async () => {
    const created = await request(http)
      .post('/tickets')
      .send(validPayload())
      .expect(201);
    const id = created.body.id;

    const updated = await request(http)
      .put(`/tickets/${id}`)
      .send({ subject: 'Updated subject' });
    expect(updated.status).toBe(200);
    expect(updated.body.subject).toBe('Updated subject');

    const withMetadata = await request(http)
      .put(`/tickets/${id}`)
      .send({ metadata: { source: 'phone' } });
    expect(withMetadata.status).toBe(200);
    expect(withMetadata.body.metadata).toMatchObject({
      source: 'phone',
      browser: null,
      device_type: null,
    });

    const resolved = await request(http)
      .put(`/tickets/${id}`)
      .send({ status: 'resolved' });
    expect(resolved.status).toBe(200);
    expect(resolved.body.status).toBe('resolved');
    expect(resolved.body.resolved_at).not.toBeNull();
    expect(resolved.body.resolved_at).toMatch(ISO_RE);

    const invalid = await request(http)
      .put(`/tickets/${id}`)
      .send({ priority: 'bogus' });
    expect(invalid.status).toBe(400);
  });

  it('DELETE /tickets/:id removes the ticket and 404s for unknown ids', async () => {
    const created = await request(http)
      .post('/tickets')
      .send(validPayload())
      .expect(201);
    const id = created.body.id;

    await request(http).delete(`/tickets/${id}`).expect(204);
    await request(http).get(`/tickets/${id}`).expect(404);
    await request(http).delete(`/tickets/${randomUUID()}`).expect(404);
  });

  it('POST /tickets/:id/auto-classify returns a full classification result, 404 for unknown id', async () => {
    const created = await request(http)
      .post('/tickets')
      .send(validPayload())
      .expect(201);

    const res = await request(http).post(
      `/tickets/${created.body.id}/auto-classify`,
    );

    expect(res.status).toBe(200);
    expect(typeof res.body.confidence).toBe('number');
    expect(res.body.confidence).toBeGreaterThanOrEqual(0);
    expect(res.body.confidence).toBeLessThanOrEqual(1);
    expect(Array.isArray(res.body.keywords)).toBe(true);
    expect(typeof res.body.reasoning).toBe('string');
    expect(res.body.reasoning.length).toBeGreaterThan(0);
    expect(res.body.classified_at).toMatch(ISO_RE);

    // manually overriding the classified priority flags the decision as overridden
    const overridden = await request(http)
      .put(`/tickets/${created.body.id}`)
      .send({ priority: res.body.priority === 'low' ? 'high' : 'low' });
    expect(overridden.status).toBe(200);
    expect(overridden.body.classification.manual_override).toBe(true);

    await request(http)
      .post(`/tickets/${randomUUID()}/auto-classify`)
      .expect(404);
  });
});
