import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { createApp } from '../src/main';
import { TicketCategory, TicketPriority, TicketStatus } from '../src/tickets/entities/ticket.entity';

const validPayload = (overrides: Record<string, unknown> = {}) => ({
  customer_id: 'CUST-001',
  customer_email: 'alice@example.com',
  customer_name: 'Alice Nguyen',
  subject: 'Cannot access my dashboard',
  description: 'I have tried logging in five times and keep getting an error message.',
  metadata: { source: 'web_form', browser: 'Chrome', device_type: 'desktop' },
  ...overrides,
});

describe('Tickets API (Task 3: test_ticket_api)', () => {
  let app: INestApplication;

  beforeEach(async () => {
    app = await createApp();
    await app.init();
  });

  afterEach(async () => {
    await app.close();
  });

  it('POST /tickets creates a ticket and returns 201 with server-assigned fields', async () => {
    const res = await request(app.getHttpServer()).post('/tickets').send(validPayload());

    expect(res.status).toBe(201);
    expect(res.body.id).toBeDefined();
    expect(res.body.status).toBe(TicketStatus.NEW);
    expect(res.body.created_at).toBeDefined();
    expect(res.body.resolved_at).toBeNull();
  });

  it('POST /tickets returns 400 with field-level details for an invalid payload', async () => {
    const res = await request(app.getHttpServer())
      .post('/tickets')
      .send(validPayload({ customer_email: 'not-an-email' }));

    expect(res.status).toBe(400);
    expect(res.body.error).toBe('Validation failed');
    expect(res.body.details.some((d: any) => d.field === 'customer_email')).toBe(true);
  });

  it('GET /tickets returns all created tickets', async () => {
    await request(app.getHttpServer()).post('/tickets').send(validPayload());
    await request(app.getHttpServer()).post('/tickets').send(validPayload({ customer_id: 'CUST-002' }));

    const res = await request(app.getHttpServer()).get('/tickets');
    expect(res.status).toBe(200);
    expect(res.body).toHaveLength(2);
  });

  it('GET /tickets?category= filters by category', async () => {
    await request(app.getHttpServer())
      .post('/tickets')
      .send(validPayload({ category: TicketCategory.BILLING_QUESTION }));
    await request(app.getHttpServer())
      .post('/tickets')
      .send(validPayload({ category: TicketCategory.TECHNICAL_ISSUE }));

    const res = await request(app.getHttpServer()).get('/tickets').query({ category: 'billing_question' });
    expect(res.status).toBe(200);
    expect(res.body).toHaveLength(1);
    expect(res.body[0].category).toBe(TicketCategory.BILLING_QUESTION);
  });

  it('GET /tickets?priority= filters by priority', async () => {
    await request(app.getHttpServer()).post('/tickets').send(validPayload({ priority: TicketPriority.URGENT }));
    await request(app.getHttpServer()).post('/tickets').send(validPayload({ priority: TicketPriority.LOW }));

    const res = await request(app.getHttpServer()).get('/tickets').query({ priority: 'urgent' });
    expect(res.status).toBe(200);
    expect(res.body).toHaveLength(1);
    expect(res.body[0].priority).toBe(TicketPriority.URGENT);
  });

  it('GET /tickets?status= filters by status', async () => {
    const created = await request(app.getHttpServer()).post('/tickets').send(validPayload());
    await request(app.getHttpServer()).post('/tickets').send(validPayload({ customer_id: 'CUST-002' }));
    await request(app.getHttpServer())
      .put(`/tickets/${created.body.id}`)
      .send({ status: 'in_progress' });

    const res = await request(app.getHttpServer()).get('/tickets').query({ status: 'in_progress' });
    expect(res.status).toBe(200);
    expect(res.body).toHaveLength(1);
  });

  it('GET /tickets/:id returns the requested ticket', async () => {
    const created = await request(app.getHttpServer()).post('/tickets').send(validPayload());
    const res = await request(app.getHttpServer()).get(`/tickets/${created.body.id}`);

    expect(res.status).toBe(200);
    expect(res.body.id).toBe(created.body.id);
  });

  it('GET /tickets/:id returns 404 for an unknown id', async () => {
    const res = await request(app.getHttpServer()).get('/tickets/00000000-0000-0000-0000-000000000000');
    expect(res.status).toBe(404);
  });

  it('PUT /tickets/:id updates fields and bumps updated_at', async () => {
    const created = await request(app.getHttpServer()).post('/tickets').send(validPayload());
    const res = await request(app.getHttpServer())
      .put(`/tickets/${created.body.id}`)
      .send({ assigned_to: 'agent-42', priority: 'high' });

    expect(res.status).toBe(200);
    expect(res.body.assigned_to).toBe('agent-42');
    expect(res.body.priority).toBe('high');
    expect(new Date(res.body.updated_at).getTime()).toBeGreaterThanOrEqual(
      new Date(created.body.updated_at).getTime(),
    );
  });

  it('PUT /tickets/:id sets resolved_at when status moves to resolved', async () => {
    const created = await request(app.getHttpServer()).post('/tickets').send(validPayload());
    const res = await request(app.getHttpServer())
      .put(`/tickets/${created.body.id}`)
      .send({ status: 'resolved' });

    expect(res.status).toBe(200);
    expect(res.body.status).toBe('resolved');
    expect(res.body.resolved_at).not.toBeNull();
  });

  it('DELETE /tickets/:id removes the ticket', async () => {
    const created = await request(app.getHttpServer()).post('/tickets').send(validPayload());

    const del = await request(app.getHttpServer()).delete(`/tickets/${created.body.id}`);
    expect(del.status).toBe(204);

    const get = await request(app.getHttpServer()).get(`/tickets/${created.body.id}`);
    expect(get.status).toBe(404);
  });

  it('DELETE /tickets/:id returns 404 for an unknown id', async () => {
    const res = await request(app.getHttpServer()).delete('/tickets/00000000-0000-0000-0000-000000000000');
    expect(res.status).toBe(404);
  });

  it('POST /tickets flattens nested validation errors into dotted field paths', async () => {
    const res = await request(app.getHttpServer())
      .post('/tickets')
      .send(validPayload({ metadata: { source: 'carrier_pigeon' } }));

    expect(res.status).toBe(400);
    expect(res.body.details.some((d: any) => d.field === 'metadata.source')).toBe(true);
  });

  it('POST /tickets with autoClassify=true classifies the ticket immediately', async () => {
    const res = await request(app.getHttpServer())
      .post('/tickets')
      .send(
        validPayload({
          subject: "Can't access my account",
          description: 'This is critical, I cannot access my account at all after the reset.',
          autoClassify: true,
        }),
      );

    expect(res.status).toBe(201);
    expect(res.body.classification).not.toBeNull();
  });

  it('PUT /tickets/:id updates the nested metadata object', async () => {
    const created = await request(app.getHttpServer()).post('/tickets').send(validPayload());
    const res = await request(app.getHttpServer())
      .put(`/tickets/${created.body.id}`)
      .send({ metadata: { source: 'chat', device_type: 'mobile' } });

    expect(res.status).toBe(200);
    expect(res.body.metadata).toEqual({ source: 'chat', browser: null, device_type: 'mobile' });
  });

  it('POST /tickets/import requires a file upload', async () => {
    const res = await request(app.getHttpServer()).post('/tickets/import');
    expect(res.status).toBe(400);
  });

  it('POST /tickets/import falls back to the mimetype when the extension is unrecognized', async () => {
    const res = await request(app.getHttpServer())
      .post('/tickets/import')
      .attach('file', Buffer.from(JSON.stringify([validPayload()])), {
        filename: 'export.dat',
        contentType: 'application/json',
      });

    expect(res.status).toBe(200);
    expect(res.body.successful).toBe(1);
  });

  it('POST /tickets/import returns 400 when the format cannot be determined', async () => {
    const res = await request(app.getHttpServer())
      .post('/tickets/import')
      .attach('file', Buffer.from('irrelevant'), {
        filename: 'data.bin',
        contentType: 'application/octet-stream',
      });

    expect(res.status).toBe(400);
  });
});
