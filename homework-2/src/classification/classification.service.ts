import { Injectable, Logger } from '@nestjs/common';
import { ClassificationResult, TicketCategory, TicketPriority } from '../tickets/entities/ticket.entity';
import { CATEGORY_KEYWORDS, PRIORITY_KEYWORDS } from './keywords';

function round2(value: number): number {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

@Injectable()
export class ClassificationService {
  private readonly logger = new Logger(ClassificationService.name);

  /**
   * Deterministic, keyword-based classifier — no external AI call. Matches the
   * subject + description against the category/priority keyword tables and
   * picks the first table entry with at least one hit.
   */
  classify(ticketId: string, subject: string, description: string): ClassificationResult {
    const text = `${subject} ${description}`.toLowerCase();

    const categoryMatch = CATEGORY_KEYWORDS.map(({ category, keywords }) => ({
      category,
      matched: keywords.filter((keyword) => text.includes(keyword)),
    })).find((entry) => entry.matched.length > 0);

    const priorityMatch = PRIORITY_KEYWORDS.map(({ priority, keywords }) => ({
      priority,
      matched: keywords.filter((keyword) => text.includes(keyword)),
    })).find((entry) => entry.matched.length > 0);

    const category = categoryMatch?.category ?? TicketCategory.OTHER;
    const priority = priorityMatch?.priority ?? TicketPriority.MEDIUM;

    const categoryConfidence = categoryMatch
      ? Math.min(0.95, 0.5 + 0.15 * categoryMatch.matched.length)
      : 0.3;
    const priorityConfidence = priorityMatch ? 0.9 : 0.5;
    const confidence = round2((categoryConfidence + priorityConfidence) / 2);

    const keywords = [...(categoryMatch?.matched ?? []), ...(priorityMatch?.matched ?? [])];

    const reasoning = categoryMatch
      ? `Matched category keyword(s) [${categoryMatch.matched.join(', ')}] -> ${category}. ` +
        (priorityMatch
          ? `Matched priority keyword(s) [${priorityMatch.matched.join(', ')}] -> ${priority}.`
          : `No priority keyword matched, defaulting to ${priority}.`)
      : `No category keyword matched, defaulting to ${category}. ` +
        (priorityMatch
          ? `Matched priority keyword(s) [${priorityMatch.matched.join(', ')}] -> ${priority}.`
          : `No priority keyword matched, defaulting to ${priority}.`);

    const result: ClassificationResult = {
      category,
      priority,
      confidence,
      reasoning,
      keywords,
      classifiedAt: new Date().toISOString(),
    };

    this.logger.log(
      `Classified ticket ${ticketId}: category=${category} priority=${priority} confidence=${confidence}`,
    );

    return result;
  }
}
