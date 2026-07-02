import { ClassificationService } from '../src/classification/classification.service';
import { TicketCategory, TicketPriority } from '../src/tickets/entities/ticket.entity';

describe('ClassificationService (Task 3: test_categorization)', () => {
  const service = new ClassificationService();

  it('classifies account_access from login/password keywords', () => {
    const result = service.classify('t1', 'Cannot log in', 'I forgot my password and cannot sign in.');
    expect(result.category).toBe(TicketCategory.ACCOUNT_ACCESS);
  });

  it('classifies technical_issue from crash/error keywords', () => {
    const result = service.classify('t2', 'App crashes', 'The app throws an error and crashes on launch.');
    expect(result.category).toBe(TicketCategory.TECHNICAL_ISSUE);
  });

  it('classifies billing_question from refund/invoice keywords', () => {
    const result = service.classify('t3', 'Refund request', 'Please refund my last invoice, I was charged twice.');
    expect(result.category).toBe(TicketCategory.BILLING_QUESTION);
  });

  it('classifies feature_request from suggestion/enhancement keywords', () => {
    const result = service.classify(
      't4',
      'Feature request for dark mode',
      'This is just a suggestion, an enhancement for a future release.',
    );
    expect(result.category).toBe(TicketCategory.FEATURE_REQUEST);
  });

  it('classifies bug_report when reproduction steps are present, ahead of the generic "bug" match', () => {
    const result = service.classify(
      't5',
      'Data export bug',
      'Steps to reproduce: open reports, click export, the file is corrupted every time.',
    );
    expect(result.category).toBe(TicketCategory.BUG_REPORT);
  });

  it('falls back to "other" when no category keyword matches', () => {
    const result = service.classify('t6', 'General inquiry', 'I have a general question about your company.');
    expect(result.category).toBe(TicketCategory.OTHER);
  });

  it('assigns urgent priority for "critical"/"production down"/"security" keywords', () => {
    const result = service.classify('t7', 'Production down', 'Our production environment is down, this is critical.');
    expect(result.priority).toBe(TicketPriority.URGENT);
  });

  it('assigns high priority for "important"/"blocking"/"asap" keywords', () => {
    const result = service.classify('t8', 'Blocking issue', 'This is important and blocking our release, please asap.');
    expect(result.priority).toBe(TicketPriority.HIGH);
  });

  it('assigns low priority for "minor"/"cosmetic"/"suggestion" keywords', () => {
    const result = service.classify('t9', 'Minor UI issue', 'This is a minor, cosmetic suggestion, nothing urgent.');
    expect(result.priority).toBe(TicketPriority.LOW);
  });

  it('increases confidence with more matched keywords and always returns reasoning + keywords', () => {
    const weak = service.classify('t10a', 'Login problem', 'I cannot log in to my account.');
    const strong = service.classify(
      't10b',
      'Login and 2FA problem',
      'I cannot log in, my password and 2fa authentication are both broken during sign in.',
    );

    expect(strong.confidence).toBeGreaterThanOrEqual(weak.confidence);
    expect(typeof weak.reasoning).toBe('string');
    expect(weak.reasoning.length).toBeGreaterThan(0);
    expect(Array.isArray(weak.keywords)).toBe(true);
    expect(weak.confidence).toBeGreaterThanOrEqual(0);
    expect(weak.confidence).toBeLessThanOrEqual(1);
  });
});
