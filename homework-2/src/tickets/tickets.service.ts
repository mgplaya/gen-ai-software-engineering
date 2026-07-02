import { Injectable, NotFoundException } from '@nestjs/common';
import { randomUUID } from 'node:crypto';
import { ClassificationService } from '../classification/classification.service';
import { CreateTicketDto } from './dto/create-ticket.dto';
import { QueryTicketsDto } from './dto/query-tickets.dto';
import { UpdateTicketDto } from './dto/update-ticket.dto';
import { Ticket, TicketCategory, TicketPriority, TicketStatus } from './entities/ticket.entity';

@Injectable()
export class TicketsService {
  // In-memory storage — resets on every restart. No database required (per spec).
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
      metadata: {
        source: dto.metadata.source,
        browser: dto.metadata.browser ?? null,
        device_type: dto.metadata.device_type ?? null,
      },
      classification: null,
    };

    this.tickets.push(ticket);

    if (dto.autoClassify) {
      this.autoClassify(ticket.id);
    }

    return ticket;
  }

  findAll(filter: QueryTicketsDto = {}): Ticket[] {
    return this.tickets.filter((t) => {
      if (filter.category && t.category !== filter.category) return false;
      if (filter.priority && t.priority !== filter.priority) return false;
      if (filter.status && t.status !== filter.status) return false;
      if (filter.customer_id && t.customer_id !== filter.customer_id) return false;
      if (filter.assigned_to && t.assigned_to !== filter.assigned_to) return false;
      if (filter.tag && !t.tags.includes(filter.tag)) return false;
      return true;
    });
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

    if (dto.subject !== undefined) ticket.subject = dto.subject;
    if (dto.description !== undefined) ticket.description = dto.description;
    if (dto.category !== undefined) ticket.category = dto.category;
    if (dto.priority !== undefined) ticket.priority = dto.priority;
    if (dto.assigned_to !== undefined) ticket.assigned_to = dto.assigned_to;
    if (dto.tags !== undefined) ticket.tags = dto.tags;
    if (dto.metadata !== undefined) {
      ticket.metadata = {
        source: dto.metadata.source,
        browser: dto.metadata.browser ?? null,
        device_type: dto.metadata.device_type ?? null,
      };
    }

    if (dto.status !== undefined) {
      ticket.status = dto.status;
      // A ticket moving into "resolved" gets a resolved_at timestamp; moving
      // out of it (e.g. reopened) clears it.
      ticket.resolved_at = dto.status === TicketStatus.RESOLVED ? new Date().toISOString() : null;
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

  /** Runs the rule-based classifier against a ticket and stores the result (Task 2). */
  autoClassify(id: string): Ticket {
    const ticket = this.findOne(id);
    const result = this.classificationService.classify(id, ticket.subject, ticket.description);

    ticket.category = result.category;
    ticket.priority = result.priority;
    ticket.classification = result;
    ticket.updated_at = new Date().toISOString();

    return ticket;
  }
}
