/**
 * pm4vitest.errors — the vitest AssertionError surface.
 *
 * vitest re-exports chai (its assertion substrate); chai.AssertionError is
 * the AssertionError class vitest's own `expect` throws. Constructing it
 * through `vitest`'s re-export keeps vitest the single peer dependency.
 */

import { chai } from 'vitest';

interface AssertionErrorCtor {
  new (
    message: string,
    props?: { actual?: unknown; expected?: unknown },
    ssf?: Function,
  ): Error;
}

const AssertionError = (chai as unknown as { AssertionError: AssertionErrorCtor }).AssertionError;

export function processAssertionError(
  message: string,
  actual?: unknown,
  expected?: unknown,
): Error {
  return new AssertionError(message, { actual, expected });
}
