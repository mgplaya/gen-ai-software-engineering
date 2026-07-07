import { Type } from 'class-transformer';
import {
  IsArray,
  IsBoolean,
  IsDefined,
  IsEmail,
  IsEnum,
  IsOptional,
  IsString,
  Length,
  ValidateNested,
} from 'class-validator';
import { TicketCategory, TicketPriority } from '../entities/ticket.entity';
import { TicketMetadataDto } from './ticket-metadata.dto';

export class CreateTicketDto {
  @IsString()
  @Length(1, 100, { message: 'customer_id must be between 1 and 100 characters' })
  customer_id: string;

  @IsEmail({}, { message: 'customer_email must be a valid email address' })
  customer_email: string;

  @IsString()
  @Length(1, 100, { message: 'customer_name must be between 1 and 100 characters' })
  customer_name: string;

  @IsString()
  @Length(1, 200, { message: 'subject must be between 1 and 200 characters' })
  subject: string;

  @IsString()
  @Length(10, 2000, { message: 'description must be between 10 and 2000 characters' })
  description: string;

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
  @IsString()
  assigned_to?: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  tags?: string[];

  @IsDefined({ message: 'metadata is required' })
  @ValidateNested()
  @Type(() => TicketMetadataDto)
  metadata: TicketMetadataDto;

  @IsOptional()
  @IsBoolean()
  autoClassify?: boolean;
}
