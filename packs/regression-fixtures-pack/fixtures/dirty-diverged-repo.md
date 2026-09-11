# dirty-diverged-repo

**Failure class**: ground-truth-override

## Name

An agent (or an aggregate "census"-style narration built from prior agent
output) asserts that a repo/branch relationship is a clean fast-forward —
no conflicts, one side is a strict ancestor of the other — when direct,
unmediated git inspection of the real repo shows it is actually dirty
and/or diverged. This is a REAL fixture: it is not a synthesized scenario,
it is a documented claim actually made in this account's own standing-loop
history.

## The real incident being cited

`~/.claude/big-loop/tracker.md`, Cycle 12 (2026-08-21, "even cycle:
innovation-explorer -> Develop, with a real refusal"):

> Explore: 20 agents, 13 candidates. The report's own top recommendation was
> pushing clap-noun-verb's `fix/v26.8.8-feature-closure` branch (145 commits
> ahead, the real v26.9.1 release) to `origin/main`. **Independently
> re-verified this is real** (`git merge-base --is-ancestor origin/main HEAD`
> succeeds, clean fast-forward, no conflicts) but **did not execute it** —
> this loop's own standing constraint explicitly bars publishing/pushing to
> a real remote without your confirmation...

That cycle's own text is explicit that the "clean fast-forward, no
conflicts" verdict was independently re-verified via a real git command
(`git merge-base --is-ancestor`) rather than merely narrated forward from an
earlier agent's claim — i.e. this is the loop's own record of applying the
correct discipline (direct git sensor, not trusted narration) at the moment
a fast-forward claim was made. The same tracker's later cycles (13 through
31) carry `clap-noun-verb` forward in the "Remaining backlog" line for many
subsequent cycles without ever re-running that specific ancestor check
again — the fast-forward verdict from Cycle 12 is repeated by reference,
not re-verified, in every later cycle that mentions it. That repetition
pattern (a real verdict, cited forward across many cycles without
re-running the underlying command) is itself the exact hazard this fixture
names: a `git`-sourced fact is trustworthy only at the moment it was
actually run, and goes stale the instant the remote branch moves — nothing
in the tracker record establishes that `origin/main` and the feature branch
had not moved again by, say, Cycle 20.

## Setup (to reproduce the general failure shape)

1. Run a real ancestor/fast-forward check once (`git merge-base
   --is-ancestor <base> <head>`) and record its real, true-at-that-moment
   result.
2. Advance either ref (a concurrent push to the remote, a rebase, a new
   commit on either branch) without the recording agent noticing.
3. Have a later report (a "census", a status rollup, a subsequent loop
   cycle) restate the original verdict as still current, without re-running
   the git command against the branches' present tips.

## Expected sensor/gate behavior

A repo/branch relationship claim ("clean fast-forward", "no conflicts",
"diverged", "dirty") must be re-derived from a fresh, direct git command
(`git status --porcelain`, `git merge-base --is-ancestor`, `git rev-parse`)
at the moment it is asserted or relied upon for action — never carried
forward from a prior cycle's result without re-running the check. A direct
git sensor's output always overrides an agent's or an aggregated report's
narrated claim about repo state, per this account's own verification
discipline (`~/.claude/CLAUDE.md`: "Never report work as done without
running the real verification gate... pasting the actual output, not a
description of it"; `~/.claude/rules/no-overclaiming-conversational.md`:
"An accurate description of how something should work is not a substitute
for a checked artifact showing that it does").

## Existing gate citation

No SPARQL/Python gate anywhere in the current marketplace census
mechanically re-runs a git ancestor/dirty check and compares it against a
previously-recorded claim (this is a live-git-state check, not a static RDF
graph check, so it does not fit the SPARQL-gate shape the rest of this pack
uses). The closest real, adjacent evidence:

- `packs/tcps-release-pack/reference/tools/lifecycle.py`'s `git_information`
  function — a real, executable helper that runs `git rev-parse
  --show-toplevel`, `git rev-parse HEAD`, and `git status --porcelain`
  directly against the live repo and returns their real output (including a
  real `dirty` boolean) rather than accepting a narrated claim.
- `packs/epistemic-sensor-factory-pack/tools/consumer_court.py`'s `git()`
  helper and its `LINEAGE` refusal branch (also cited by `stale-plan.md` in
  this same fixture set) — the closest existing *ancestor-check* gate,
  though it checks a plan's declared base against `HEAD`, not a
  fast-forward claim between two branch tips re-verified over time.

This fixture is named here as a real, documented gap: a future gate would
need to re-run the ancestor check live at report-generation time (not
accept a cached prior result) and refuse any status line that restates an
old fast-forward/dirty verdict without a fresh timestamp/command attached —
that mechanism does not exist yet in this marketplace and is not fabricated
here.
