// A profile/name is not proof of the currently authenticated Official Account.
export const ACCOUNT_ID_EXPRESSION = `String(window.wx?.data?.user_name || '')`;
export function assertBackendAccount(expected: string | undefined, actual: unknown): void {
  if (!expected?.trim()) throw new Error('Expected backend original account ID required');
  if (typeof actual !== 'string' || !actual || actual !== expected) {
    throw new Error('Backend account mismatch or identity unavailable; no upload permitted');
  }
}
