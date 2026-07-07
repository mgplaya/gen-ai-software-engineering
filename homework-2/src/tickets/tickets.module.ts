import { Module } from '@nestjs/common';
import { ClassificationModule } from '../classification/classification.module';
import { ImportService } from '../import/import.service';
import { TicketsController } from './tickets.controller';
import { TicketsService } from './tickets.service';

@Module({
  imports: [ClassificationModule],
  controllers: [TicketsController],
  providers: [TicketsService, ImportService],
})
export class TicketsModule {}
