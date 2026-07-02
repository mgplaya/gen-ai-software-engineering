import { TicketCategory, TicketPriority } from '../tickets/entities/ticket.entity';

/**
 * Category keywords, checked in this order. bug_report is listed before
 * technical_issue because "reproduce"/"steps to reproduce" language is a
 * more specific signal than a generic "bug"/"error" mention.
 */
export const CATEGORY_KEYWORDS: { category: TicketCategory; keywords: string[] }[] = [
  {
    category: TicketCategory.BUG_REPORT,
    keywords: [
      'steps to reproduce',
      'reproduce',
      'reproducible',
      'repro steps',
      'defect',
      'regression',
    ],
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
    keywords: [
      'payment',
      'invoice',
      'refund',
      'charge',
      'billing',
      'subscription',
      'credit card',
      'overcharged',
    ],
  },
  {
    category: TicketCategory.FEATURE_REQUEST,
    keywords: [
      'feature request',
      'enhancement',
      'suggestion',
      'would be nice',
      'please add',
      'could you add',
    ],
  },
  {
    category: TicketCategory.TECHNICAL_ISSUE,
    keywords: ['bug', 'error', 'crash', 'broken', 'not working', 'exception', 'freeze', 'glitch'],
  },
];

/**
 * Priority keywords, checked in this order — the first match wins, so more
 * severe priorities are listed first (an "urgent" phrase should never be
 * downgraded by a "low" one appearing elsewhere in the same text).
 */
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
