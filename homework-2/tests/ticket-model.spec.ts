import { plainToInstance } from 'class-transformer';
import { validate } from 'class-validator';
import { CreateTicketDto } from '../src/tickets/dto/create-ticket.dto';
import { TicketSource } from '../src/tickets/entities/ticket.entity';

const VALID_PAYLOAD = {
  customer_id: 'CUST-001',
  customer_email: 'alice@example.com',
  customer_name: 'Alice Nguyen',
  subject: 'Cannot access my dashboard',
  description: 'I have tried logging in five times and keep getting an error message.',
  metadata: { source: TicketSource.WEB_FORM, browser: 'Chrome', device_type: 'desktop' },
};

async function validateDto(overrides: Record<string, unknown> = {}) {
  const dto = plainToInstance(CreateTicketDto, { ...VALID_PAYLOAD, ...overrides });
  return validate(dto);
}

describe('CreateTicketDto validation (Task 3: test_ticket_model)', () => {
  it('accepts a fully valid ticket payload', async () => {
    const errors = await validateDto();
    expect(errors).toHaveLength(0);
  });

  it('rejects an invalid customer_email format', async () => {
    const errors = await validateDto({ customer_email: 'not-an-email' });
    expect(errors.some((e) => e.property === 'customer_email')).toBe(true);
  });

  it('rejects an empty customer_name', async () => {
    const errors = await validateDto({ customer_name: '' });
    expect(errors.some((e) => e.property === 'customer_name')).toBe(true);
  });

  it('rejects a subject longer than 200 characters', async () => {
    const errors = await validateDto({ subject: 'x'.repeat(201) });
    expect(errors.some((e) => e.property === 'subject')).toBe(true);
  });

  it('rejects a description shorter than 10 characters', async () => {
    const errors = await validateDto({ description: 'too short' });
    expect(errors.some((e) => e.property === 'description')).toBe(true);
  });

  it('rejects a description longer than 2000 characters', async () => {
    const errors = await validateDto({ description: 'x'.repeat(2001) });
    expect(errors.some((e) => e.property === 'description')).toBe(true);
  });

  it('rejects an invalid category enum value', async () => {
    const errors = await validateDto({ category: 'not_a_category' });
    expect(errors.some((e) => e.property === 'category')).toBe(true);
  });

  it('rejects an invalid priority enum value', async () => {
    const errors = await validateDto({ priority: 'super-urgent' });
    expect(errors.some((e) => e.property === 'priority')).toBe(true);
  });

  it('rejects metadata with a missing/invalid source', async () => {
    const errors = await validateDto({ metadata: { source: 'carrier_pigeon' } });
    const metadataError = errors.find((e) => e.property === 'metadata');
    expect(metadataError).toBeDefined();
    expect(metadataError?.children?.some((c) => c.property === 'source')).toBe(true);
  });
});
