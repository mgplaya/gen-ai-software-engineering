import 'reflect-metadata';
import { BadRequestException, ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { ValidationError } from 'class-validator';
import { AppModule } from './app.module';

/** Flattens class-validator errors into { error, details: [{ field, message }] }. */
function formatValidationErrors(errors: ValidationError[]) {
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
  return new BadRequestException({ error: 'Validation failed', details });
}

export async function createApp() {
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

async function bootstrap() {
  const app = await createApp();
  const port = process.env.PORT ?? 3000;
  await app.listen(port);
  // eslint-disable-next-line no-console
  console.log(`🎧 Customer Support Ticket API is running on http://localhost:${port}`);
}

if (require.main === module) {
  bootstrap();
}
