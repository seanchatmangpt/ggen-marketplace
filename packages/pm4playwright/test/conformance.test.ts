import { test, expect } from '@playwright/test';
import {
  Pm4Session,
  assertConformance,
  refuteConformance,
  assertSla,
  toTAP13,
  toJUnitXml,
  ConformanceError,
  SlaBreachError,
} from '../src/index.js';

test.describe('pm4playwright core conformance engine', () => {
  test('Pm4Session tracks objects and events and outputs OCEL 2.0 JSON', async () => {
    const s = new Pm4Session();
    s.registerObject('wo-1', 'WorkOrder', { priority: 'P1' });
    s.emitEvent('evt-1', 'wo_ingested', { objectIds: ['wo-1'] });
    s.emitEvent('evt-2', 'visit_dispatched', { objectIds: ['wo-1'] });

    expect(s.getTrace()).toEqual(['wo_ingested', 'visit_dispatched']);
    expect(s.getEvents().length).toBe(2);

    const json = JSON.parse(s.toOcel2Json());
    expect(json.objects['wo-1'].type).toBe('WorkOrder');
    expect(json.events.length).toBe(2);
  });

  test('assertConformance verifies 1.0 fitness on valid trace', async () => {
    const trace = ['wo_ingested', 'client_brand_resolved', 'visit_dispatched'];
    const validPaths = [
      ['wo_ingested', 'client_brand_resolved', 'visit_dispatched'],
      ['wo_ingested', 'cancelled'],
    ];

    expect(() => assertConformance(trace, validPaths)).not.toThrow();
  });

  test('assertConformance detects missing/remaining tokens on broken sequence', async () => {
    const brokenTrace = ['wo_ingested', 'visit_dispatched']; // skipped client_brand_resolved
    const validPaths = [
      ['wo_ingested', 'client_brand_resolved', 'visit_dispatched'],
    ];

    expect(() => assertConformance(brokenTrace, validPaths, { minFitness: 1.0 })).toThrow(
      ConformanceError
    );
  });

  test('refuteConformance admits invalid sequences and refutes conforming sequences', async () => {
    const illegalTrace = ['visit_dispatched', 'wo_ingested'];
    const validPaths = [
      ['wo_ingested', 'client_brand_resolved', 'visit_dispatched'],
    ];

    expect(() => refuteConformance(illegalTrace, validPaths)).not.toThrow();

    const conformingTrace = ['wo_ingested', 'client_brand_resolved', 'visit_dispatched'];
    expect(() => refuteConformance(conformingTrace, validPaths)).toThrow();
  });

  test('assertSla verifies temporal latency bounds', async () => {
    const s = new Pm4Session();
    const t0 = 1000000;
    s.emitEvent('e1', 'wo_ingested', { timestamp: t0 });
    s.emitEvent('e2', 'visit_dispatched', { timestamp: t0 + 2500 }); // +2.5s

    expect(() =>
      assertSla(s, 'wo_ingested', 'visit_dispatched', { maxSeconds: 5.0 })
    ).not.toThrow();

    expect(() =>
      assertSla(s, 'wo_ingested', 'visit_dispatched', { maxSeconds: 1.0 })
    ).toThrow(SlaBreachError);
  });

  test('Reporters generate valid TAP v13 and JUnit XML', async () => {
    const outcomes = [
      { name: 'test_conformance_happy', ok: true, durationMs: 120 },
      { name: 'test_conformance_negative', ok: false, durationMs: 45, diagnostic: 'fitness: 0.6667' },
    ];

    const tap = toTAP13(outcomes);
    expect(tap).toContain('TAP version 13');
    expect(tap).toContain('ok 1 - test_conformance_happy');
    expect(tap).toContain('not ok 2 - test_conformance_negative');

    const xml = toJUnitXml(outcomes, 'E2E_Conformance');
    expect(xml).toContain('<testsuites name="E2E_Conformance" tests="2" failures="1"');
    expect(xml).toContain('<testcase name="test_conformance_happy"');
  });
});
