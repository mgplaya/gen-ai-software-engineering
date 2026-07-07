import { TicketCategory, TicketPriority } from '../tickets/entities/ticket.entity';

/**
 * Ordered tables: the first entry with at least one keyword match wins,
 * so more specific categories (bug_report) must precede broader ones (technical_issue).
 */
export const CATEGORY_KEYWORDS: { category: TicketCategory; keywords: string[] }[] = [
  {
    category: TicketCategory.BUG_REPORT,
    keywords: ['steps to reproduce', 'reproduce', 'reproducible', 'repro steps', 'defect', 'regression'],
  },
  {
    category: TicketCategory.ACCOUNT_ACCESS,
    keywords: [
      'login',
      'log in',
      'password',
      '2fa',
      'two-factor',
      'two factor',
      'authentication',
      'sign in',
      'locked out',
      'account access',
    ],
  },
  {
    category: TicketCategory.BILLING_QUESTION,
    keywords: ['payment', 'invoice', 'refund', 'charge', 'billing', 'subscription', 'credit card', 'overcharged'],
  },
  {
    category: TicketCategory.FEATURE_REQUEST,
    keywords: ['feature request', 'enhancement', 'suggestion', 'would be nice', 'please add', 'could you add'],
  },
  {
    category: TicketCategory.TECHNICAL_ISSUE,
    keywords: ['bug', 'error', 'crash', 'broken', 'not working', 'exception', 'freeze', 'glitch'],
  },
];

export const PRIORITY_KEYWORDS: { priority: TicketPriority; keywords: string[] }[] = [
  {
    priority: TicketPriority.URGENT,
    keywords: ["can't access", 'cannot access', 'critical', 'production down', 'security'],
  },
  {
    priority: TicketPriority.HIGH,
    keywords: ['important', 'blocking', 'asap'],
  },
  {
    priority: TicketPriority.LOW,
    keywords: ['minor', 'cosmetic', 'suggestion'],
  },
];
