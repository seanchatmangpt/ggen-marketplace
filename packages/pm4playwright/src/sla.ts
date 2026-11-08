import { Pm4Session } from './session.js';
import { SlaBreachError } from './errors.js';

export interface SlaOptions {
  maxSeconds: number;
}

export function assertSla(
  session: Pm4Session,
  startActivity: string,
  endActivity: string,
  options: SlaOptions
): void {
  const events = session.getEvents();

  const startIdx = events.findIndex((e) => e.activity === startActivity);
  if (startIdx === -1) {
    throw new Error(`assertSla: start activity "${startActivity}" was never emitted`);
  }

  const endIdx = events.findIndex((e, idx) => idx > startIdx && e.activity === endActivity);
  if (endIdx === -1) {
    throw new Error(
      `assertSla: end activity "${endActivity}" was never emitted after "${startActivity}"`
    );
  }

  const startEvent = events[startIdx];
  const endEvent = events[endIdx];

  const durationMs = endEvent.timestamp - startEvent.timestamp;
  const durationSec = durationMs / 1000.0;

  if (durationSec > options.maxSeconds) {
    throw new SlaBreachError({
      startActivity,
      endActivity,
      maxSeconds: options.maxSeconds,
      actualSeconds: durationSec,
    });
  }
}
