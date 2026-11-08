# pm4playwright

Playwright-native process-intelligence test library. Mirror of `pm4pytest` (Python), `pm4exunit` (Elixir), and `pm4vitest` (Vitest):
- Process-bound OCEL 2.0 object & event tracking
- Token-Based Replay (TBR) conformance verification
- Causal-pair temporal latency SLA assertions
- Native Playwright test fixture (`pm4Session`, `trackStep`)
- TAP v13 and JUnit XML test output generators
- **Zero external dependencies** (`@playwright/test` peer dependency only)

## Installation

```bash
npm install -D pm4playwright
```

## Usage in Playwright E2E Tests

```typescript
import { test, expect } from 'pm4playwright';
import { assertConformance, assertSla } from 'pm4playwright';

test('Order lifecycle conformance', async ({ page, pm4Session, trackStep }) => {
  pm4Session.registerObject('wo-01', 'WorkOrder', { priority: 'P1' });

  await trackStep('wo_ingested', async () => {
    await page.goto('/work-orders/add-work-order');
    // fill form ...
  }, { objectIds: ['wo-01'] });

  await trackStep('client_brand_resolved', async () => {
    // select client and brand ...
  }, { objectIds: ['wo-01'] });

  await trackStep('visit_dispatched', async () => {
    // dispatch technician ...
  }, { objectIds: ['wo-01'] });

  // Token-Based Replay Conformance Verification
  assertConformance(pm4Session, [
    ['wo_ingested', 'client_brand_resolved', 'visit_dispatched']
  ], { minFitness: 1.0 });

  // Temporal Latency SLA Verification (e.g. <= 10 seconds in E2E test)
  assertSla(pm4Session, 'wo_ingested', 'visit_dispatched', { maxSeconds: 10.0 });
});
```

## Conformance Verification Formula

Token-based replay calculates the standard Petri Net token fitness metric:

$$\text{fitness} = \frac{1}{2}\left(1 - \frac{\text{missing}}{\text{consumed}}\right) + \frac{1}{2}\left(1 - \frac{\text{remaining}}{\text{produced}}\right)$$
