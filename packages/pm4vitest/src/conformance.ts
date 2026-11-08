/**
 * pm4vitest.conformance — token-based replay (TBR) conformance over a
 * Petri-net/FSM valid-path set.
 *
 * Each valid path becomes a parallel branch in a block-structured Petri net
 * (shared source place → per-activity transitions → shared sink place). A
 * trace is replayed token-by-token with bounded backtracking; fitness follows
 * the standard TBR formula:
 *
 *   fitness = 0.5 * (1 - missing/consumed) + 0.5 * (1 - remaining/produced)
 */

import type { Pm4Session } from './session.js';
import { processAssertionError } from './errors.js';

export interface ConformanceOptions {
  minFitness?: number;
}

export interface TraceInput {
  activity: string;
  time?: Date;
}

export interface TbrResult {
  fitness: number;
  /** tokens that were required but absent */
  missing: number;
  /** tokens actually consumed (including missing-substituted firings) */
  consumed: number;
  /** tokens stranded outside the final marking */
  remaining: number;
  /** tokens produced during replay (initial marking + firings) */
  produced: number;
  /** activities from the best-matching valid path absent from the trace */
  missingTransitions: string[];
  /** place -> leftover token count */
  remainingTokens: Record<string, number>;
  /** the valid path the replay best matched (LCS) */
  bestPath: string[];
}

// ---------------------------------------------------------------------------
// Petri net construction from valid paths
// ---------------------------------------------------------------------------

interface NetTransition {
  name: string;
  label: string | null; // null = silent
  input: string;
  output: string;
}

interface Net {
  transitions: NetTransition[];
  initialMarking: Record<string, number>;
  finalPlace: string;
}

export function buildNet(validPaths: readonly string[][]): Net {
  const transitions: NetTransition[] = [];
  const start = '__start__';
  const finalPlace = '__end__';

  validPaths.forEach((path, k) => {
    let cur = start;
    path.forEach((activity, i) => {
      const outPlace = i === path.length - 1 ? finalPlace : `p${k}_${i}`;
      transitions.push({
        name: `t_${k}_${i}_${activity}`,
        label: activity,
        input: cur,
        output: outPlace,
      });
      cur = outPlace;
    });
  });

  return { transitions, initialMarking: { [start]: 1 }, finalPlace };
}

// ---------------------------------------------------------------------------
// Token-based replay (bounded backtracking)
// ---------------------------------------------------------------------------

function markingKey(marking: Record<string, number>): string {
  return Object.keys(marking)
    .filter((p) => marking[p]! > 0)
    .sort()
    .map((p) => `${p}:${marking[p]}`)
    .join(',');
}

/**
 * Bounded-backtracking TBR replay of `trace` against the net.
 * Chooses the firing sequence minimizing (missing, remaining) lexicographically.
 */
export function replay(net: Net, trace: readonly TraceInput[]): TbrResult {
  const initialTokens = Object.values(net.initialMarking).reduce((s, n) => s + n, 0);
  let expansions = 0;
  const BUDGET = 100000;
  const memo = new Map<string, { missing: number; remaining: number }>();

  interface Step {
    kind: 'fire' | 'cannot';
    t?: NetTransition;
    activity: string;
  }

  const candidates = (marking: Record<string, number>, activity: string): NetTransition[] =>
    net.transitions.filter((t) => t.label === activity && (marking[t.input] ?? 0) > 0);

  const applyFire = (marking: Record<string, number>, t: NetTransition): Record<string, number> => {
    const next = { ...marking };
    next[t.input] = next[t.input]! - 1;
    next[t.output] = (next[t.output] ?? 0) + 1;
    return next;
  };

  const remainingOf = (marking: Record<string, number>): { remaining: number; tokens: Record<string, number> } => {
    let remaining = 0;
    const tokens: Record<string, number> = {};
    for (const place of Object.keys(marking)) {
      const n = marking[place] ?? 0;
      if (place !== net.finalPlace && n > 0) {
        remaining += n;
        tokens[place] = n;
      }
    }
    return { remaining, tokens };
  };

  type DfsResult = { missing: number; remaining: number; path: Step[]; tokens: Record<string, number> };
  const OVERFLOW: DfsResult = { missing: Number.MAX_SAFE_INTEGER, remaining: 0, path: [], tokens: {} };

  function dfs(idx: number, marking: Record<string, number>, path: Step[]): DfsResult | null {
    if (expansions > BUDGET) return null;
    const key = `${idx}|${markingKey(marking)}`;
    const cached = memo.get(key);
    if (cached && cached.missing === 0 && cached.remaining === 0) return null; // perfect continuation known
    if (idx >= trace.length) {
      const { remaining, tokens } = remainingOf(marking);
      return { missing: 0, remaining, path, tokens };
    }
    expansions += 1;
    const results: DfsResult[] = [];
    for (const t of candidates(marking, trace[idx]!.activity)) {
      results.push(dfs(idx + 1, applyFire(marking, t), [...path, { kind: 'fire', t, activity: trace[idx]!.activity }]) ?? OVERFLOW);
    }
    // cannot-fire branch (missing token manufactured)
    results.push(dfs(idx + 1, marking, [...path, { kind: 'cannot', activity: trace[idx]!.activity }]) ?? OVERFLOW);
    if (results.length === 0) return null;
    let best = results[0]!;
    for (const r of results.slice(1)) {
      const better =
        r.missing < best.missing || (r.missing === best.missing && r.remaining < best.remaining);
      if (better) best = r;
      if (best.missing === 0 && best.remaining === 0) break;
      if (expansions > BUDGET) break;
    }
    if (best.missing !== Number.MAX_SAFE_INTEGER) {
      memo.set(key, { missing: best.missing, remaining: best.remaining });
    }
    return best;
  }

  const outcome = dfs(0, { ...net.initialMarking }, []);
  const steps = outcome?.path ?? trace.map((activity) => ({ kind: 'cannot' as const, activity }));
  let missing = 0;
  let consumed = 0;
  let produced = initialTokens;
  const firedActivityLabels = new Set<string>();
  let marking: Record<string, number> = { ...net.initialMarking };
  for (const step of steps) {
    if (step.kind === 'fire' && step.t) {
      const t = step.t;
      if ((marking[t.input] ?? 0) <= 0) missing += 1;
      else marking[t.input] = marking[t.input]! - 1;
      consumed += 1;
      marking[t.output] = (marking[t.output] ?? 0) + 1;
      produced += 1;
      firedActivityLabels.add(t.label ?? step.activity);
    } else {
      missing += 1;
      consumed += 1;
    }
  }
  const { remaining, tokens } = remainingOf(marking);

  return {
    fitness:
      0.5 * (1 - (consumed > 0 ? missing / consumed : 0)) +
      0.5 * (1 - (produced > 0 ? remaining / produced : 0)),
    missing,
    consumed,
    remaining,
    produced,
    missingTransitions: diagnoseMissingMandatory(net, trace, firedActivityLabels),
    remainingTokens: tokens,
    bestPath: diagnoseBestPath(net, trace),
  };
}

/** Activities of the best-matching valid path that the trace never fired. */
function diagnoseMissingMandatory(
  net: Net,
  trace: readonly TraceInput[],
  fired: Set<string>,
): string[] {
  const path = diagnoseBestPath(net, trace);
  return path.filter((a) => !fired.has(a));
}

/** Valid path with the longest common subsequence against the trace (ties: path order). */
function diagnoseBestPath(net: Net, trace: readonly TraceInput[]): string[] {
  const acts = trace.map((e) => e.activity);
  const paths = distinctPaths(net);
  let best: string[] = [];
  let bestLen = -1;
  for (const p of paths) {
    const l = lcsLength(acts, p);
    if (l > bestLen) {
      bestLen = l;
      best = p;
    }
  }
  return best;
}

function distinctPaths(net: Net): string[][] {
  const paths: string[][] = [];
  for (const t of net.transitions) {
    if (t.label === null) continue;
    const k = Number(t.name.split('_')[1]);
    if (!Number.isInteger(k)) continue;
    (paths[k] ??= []).push(t.label);
  }
  return paths;
}

function lcsLength(a: readonly string[], b: readonly string[]): number {
  const dp: number[][] = Array.from({ length: a.length + 1 }, () => new Array(b.length + 1).fill(0));
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      dp[i]![j] = a[i - 1] === b[j - 1] ? dp[i - 1]![j - 1]! + 1 : Math.max(dp[i - 1]![j]!, dp[i]![j - 1]!);
    }
  }
  return dp[a.length]![b.length]!;
}

// ---------------------------------------------------------------------------
// Assertions
// ---------------------------------------------------------------------------

function traceOf(sessionOrTrace: Pm4Session | readonly TraceInput[]): TraceInput[] {
  const isSession = (x: unknown): x is Pm4Session =>
    typeof x === 'object' && x !== null && 'emitEvent' in x && 'getTrace' in x;
  if (isSession(sessionOrTrace)) return sessionOrTrace.getTrace();
  return [...sessionOrTrace];
}

function formatDiagnostic(r: TbrResult, minFitness: number): string {
  const lines = [
    `Process conformance violated: fitness ${r.fitness.toFixed(4)} < required ${minFitness.toFixed(4)}`,
    `TBR counters: missing=${r.missing} consumed=${r.consumed} remaining=${r.remaining} produced=${r.produced}`,
    `best-matching valid path: ${r.bestPath.length ? r.bestPath.join(' -> ') : '(none)'}`,
  ];
  if (r.missingTransitions.length > 0) {
    lines.push(`missing mandatory transitions: ${r.missingTransitions.join(', ')}`);
  }
  const remEntries = Object.entries(r.remainingTokens);
  if (remEntries.length > 0) {
    lines.push(`remaining/unconsumed tokens: ${remEntries.map(([p, n]) => `${p} x${n}`).join(', ')}`);
  }
  return lines.join('\n');
}

export function assertConformance(
  sessionOrTrace: Pm4Session | readonly TraceInput[],
  validPaths: readonly string[][],
  options: ConformanceOptions = {},
): TbrResult {
  const minFitness = options.minFitness ?? 1.0;
  const net = buildNet(validPaths);
  const result = replay(net, traceOf(sessionOrTrace));
  if (result.fitness < minFitness) {
    throw processAssertionError(
      `Conformance failure (fitness ${result.fitness.toFixed(4)} < ${minFitness}).\n${formatDiagnostic(
        result,
        minFitness,
      )}`,
      result.fitness,
      minFitness,
    );
  }
  return result;
}

/**
 * Illegal-sequence verification: passes when the trace does NOT perfectly fit
 * the valid-path set; throws when it does conform.
 */
export function refuteConformance(
  sessionOrTrace: Pm4Session | readonly TraceInput[],
  validPaths: readonly string[][],
): TbrResult {
  const net = buildNet(validPaths);
  const result = replay(net, traceOf(sessionOrTrace));
  if (result.fitness >= 1.0) {
    throw processAssertionError(
      `Expected trace NOT to conform to the valid-path set, but it conforms perfectly (fitness ${result.fitness.toFixed(
        4,
      )}).\ntrace: ${traceOf(sessionOrTrace)
        .map((e) => e.activity)
        .join(' -> ')}`,
      result.fitness,
      '< 1.0',
    );
  }
  return result;
}
