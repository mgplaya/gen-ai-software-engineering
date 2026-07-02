import { IsEnum, IsOptional, IsString } from 'class-validator';
import { DeviceType, TicketSource } from '../entities/ticket.entity';

export class TicketMetadataDto {
  @IsEnum(TicketSource, {
    message: 'metadata.source must be one of: web_form, email, api, chat, phone',
  })
  source: TicketSource;

  @IsOptional()
  @IsString()
  browser?: string;

  @IsOptional()
  @IsEnum(DeviceType, {
    message: 'metadata.device_type must be one of: desktop, mobile, tablet',
  })
  device_type?: DeviceType;
}
