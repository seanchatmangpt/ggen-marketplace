import { test as base } from '@playwright/test';
import { Pm4Session } from './session.js';

export interface Pm4Fixtures {
  pm4Session: Pm4Session;
  trackStep: <T>(
    activity: string,
    fn: () => Promise<T>,
    opts?: { objectIds?: string[]; attributes?: Record<string, unknown> }
  ) => Promise<T>;
}

export const test = base.extend<Pm4Fixtures>({
  pm4Session: async ({}, use) => {
    const session = new Pm4Session();
    await use(session);
  },
  trackStep: async ({ pm4Session }, use) => {
    const tracker = async <T>(
      activity: string,
      fn: () => Promise<T>,
      opts?: { objectIds?: string[]; attributes?: Record<string, unknown> }
    ): Promise<T> => {
      const startTime = Date.now();
      try {
        const res = await base.step(activity, fn);
        const endTime = Date.now();
        pm4Session.emitEvent(`evt_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`, activity, {
          timestamp: startTime,
          objectIds: opts?.objectIds ?? [],
          attributes: {
            ...opts?.attributes,
            durationMs: endTime - startTime,
          },
        });
        return res;
      } catch (err) {
        pm4Session.emitEvent(`evt_${Date.now()}_err`, `${activity}:failed`, {
          timestamp: startTime,
          objectIds: opts?.objectIds ?? [],
          attributes: { error: String(err) },
        });
        throw err;
      }
    };
    await use(tracker);
  },
});

export { expect } from '@playwright/test';
