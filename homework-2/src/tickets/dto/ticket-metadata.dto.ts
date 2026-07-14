import { IsEnum, IsOptional, IsString } from 'class-validator';
import { DeviceType, TicketSource } from '../entities/ticket.entity';

export class TicketMetadataDto {
  @IsEnum(TicketSource, {
    message: `source must be one of: ${Object.values(TicketSource).join(', ')}`,
  })
  source: TicketSource;

  @IsOptional()
  @IsString()
  browser?: string;

  @IsOptional()
  @IsEnum(DeviceType, {
    message: `device_type must be one of: ${Object.values(DeviceType).join(', ')}`,
  })
  device_type?: DeviceType;
}
