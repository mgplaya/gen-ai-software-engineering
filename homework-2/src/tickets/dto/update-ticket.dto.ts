import { Type } from 'class-transformer';
import {
  IsArray,
  IsEnum,
  IsOptional,
  IsString,
  Length,
  ValidateNested,
} from 'class-validator';
import { TicketCategory, TicketPriority, TicketStatus } from '../entities/ticket.entity';
import { TicketMetadataDto } from './ticket-metadata.dto';

export class UpdateTicketDto {
  @IsOptional()
  @IsString()
  @Length(1, 200, { message: 'subject must be between 1 and 200 characters' })
  subject?: string;

  @IsOptional()
  @IsString()
  @Length(10, 2000, { message: 'description must be between 10 and 2000 characters' })
  description?: string;

  @IsOptional()
  @IsEnum(TicketCategory, {
    message: `category must be one of: ${Object.values(TicketCategory).join(', ')}`,
  })
  category?: TicketCategory;

  @IsOptional()
  @IsEnum(TicketPriority, {
    message: `priority must be one of: ${Object.values(TicketPriority).join(', ')}`,
  })
  priority?: TicketPriority;

  @IsOptional()
  @IsEnum(TicketStatus, {
    message: `status must be one of: ${Object.values(TicketStatus).join(', ')}`,
  })
  status?: TicketStatus;

  @IsOptional()
  @IsString()
  assigned_to?: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  tags?: string[];

  @IsOptional()
  @ValidateNested()
  @Type(() => TicketMetadataDto)
  metadata?: TicketMetadataDto;
}
