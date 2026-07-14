import { readFileSync } from 'node:fs';
import { join } from 'node:path';

/** Reads a fixture file from tests/fixtures as UTF-8 text. */
export function fixture(name: string): string {
  return readFileSync(join(__dirname, 'fixtures', name), 'utf-8');
}

/** A fully valid POST /tickets payload; override any field per test. */
export function validPayload(overrides: Record<string, unknown> = {}) {
  return {
    customer_id: 'CUST-001',
    customer_email: 'jane.doe@example.com',
    customer_name: 'Jane Doe',
    subject: 'Question about my subscription',
    description: 'I would like to understand how my subscription renewal works.',
    tags: ['subscription'],
    metadata: { source: 'web_form', browser: 'Chrome', device_type: 'desktop' },
    ...overrides,
  };
}
