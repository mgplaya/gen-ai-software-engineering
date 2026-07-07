import { ClassificationService } from '../src/classification/classification.service';
import { TicketCategory, TicketPriority } from '../src/tickets/entities/ticket.entity';

describe('ClassificationService keyword engine', () => {
  let service: ClassificationService;

  beforeEach(() => {
    service = new ClassificationService();
  });

  it('classifies password / locked out text as account_access', () => {
    const result = service.classify(
      'T-1',
      'Trouble with my password',
      'I was locked out of my account after too many attempts.',
    );

    expect(result.category).toBe(TicketCategory.ACCOUNT_ACCESS);
  });

  it('classifies crash text as technical_issue', () => {
    const result = service.classify(
      'T-2',
      'App crash on startup',
      'The application crashes every time I open the settings screen.',
    );

    expect(result.category).toBe(TicketCategory.TECHNICAL_ISSUE);
  });

  it('classifies refund / invoice text as billing_question', () => {
    const result = service.classify(
      'T-3',
      'Refund still missing',
      'I was expecting a refund but the invoice still shows the full amount.',
    );

    expect(result.category).toBe(TicketCategory.BILLING_QUESTION);
  });

  it('classifies "would be nice" text as feature_request with default medium priority', () => {
    const result = service.classify(
      'T-4',
      'Dark theme',
      'It would be nice to have a dark theme across the whole app.',
    );

    expect(result.category).toBe(TicketCategory.FEATURE_REQUEST);
    expect(result.priority).toBe(TicketPriority.MEDIUM);
  });

  it('prefers bug_report over technical_issue when both categories match', () => {
    const result = service.classify(
      'T-5',
      'Found a bug in the counter',
      'Steps to reproduce: click the save button twice and watch the counter jump.',
    );

    expect(result.category).toBe(TicketCategory.BUG_REPORT);
  });

  it('falls back to other / medium with confidence 0.4 when no keyword matches', () => {
    const result = service.classify(
      'T-6',
      'Hello there',
      'Just wanted to say thanks to the team.',
    );

    expect(result.category).toBe(TicketCategory.OTHER);
    expect(result.priority).toBe(TicketPriority.MEDIUM);
    expect(result.confidence).toBe(0.4);
  });

  it('detects urgent and high priority keywords', () => {
    const urgent = service.classify(
      'T-7a',
      'Production down',
      'Everything went offline this morning and customers are affected.',
    );
    expect(urgent.priority).toBe(TicketPriority.URGENT);

    const high = service.classify(
      'T-7b',
      'Need a response',
      'Please look into this asap, the demo is tomorrow.',
    );
    expect(high.priority).toBe(TicketPriority.HIGH);
  });

  it('detects low priority keywords and defaults neutral text to medium', () => {
    const low = service.classify(
      'T-8a',
      'Small visual thing',
      'There is a cosmetic misalignment on the profile page.',
    );
    expect(low.priority).toBe(TicketPriority.LOW);

    const medium = service.classify(
      'T-8b',
      'Question about the roadmap',
      'When is the next release of the mobile client planned?',
    );
    expect(medium.priority).toBe(TicketPriority.MEDIUM);
  });

  it('keeps confidence within [0, 1] and raises it with more keyword matches', () => {
    const singleMatch = service.classify(
      'T-9a',
      'Password reset',
      'My password will not update after I change it.',
    );
    const multiMatch = service.classify(
      'T-9b',
      'Login help',
      'My password fails and 2fa codes are rejected during login.',
    );
    const noMatch = service.classify(
      'T-9c',
      'Hello there',
      'Just wanted to say thanks to the team.',
    );

    for (const result of [singleMatch, multiMatch, noMatch]) {
      expect(result.confidence).toBeGreaterThanOrEqual(0);
      expect(result.confidence).toBeLessThanOrEqual(1);
    }

    expect(multiMatch.confidence).toBeGreaterThan(singleMatch.confidence);
  });

  it('reports matched keywords, reasoning, manual_override and records every decision', () => {
    const first = service.classify(
      'TICKET-1',
      'Password problem',
      'I am locked out of the admin console and this is critical.',
    );

    expect(first.keywords).toEqual(expect.arrayContaining(['password', 'locked out', 'critical']));
    expect(typeof first.reasoning).toBe('string');
    expect(first.reasoning.length).toBeGreaterThan(0);
    expect(
      first.keywords.some((keyword) => first.reasoning.toLowerCase().includes(keyword.toLowerCase())),
    ).toBe(true);
    expect(first.manual_override).toBe(false);

    service.classify('TICKET-2', 'Refund still missing', 'The invoice shows a duplicate charge.');
    service.classify('TICKET-3', 'Hello there', 'Just wanted to say thanks to the team.');

    const decisions = service.getDecisions();
    expect(decisions).toHaveLength(3);
    expect(decisions.map((decision) => decision.ticket_id)).toEqual(
      expect.arrayContaining(['TICKET-1', 'TICKET-2', 'TICKET-3']),
    );
  });
});
