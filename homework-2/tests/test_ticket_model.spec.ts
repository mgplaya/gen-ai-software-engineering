import { plainToInstance } from 'class-transformer';
import { validate, ValidationError } from 'class-validator';
import { CreateTicketDto } from '../src/tickets/dto/create-ticket.dto';
import { validPayload } from './helpers';

/** Transforms a plain payload into the DTO and validates it like the app's global pipe. */
async function validatePayload(payload: Record<string, unknown>): Promise<ValidationError[]> {
  const dto = plainToInstance(CreateTicketDto, payload);
  return validate(dto, { whitelist: true, forbidNonWhitelisted: true });
}

/** Top-level properties that produced validation errors. */
function errorProperties(errors: ValidationError[]): string[] {
  return errors.map((error) => error.property);
}

/** Child (nested) properties with errors under the given top-level property. */
function nestedErrorProperties(errors: ValidationError[], parent: string): string[] {
  const parentError = errors.find((error) => error.property === parent);
  return (parentError?.children ?? []).map((child) => child.property);
}

describe('CreateTicketDto validation', () => {
  it('accepts a fully valid payload with no validation errors', async () => {
    const errors = await validatePayload(validPayload());

    expect(errors).toEqual([]);
  });

  it('rejects a malformed customer_email', async () => {
    const errors = await validatePayload(validPayload({ customer_email: 'not-an-email' }));

    expect(errorProperties(errors)).toContain('customer_email');
  });

  it('enforces subject length bounds of 1 to 200 characters', async () => {
    const emptyErrors = await validatePayload(validPayload({ subject: '' }));
    expect(errorProperties(emptyErrors)).toContain('subject');

    const tooLongErrors = await validatePayload(validPayload({ subject: 'x'.repeat(201) }));
    expect(errorProperties(tooLongErrors)).toContain('subject');

    const maxLengthErrors = await validatePayload(validPayload({ subject: 'x'.repeat(200) }));
    expect(errorProperties(maxLengthErrors)).not.toContain('subject');
  });

  it('enforces description length bounds of 10 to 2000 characters', async () => {
    const tooShortErrors = await validatePayload(validPayload({ description: 'x'.repeat(9) }));
    expect(errorProperties(tooShortErrors)).toContain('description');

    const tooLongErrors = await validatePayload(validPayload({ description: 'x'.repeat(2001) }));
    expect(errorProperties(tooLongErrors)).toContain('description');

    const minLengthErrors = await validatePayload(validPayload({ description: 'x'.repeat(10) }));
    expect(errorProperties(minLengthErrors)).not.toContain('description');
  });

  it('rejects a category outside the TicketCategory enum', async () => {
    const errors = await validatePayload(validPayload({ category: 'invalid_category' }));

    expect(errorProperties(errors)).toContain('category');
  });

  it('rejects a priority outside the TicketPriority enum', async () => {
    const errors = await validatePayload(validPayload({ priority: 'super-urgent' }));

    expect(errorProperties(errors)).toContain('priority');
  });

  it('requires metadata and validates the nested source enum', async () => {
    const payloadWithoutMetadata = validPayload() as Record<string, unknown>;
    delete payloadWithoutMetadata.metadata;
    const missingErrors = await validatePayload(payloadWithoutMetadata);
    expect(errorProperties(missingErrors)).toContain('metadata');

    const badSourceErrors = await validatePayload(
      validPayload({ metadata: { source: 'carrier-pigeon' } }),
    );
    expect(nestedErrorProperties(badSourceErrors, 'metadata')).toContain('source');
  });

  it('rejects an invalid metadata.device_type and non-string tags elements', async () => {
    const badDeviceErrors = await validatePayload(
      validPayload({ metadata: { source: 'web_form', device_type: 'smartwatch' } }),
    );
    expect(nestedErrorProperties(badDeviceErrors, 'metadata')).toContain('device_type');

    const badTagsErrors = await validatePayload(validPayload({ tags: [123] }));
    expect(errorProperties(badTagsErrors)).toContain('tags');
  });

  it('accepts a payload with all optional fields omitted', async () => {
    const payload = validPayload({ metadata: { source: 'web_form' } }) as Record<string, unknown>;
    delete payload.tags;

    const errors = await validatePayload(payload);

    expect(errors).toEqual([]);
  });
});
