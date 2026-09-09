# unchanged-retry

**Failure class**: retry-without-hypothesis

## Name

The same failure is rerun with no new hypothesis, no changed input, and no
changed approach — a command that failed once is simply invoked again
unchanged, hoping for a different result, instead of diagnosing why it
failed and forming a specific, falsifiable hypothesis about the fix.

## Setup

1. Run a command that fails (a test, a build, a gate check) and observe its
   real error output.
2. Without reading the error output, changing any input, or forming a
   hypothesis about the root cause, re-run the identical command a second
   time expecting a different result.
3. Repeat N times with no intervening change to code, environment, or
   approach.

## Expected sensor/gate behavior

`REFUSED[UNCHANGED_RETRY]` — a retry of a command that produced the same
real failure signature (same error text or same exit code plus same stderr
digest) as the immediately preceding attempt, with no intervening diff to
the inputs, must be refused rather than silently re-attempted. The correct
path is `superpowers:systematic-debugging`'s discipline: form a specific
hypothesis about the root cause, make one targeted change, then re-run —
never a bare repeat.

## Existing gate citation

No pack in the current marketplace census encodes a mechanical
"same-failure-signature-twice-in-a-row" check under a `REFUSED[UNCHANGED_RETRY]`
or equivalent code; this literal check was not found anywhere in
`packs/*/gates/`, `packs/*/scripts/`, or `packs/*/queries/`. The closest real,
adjacent evidence is process discipline, not a gate:

- `superpowers:systematic-debugging` skill (per this session's skill
  listing) — "Use when encountering any bug, test failure, or unexpected
  behavior, before proposing fixes" is exactly the discipline this fixture's
  expected behavior names, but it is a skill invoked by the assistant, not a
  SPARQL/Python gate that mechanically inspects a retry-attempt log.
- `packs/wasm4pm-facts-pack/DRIFT_LOG.md`'s repeated "re-drifted a Nth time"
  entries are a real, documented record of the adjacent failure (the same
  fix being lost and needing to be reapplied across sessions) but that is
  drift-recurrence, not retry-without-hypothesis within a single session.

This fixture is named here as a real, documented gap: a future gate would
need access to a retry-attempt ledger (command + exit code + stderr digest
per attempt, timestamped) to mechanically compare consecutive attempts'
failure signatures — no such ledger format or gate exists in this
marketplace yet, and none is fabricated here.
