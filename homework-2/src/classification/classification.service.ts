import { Injectable, Logger } from '@nestjs/common';
import {
  ClassificationResult,
  TicketCategory,
  TicketPriority,
} from '../tickets/entities/ticket.entity';
import { CATEGORY_KEYWORDS, PRIORITY_KEYWORDS } from './keywords';

export interface ClassificationDecision extends ClassificationResult {
  ticket_id: string;
}

function round2(value: number): number {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

interface KeywordMatcher {
  keyword: string;
  pattern: RegExp;
}

interface MatcherTable<T> {
  value: T;
  matchers: KeywordMatcher[];
}

/** Word-boundary patterns so 'bug' does not match inside 'debug'; compiled once at module load. */
function compileTable<T>(entries: { value: T; keywords: string[] }[]): MatcherTable<T>[] {
  return entries.map(({ value, keywords }) => ({
    value,
    matchers: keywords.map((keyword) => ({
      keyword,
      pattern: new RegExp(`\\b${escapeRegExp(keyword)}\\b`),
    })),
  }));
}

const CATEGORY_MATCHERS = compileTable(
  CATEGORY_KEYWORDS.map(({ category, keywords }) => ({ value: category, keywords })),
);
const PRIORITY_MATCHERS = compileTable(
  PRIORITY_KEYWORDS.map(({ priority, keywords }) => ({ value: priority, keywords })),
);

/** Tables are ordered by precedence: the first entry with at least one match wins. */
function firstMatch<T>(
  tables: MatcherTable<T>[],
  text: string,
): { value: T; matched: string[] } | undefined {
  for (const { value, matchers } of tables) {
    const matched = matchers.filter((m) => m.pattern.test(text)).map((m) => m.keyword);
    if (matched.length > 0) {
      return { value, matched };
    }
  }
  return undefined;
}

function describeMatch(
  label: string,
  match: { value: unknown; matched: string[] } | undefined,
  fallback: unknown,
): string {
  return match
    ? `Matched ${label} keyword(s) [${match.matched.join(', ')}] -> ${match.value}.`
    : `No ${label} keyword matched, defaulting to ${fallback}.`;
}

@Injectable()
export class ClassificationService {
  private readonly logger = new Logger(ClassificationService.name);
  private readonly decisions: ClassificationDecision[] = [];

  classify(ticketId: string, subject: string, description: string): ClassificationResult {
    const text = `${subject} ${description}`.toLowerCase();

    const categoryMatch = firstMatch(CATEGORY_MATCHERS, text);
    const priorityMatch = firstMatch(PRIORITY_MATCHERS, text);

    const category = categoryMatch?.value ?? TicketCategory.OTHER;
    const priority = priorityMatch?.value ?? TicketPriority.MEDIUM;

    const categoryConfidence = categoryMatch
      ? Math.min(0.95, 0.5 + 0.15 * categoryMatch.matched.length)
      : 0.3;
    const priorityConfidence = priorityMatch ? 0.9 : 0.5;
    const confidence = round2((categoryConfidence + priorityConfidence) / 2);

    const result: ClassificationResult = {
      category,
      priority,
      confidence,
      reasoning: `${describeMatch('category', categoryMatch, category)} ${describeMatch('priority', priorityMatch, priority)}`,
      keywords: [...(categoryMatch?.matched ?? []), ...(priorityMatch?.matched ?? [])],
      classified_at: new Date().toISOString(),
      manual_override: false,
    };

    this.decisions.push({ ticket_id: ticketId, ...result });
    this.logger.log(
      `Classified ticket ${ticketId}: category=${category} priority=${priority} confidence=${confidence}`,
    );

    return result;
  }

  getDecisions(): ClassificationDecision[] {
    return this.decisions;
  }
}
