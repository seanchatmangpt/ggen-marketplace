import { test, expect } from '../src/fixture.js';
import { assertConformance, assertSla } from '../src/index.js';

test.describe('pm4playwright test fixture integration', () => {
  test('automatically tracks steps and verifies conformance in Playwright test', async ({
    pm4Session,
    trackStep,
  }) => {
    pm4Session.registerObject('wo-99', 'WorkOrder', { type: 'reactive' });

    await trackStep(
      'wo_ingested',
      async () => {
        // Simulated UI step
        await new Promise((resolve) => setTimeout(resolve, 50));
      },
      { objectIds: ['wo-99'] }
    );

    await trackStep(
      'client_brand_resolved',
      async () => {
        // Simulated brand cascade
        await new Promise((resolve) => setTimeout(resolve, 50));
      },
      { objectIds: ['wo-99'] }
    );

    await trackStep(
      'visit_dispatched',
      async () => {
        // Simulated technician assignment
        await new Promise((resolve) => setTimeout(resolve, 50));
      },
      { objectIds: ['wo-99'] }
    );

    // Verify events recorded in pm4Session
    expect(pm4Session.getTrace()).toEqual([
      'wo_ingested',
      'client_brand_resolved',
      'visit_dispatched',
    ]);

    // Token-Based Replay Conformance verification
    assertConformance(
      pm4Session,
      [['wo_ingested', 'client_brand_resolved', 'visit_dispatched']],
      { minFitness: 1.0 }
    );

    // Causal SLA check
    assertSla(pm4Session, 'wo_ingested', 'visit_dispatched', {
      maxSeconds: 5.0,
    });
  });
});
