import { BadRequestException, INestApplication, ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { ValidationError } from 'class-validator';
import { AppModule } from './app.module';

/** Flattens a class-validator error tree (incl. nested metadata errors) into {field, message} pairs. */
export function flattenValidationErrors(
  errors: ValidationError[],
): { field: string; message: string }[] {
  const details: { field: string; message: string }[] = [];

  const walk = (error: ValidationError, parentPath = '') => {
    const field = parentPath ? `${parentPath}.${error.property}` : error.property;
    for (const message of Object.values(error.constraints ?? {})) {
      details.push({ field, message });
    }
    for (const child of error.children ?? []) {
      walk(child, field);
    }
  };

  errors.forEach((e) => walk(e));
  return details;
}

/** Wraps the flattened errors into { "error": "Validation failed", "details": [...] }. */
export function formatValidationErrors(errors: ValidationError[]) {
  return new BadRequestException({
    error: 'Validation failed',
    details: flattenValidationErrors(errors),
  });
}

/** Creates the Nest application with the global validation pipe. Shared by main.ts and tests. */
export async function createApp(): Promise<INestApplication> {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      exceptionFactory: formatValidationErrors,
    }),
  );

  return app;
}
