import { IsEnum, IsOptional, IsString } from 'class-validator';
import { TicketCategory, TicketPriority, TicketStatus } from '../entities/ticket.entity';

export class QueryTicketsDto {
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
  @IsEnum(TicketStatus, {
    message: 'status must be one of: new, in_progress, waiting_customer, resolved, closed',
  })
  status?: TicketStatus;

  @IsOptional()
  @IsString()
  customer_id?: string;

  @IsOptional()
  @IsString()
  assigned_to?: string;

  @IsOptional()
  @IsString()
  tag?: string;
}
