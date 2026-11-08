import { Pm4Session } from './session.js';
import { ConformanceError } from './errors.js';

export interface ConformanceOptions {
  minFitness?: number;
}

export interface ReplayStats {
  missing: number;
  consumed: number;
  remaining: number;
  produced: number;
  fitness: number;
  bestPathIndex: number;
  bestPath: readonly string[];
}

export function replayTokenBased(
  trace: readonly string[],
  validPaths: readonly (readonly string[])[]
): ReplayStats {
  if (validPaths.length === 0) {
    throw new Error('assertConformance: validPaths cannot be empty');
  }

  let bestFitness = -1;
  let bestStats: ReplayStats | null = null;

  for (let pIdx = 0; pIdx < validPaths.length; pIdx++) {
    const path = validPaths[pIdx];
    const stats = replaySinglePath(trace, path, pIdx);
    if (stats.fitness > bestFitness) {
      bestFitness = stats.fitness;
      bestStats = stats;
      if (bestFitness === 1.0) break;
    }
  }

  return bestStats!;
}

function replaySinglePath(
  trace: readonly string[],
  path: readonly string[],
  pIdx: number
): ReplayStats {
  let missing = 0;
  let consumed = 0;
  let produced = 1; // start place initial token
  let tokensInPlaces = 1;

  let pathIdx = 0;

  for (const activity of trace) {
    if (pathIdx < path.length && path[pathIdx] === activity) {
      // Normal sequential transition fire
      if (tokensInPlaces > 0) {
        tokensInPlaces--;
        consumed++;
      } else {
        missing++;
        consumed++;
      }
      tokensInPlaces++;
      produced++;
      pathIdx++;
    } else {
      const futureMatchIdx = path.indexOf(activity, pathIdx);
      if (futureMatchIdx !== -1) {
        // Skipped activities in the path between pathIdx and futureMatchIdx
        const skippedCount = futureMatchIdx - pathIdx;
        missing += skippedCount;
        consumed += skippedCount;
        produced += skippedCount;

        if (tokensInPlaces > 0) {
          tokensInPlaces--;
          consumed++;
        } else {
          missing++;
          consumed++;
        }
        tokensInPlaces++;
        produced++;
        pathIdx = futureMatchIdx + 1;
      } else {
        // Activity not in path or already passed
        missing++;
        consumed++;
      }
    }
  }

  // Final consumption to __end__ place
  if (pathIdx === path.length) {
    if (tokensInPlaces > 0) {
      tokensInPlaces--;
      consumed++;
    } else {
      missing++;
      consumed++;
    }
  } else {
    // Path was not completed
    const remainingInPath = path.length - pathIdx;
    missing += remainingInPath;
    consumed += remainingInPath;
    produced += remainingInPath;
    if (tokensInPlaces > 0) {
      tokensInPlaces--;
      consumed++;
    } else {
      missing++;
      consumed++;
    }
  }

  const remaining = tokensInPlaces;

  const f1 = consumed > 0 ? 1 - missing / consumed : 0;
  const f2 = produced > 0 ? 1 - remaining / produced : 0;
  const fitness = 0.5 * f1 + 0.5 * f2;

  return {
    missing,
    consumed,
    remaining,
    produced,
    fitness: Math.max(0, Math.min(1, fitness)),
    bestPathIndex: pIdx,
    bestPath: path,
  };
}

export function assertConformance(
  sessionOrTrace: Pm4Session | readonly string[],
  validPaths: readonly (readonly string[])[],
  options: ConformanceOptions = {}
): void {
  const minFitness = options.minFitness ?? 1.0;
  const trace = Array.isArray(sessionOrTrace)
    ? (sessionOrTrace as readonly string[])
    : (sessionOrTrace as Pm4Session).getTrace();

  const stats = replayTokenBased(trace, validPaths);

  if (stats.fitness < minFitness) {
    const yaml = [
      '---',
      `observed_trace: [${trace.map((s) => `"${s}"`).join(', ')}]`,
      `best_matching_path: [${stats.bestPath.map((s) => `"${s}"`).join(', ')}]`,
      `fitness: ${stats.fitness.toFixed(4)}`,
      `min_fitness: ${minFitness.toFixed(4)}`,
      `missing_tokens: ${stats.missing}`,
      `consumed_tokens: ${stats.consumed}`,
      `remaining_tokens: ${stats.remaining}`,
      `produced_tokens: ${stats.produced}`,
      '---',
    ].join('\n');

    throw new ConformanceError({
      message: `Conformance check failed: fitness ${stats.fitness.toFixed(4)} < minFitness ${minFitness.toFixed(4)}`,
      missing: stats.missing,
      consumed: stats.consumed,
      remaining: stats.remaining,
      produced: stats.produced,
      fitness: stats.fitness,
      trace,
      validPaths,
      diagnosticYaml: yaml,
    });
  }
}

export function refuteConformance(
  sessionOrTrace: Pm4Session | readonly string[],
  validPaths: readonly (readonly string[])[]
): void {
  const trace = Array.isArray(sessionOrTrace)
    ? (sessionOrTrace as readonly string[])
    : (sessionOrTrace as Pm4Session).getTrace();

  const stats = replayTokenBased(trace, validPaths);

  if (stats.fitness === 1.0) {
    throw new Error(
      `refuteConformance failed: trace conformed perfectly (fitness = 1.0) to validPaths: [${trace.join(', ')}]`
    );
  }
}
