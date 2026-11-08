export class ConformanceError extends Error {
  readonly missing: number;
  readonly consumed: number;
  readonly remaining: number;
  readonly produced: number;
  readonly fitness: number;
  readonly trace: readonly string[];
  readonly validPaths: readonly (readonly string[])[];
  readonly diagnosticYaml: string;

  constructor(opts: {
    message: string;
    missing: number;
    consumed: number;
    remaining: number;
    produced: number;
    fitness: number;
    trace: readonly string[];
    validPaths: readonly (readonly string[])[];
    diagnosticYaml: string;
  }) {
    super(`${opts.message}\n${opts.diagnosticYaml}`);
    this.name = 'ConformanceError';
    this.missing = opts.missing;
    this.consumed = opts.consumed;
    this.remaining = opts.remaining;
    this.produced = opts.produced;
    this.fitness = opts.fitness;
    this.trace = opts.trace;
    this.validPaths = opts.validPaths;
    this.diagnosticYaml = opts.diagnosticYaml;

    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ConformanceError);
    }
  }
}

export class SlaBreachError extends Error {
  readonly startActivity: string;
  readonly endActivity: string;
  readonly maxSeconds: number;
  readonly actualSeconds: number;

  constructor(opts: {
    startActivity: string;
    endActivity: string;
    maxSeconds: number;
    actualSeconds: number;
  }) {
    super(
      `SLA breach between "${opts.startActivity}" and "${opts.endActivity}": ` +
        `expected <= ${opts.maxSeconds}s, took ${opts.actualSeconds.toFixed(3)}s`
    );
    this.name = 'SlaBreachError';
    this.startActivity = opts.startActivity;
    this.endActivity = opts.endActivity;
    this.maxSeconds = opts.maxSeconds;
    this.actualSeconds = opts.actualSeconds;

    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, SlaBreachError);
    }
  }
}
