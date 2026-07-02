import 'reflect-metadata';
import { Logger } from '@nestjs/common';

// Keep test output focused on assertion failures instead of Nest's request/route logs.
Logger.overrideLogger(false);
