/**
 * pm4vitest.sla — causal-pair SLA duration bounds.
 */

import type { Pm4Session } from './session.js';
import { processAssertionError } from './errors.js';

export interface SlaOptions {
  maxSeconds: number;
}

export interface SlaTraceInput {
  activity: string;
  time: Date;
}

export interface SlaResult {
  pair: string;
  start: Date;
  end: Date;
  durationSeconds: number;
}

function isSession(x: unknown): x is Pm4Session {
  return typeof x === 'object' && x !== null && 'emitEvent' in x && 'getTrace' in x;
}

export function assertSla(
  sessionOrTrace: Pm4Session | readonly SlaTraceInput[],
  startActivity: string,
  endActivity: string,
  options: SlaOptions,
): SlaResult {
  const trace = isSession(sessionOrTrace)
    ? sessionOrTrace.getTrace()
    : ([...sessionOrTrace] as Array<{ activity: string; time: Date }>);

  const startEv = trace.find((e) => e.activity === startActivity);
  const startIdx = startEv ? trace.indexOf(startEv) : -1;
  if (!startEv || startIdx === -1) {
    throw processAssertionError(
      `SLA causal pair broken: start activity "${startActivity}" not found in trace.`,
      trace.map((e) => e.activity),
      `trace containing "${startActivity}"`,
    );
  }

  const endEv = trace
    .slice(startIdx + 1)
    .find((e) => e.activity === endActivity);
  if (!endEv) {
    throw processAssertionError(
      `SLA causal pair broken: end activity "${endActivity}" never occurs after "${startActivity}".`,
      trace.map((e) => e.activity),
      `"${endActivity}" after "${startActivity}"`,
    );
  }

  const durationSeconds = (endEv.time.getTime() - startEv.time.getTime()) / 1000;
  if (durationSeconds > options.maxSeconds) {
    throw processAssertionError(
      `SLA breach: "${startActivity}" -> "${endActivity}" took ${durationSeconds.toFixed(
        3,
      )}s, exceeding max ${options.maxSeconds}s.`,
      durationSeconds,
      `<= ${options.maxSeconds}`,
    );
  }

  return { pair: `${startActivity} -> ${endActivity}`, start: startEv.time, end: endEv.time, durationSeconds };
}
