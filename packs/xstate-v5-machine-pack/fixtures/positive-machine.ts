// positive-machine.ts — lawful XState v5 fixture (construct gate positive case).
// Shape: setup() inline, static src, initial present, flat with a guarded transition.
import { setup } from 'xstate';

export const positiveMachine = setup({
  types: {} as { context: { count: number } },
  actions: {
    increment: ({ context }) => ({ context: { ...context, count: context.count + 1 } }),
  },
  guards: {
    canIncrement: ({ context }) => context.count < 3,
  },
}).createMachine({
  id: 'positive',
  initial: 'idle',
  context: { count: 0 },
  states: {
    idle: {
      on: {
        START: {
          target: 'running',
          guard: 'canIncrement',
        },
      },
    },
    running: {
      on: {
        TICK: { actions: 'increment' },
        STOP: { target: 'idle' },
      },
    },
  },
});
