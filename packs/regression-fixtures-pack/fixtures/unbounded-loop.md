# unbounded-loop

**Failure class**: unbounded-directive

## Name

A standing loop/directive is authored with no machine-checkable exit
predicate — e.g. "keep improving this until it's good", "loop until done" —
so nothing can ever mechanically determine the loop has finished, and it
either runs forever or is stopped by an arbitrary, undocumented human call.

## Setup

1. Author a loop directive whose only stop condition is a subjective
   adjective ("until it's clean", "until it's solid") with no bound on
   iteration count, wall-clock time, or a checkable predicate over real
   state (a specific test passing, a specific file matching a specific
   digest, a specific gate count reaching zero).
2. Submit it for admission as a standing loop (cron job, `/loop` skill
   invocation, or a workflow's own internal retry).

## Expected sensor/gate behavior

Admission must be refused until the directive is restated with a real,
machine-checkable exit predicate (a bounded iteration count, a wall-clock
deadline, or — preferred — a concrete state predicate: "stop when `pytest`
exits 0 AND the gate count is 0"). The refusal must name what's missing
(no exit predicate), not just reject silently.

## Existing gate citation

No exact SPARQL/Python gate for "does this directive's exit condition parse
as a checkable predicate" was found anywhere in the current marketplace
census (`control-plane-invariants-pack` does not exist as a pack in this
tree, and no other pack's gates directory encodes this specific check as
of this session). The closest real, adjacent mechanisms are:

- `~/.claude/rules/dmedi-methodology.md`'s Implement-phase discipline
  ("a standing check that catches regression... rather than a one-time fix
  assumed to hold forever") — a process rule, not a machine gate.
- The `loop`/`schedule` skills' own cadence and 7-day auto-expiry mechanics
  (per this session's tool listing) bound a *recurring cron job's* lifetime
  automatically, but do not validate that the *directive text itself*
  carries a checkable exit predicate before admission.

This fixture is named here as a real, documented gap: a future gate (most
naturally as a `PLAN_TEXT_PARSE` style Python check analogous to
`enterprise-architecture-connection-pack/gates/010_connection_shape.py`'s
`_refuse(...)` pattern) would need to parse a submitted loop directive's
declared stop condition and refuse admission when it resolves to a bare
subjective adjective with no bound — that gate does not exist yet and is
not fabricated here.
