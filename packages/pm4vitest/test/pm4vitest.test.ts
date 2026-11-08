import { describe, expect, it } from 'vitest';
import { chai } from 'vitest';
import {
  Pm4Session,
  assertConformance,
  assertSla,
  buildNet,
  refuteConformance,
  replay,
  toJUnitXml,
  toTAP13,
} from '../src/index.js';
import type { ProcessTestOutcome } from '../src/index.js';

const ORDER_PATH = ['order_placed', 'payment_received', 'item_shipped', 'order_delivered'];

function timed(path: string[]): Array<{ activity: string; time: Date }> {
  return path.map((a, i) => ({ activity: a, time: new Date(i * 1000) }));
}

describe('Pm4Session', () => {
  it('tracks events and objects, projecting an ordered trace', () => {
    const s = new Pm4Session();
    s.registerObject('o1', 'Order', { total: 42 })
      .emitEvent('e1', 'order_placed', { objectIds: ['o1'] })
      .emitEvent('e2', 'payment_received', { objectIds: ['o1'], attributes: { amount: 42 } });
    expect(s.events).toHaveLength(2);
    expect(s.objects).toHaveLength(1);
    expect(s.getTrace().map((e) => e.activity)).toEqual(['order_placed', 'payment_received']);
    expect(s.events[1]!.relationships).toEqual([{ objectId: 'o1', qualifier: 'related' }]);
  });

  it('accepts explicit timestamps for deterministic SLA tests', () => defaultStamp());

  function defaultStamp(): void {
    const s = new Pm4Session();
    const t0 = new Date('2026-01-01T00:00:00Z');
    s.emitEvent('e1', 'start', { timestamp: t0 }).emitEvent('e2', 'end', {
      timestamp: new Date(t0.getTime() + 5000),
    });
    const trace = s.getTrace();
    expect(trace[1]!.time.getTime() - trace[0]!.time.getTime()).toBe(5000);
  }
});

describe('fitness math', () => {
  const paths = [ORDER_PATH];

  it('perfect trace = 1.0', () => {
    const r = replay(buildNet(paths), timed(ORDER_PATH));
    expect(r.fitness).toBe(1.0);
    expect(r.missing).toBe(0);
    expect(r.remaining).toBe(0);
  });

  it('missing middle transition: exact formula value 0.5*(1-1/3) + 0.5*(1-1/3) = 2/3', () => {
    const trace = ORDER_PATH.filter((a) => a !== 'item_shipped');
    const r = replay(buildNet(paths), timed(trace));
    expect(r.missing).toBe(1);
    expect(r.consumed).toBe(3);
    expect(r.remaining).toBe(1);
    expect(r.produced).toBe(3);
    const expected = 0.5 * (1 - 1 / 3) + 0.5 * (1 - 1 / 3);
    expect(r.fitness).toBeCloseTo(expected, 12);
    expect(r.fitness).toBeLessThan(1);
  });

  it('remaining token only (trace stops one short): remaining=1, produced=4 (initial + 3)', () => {
    const trace = ORDER_PATH.slice(0, 3);
    const r = replay(buildNet(paths), timed(trace));
    expect(r.missing).toBe(0);
    expect(r.remaining).toBe(1);
    const expected = 0.5 * (1 - 0 / 3) + 0.5 * (1 - 1 / 4);
    expect(r.fitness).toBeCloseTo(expected, 12);
  });

  it('extra illegal activity counts as missing token', () => {
    const trace = [...ORDER_PATH.slice(0, 2), 'refund_issued', ...ORDER_PATH.slice(2)];
    const r = replay(buildNet(paths), timed(trace));
    expect(r.missing).toBe(1);
    expect(r.fitness).toBeLessThan(1);
  });
});

describe('conformance assertions', () => {
  const paths = [ORDER_PATH, ['order_placed', 'order_cancelled']];

  it('assertConformance passes on a valid path', () => {
    const s = new Pm4Session();
    s.emitEvent('e1', 'order_placed').emitEvent('e2', 'order_cancelled');
    expect(() => assertConformance(s, paths)).not.toThrow();
  });

  it('assertConformance throws AssertionError with diagnostic block naming missing/remaining', () => {
    const trace = ORDER_PATH.filter((a) => a !== 'payment_received');
    expect(() =>
      assertConformance(trace.map((a) => ({ activity: a })), paths),
    ).toThrowError(/missing mandatory transitions: payment_received/);
    expect(() =>
      assertConformance(trace.map((a) => ({ activity: a })), paths),
    ).toThrowError(/remaining\/unconsumed tokens/);
  });

  it('respects minFitness option', () => {
    const trace = ORDER_PATH.slice(0, 3); // fitness = 0.5*(1-0/3) + 0.5*(1-1/3) ~ 0.833
    expect(() =>
      assertConformance(timed(trace), [ORDER_PATH], { minFitness: 0.8 }),
    ).not.toThrow();
    expect(() =>
      assertConformance(timed(ORDER_PATH.slice(0, 1)), [ORDER_PATH], { minFitness: 0.9 }),
    ).toThrow();
  });

  it('refuteConformance passes on illegal sequence, throws on valid one', () => {
    expect(() =>
      refuteConformance([{ activity: 'order_cancelled' }, { activity: 'order_placed' }], paths),
    ).not.toThrow();
    expect(() =>
      refuteConformance([{ activity: 'order_placed' }, { activity: 'order_cancelled' }], paths),
    ).toThrow();
  });
});

describe('assertSla', () => {
  function session(): Pm4Session {
    const s = new Pm4Session();
    const t0 = new Date('2026-01-01T00:00:00Z');
    s.emitEvent('e1', 'submit', { timestamp: t0 }).emitEvent('e2', 'approve', {
      timestamp: new Date(t0.getTime() + 2000),
    });
    return s;
  }

  it('passes within bound', () => {
    expect(() => assertSla(session(), 'submit', 'approve', { maxSeconds: 5 })).not.toThrow();
  });

  it('throws on breach', () => {
    expect(() => assertSla(session(), 'submit', 'approve', { maxSeconds: 1 })).toThrow(chai.AssertionError);
  });

  it('throws when end activity absent', () => {
    expect(() => assertSla(session(), 'submit', 'never', { maxSeconds: 5 })).toThrow(chai.AssertionError);
  });
});

describe('reporters', () => {
  const outcomes: ProcessTestOutcome[] = [
    { name: 'passes', passed: true },
    { name: 'fails', passed: false, diagnostics: { message: 'SLA breach', fitness: 0.7 } },
    { name: 'skips', passed: false, skip: true, skipReason: 'not applicable' },
  ];

  it('TAP v13 shape with YAML diagnostics', () => {
    const tap = toTAP13(outcomes);
    expect(tap).toMatch(/^TAP version 13\n1\.\.3\n/);
    expect(tap).toContain('ok 1 - passes');
    expect(tap).toContain('not ok 2 - fails');
    expect(tap).toContain('# SKIP');
    expect(tap).toContain('  ---\n  message: SLA breach\n  fitness: 0.7\n  ...');
  });

  it('JUnit XML shape', () => {
    const xml = toJUnitXml(outcomes, 'pm4vitest-suite');
    expect(xml).toMatch(/^<\?xml version="1.0" encoding="utf-8"\?>\n<testsuites /);
    expect(xml).toContain('tests="3" failures="1" errors="0" skipped="1"');
    expect(xml).toContain('<failure message="SLA breach">');
    expect(xml).toContain('<skipped message="not applicable"/>');
    expect(xml.trimEnd().endsWith('</testsuites>')).toBe(true);
  });
});
