// divergent-machine.ts — construct gate negative case (planted missing-initial defect).
// Same shape as positive-machine.ts, but the compound `running` state is missing
// its required `initial`; machine construction MUST throw the exact xstate error.
import { setup } from 'xstate';

export const divergentMachine = setup({
  types: {} as { context: { count: number } },
}).createMachine({
  id: 'divergent',
  initial: 'idle',
  context: { count: 0 },
  states: {
    idle: {
      on: {
        START: { target: 'running' },
      },
    },
    running: {
      // PLANTED DEFECT: compound state with child states but no `initial`.
      states: {
        step1: {},
        step2: {},
      },
      on: {
        STOP: { target: 'idle' },
      },
    },
  },
});
