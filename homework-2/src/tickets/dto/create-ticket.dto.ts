import { Type } from 'class-transformer';
import {
  IsArray,
  IsBoolean,
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
  @Length(1, 100, { message: 'customer_id must not be empty' })
  customer_id: string;

  @IsEmail({}, { message: 'customer_email must be a valid email address' })
  customer_email: string;

  @IsString()
  @Length(1, 100, { message: 'customer_name must not be empty' })
  customer_name: string;

  @IsString()
  @Length(1, 200, { message: 'subject must be between 1 and 200 characters' })
  subject: string;

  @IsString()
  @Length(10, 2000, { message: 'description must be between 10 and 2000 characters' })
  description: string;

  // Optional at creation time — a ticket can be classified later via
  // POST /tickets/:id/auto-classify, or immediately via the autoClassify flag below.
  @IsOptional()
  @IsEnum(TicketCategory, {
    message:
      'category must be one of: account_access, technical_issue, billing_question, feature_request, bug_report, other',
  })
  category?: TicketCategory;

  @IsOptional()
  @IsEnum(TicketPriority, {
    message: 'priority must be one of: urgent, high, medium, low',
  })
  priority?: TicketPriority;

  @IsOptional()
  @IsString()
  assigned_to?: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  tags?: string[];

  @ValidateNested()
  @Type(() => TicketMetadataDto)
  metadata: TicketMetadataDto;

  // When true, runs the rule-based classifier immediately after creation
  // instead of requiring a separate POST /tickets/:id/auto-classify call.
  @IsOptional()
  @IsBoolean()
  autoClassify?: boolean;
}
