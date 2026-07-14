import { Injectable, NotFoundException } from '@nestjs/common';
import { randomUUID } from 'node:crypto';
import { ClassificationService } from '../classification/classification.service';
import { CreateTicketDto } from './dto/create-ticket.dto';
import { QueryTicketsDto } from './dto/query-tickets.dto';
import { UpdateTicketDto } from './dto/update-ticket.dto';
import {
  Ticket,
  TicketCategory,
  TicketMetadata,
  TicketPriority,
  TicketStatus,
} from './entities/ticket.entity';
import { TicketMetadataDto } from './dto/ticket-metadata.dto';

function toMetadata(dto: TicketMetadataDto): TicketMetadata {
  return {
    source: dto.source,
    browser: dto.browser ?? null,
    device_type: dto.device_type ?? null,
  };
}

@Injectable()
export class TicketsService {
  private readonly tickets: Ticket[] = [];

  constructor(private readonly classificationService: ClassificationService) {}

  create(dto: CreateTicketDto): Ticket {
    const now = new Date().toISOString();
    const ticket: Ticket = {
      id: randomUUID(),
      customer_id: dto.customer_id,
      customer_email: dto.customer_email,
      customer_name: dto.customer_name,
      subject: dto.subject,
      description: dto.description,
      category: dto.category ?? TicketCategory.OTHER,
      priority: dto.priority ?? TicketPriority.MEDIUM,
      status: TicketStatus.NEW,
      created_at: now,
      updated_at: now,
      resolved_at: null,
      assigned_to: dto.assigned_to ?? null,
      tags: dto.tags ?? [],
      metadata: toMetadata(dto.metadata),
      classification: null,
    };
    this.tickets.push(ticket);

    if (dto.autoClassify) {
      this.autoClassify(ticket.id);
    }
    return ticket;
  }

  findAll(query: QueryTicketsDto): Ticket[] {
    return this.tickets.filter(
      (t) =>
        (!query.category || t.category === query.category) &&
        (!query.priority || t.priority === query.priority) &&
        (!query.status || t.status === query.status) &&
        (!query.customer_id || t.customer_id === query.customer_id) &&
        (!query.assigned_to || t.assigned_to === query.assigned_to) &&
        (!query.tag || t.tags.includes(query.tag)),
    );
  }

  findOne(id: string): Ticket {
    const ticket = this.tickets.find((t) => t.id === id);
    if (!ticket) {
      throw new NotFoundException(`Ticket with id "${id}" not found`);
    }
    return ticket;
  }

  update(id: string, dto: UpdateTicketDto): Ticket {
    const ticket = this.findOne(id);

    // A manual change of category/priority away from the classified values counts as an override.
    if (
      ticket.classification &&
      ((dto.category && dto.category !== ticket.classification.category) ||
        (dto.priority && dto.priority !== ticket.classification.priority))
    ) {
      ticket.classification.manual_override = true;
    }

    // `!= null` also skips explicit JSON nulls, which @IsOptional lets through.
    if (dto.subject != null) ticket.subject = dto.subject;
    if (dto.description != null) ticket.description = dto.description;
    if (dto.category != null) ticket.category = dto.category;
    if (dto.priority != null) ticket.priority = dto.priority;
    if (dto.assigned_to !== undefined) ticket.assigned_to = dto.assigned_to;
    if (dto.tags != null) ticket.tags = dto.tags;
    if (dto.metadata != null) ticket.metadata = toMetadata(dto.metadata);
    if (dto.status != null) {
      ticket.status = dto.status;
      if (dto.status === TicketStatus.RESOLVED) {
        ticket.resolved_at = new Date().toISOString();
      } else if (dto.status !== TicketStatus.CLOSED) {
        // Reopening clears the resolution time; closing a resolved ticket keeps it.
        ticket.resolved_at = null;
      }
    }

    ticket.updated_at = new Date().toISOString();
    return ticket;
  }

  remove(id: string): void {
    const index = this.tickets.findIndex((t) => t.id === id);
    if (index === -1) {
      throw new NotFoundException(`Ticket with id "${id}" not found`);
    }
    this.tickets.splice(index, 1);
  }

  autoClassify(id: string): Ticket {
    const ticket = this.findOne(id);
    const result = this.classificationService.classify(
      ticket.id,
      ticket.subject,
      ticket.description,
    );
    ticket.category = result.category;
    ticket.priority = result.priority;
    ticket.classification = result;
    ticket.updated_at = new Date().toISOString();
    return ticket;
  }
}
