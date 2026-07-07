import 'reflect-metadata';
import { Logger } from '@nestjs/common';

// Keep test output clean: silence the Nest logger (classification decisions, import summaries).
Logger.overrideLogger(false);
