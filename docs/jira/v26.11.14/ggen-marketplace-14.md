# ggen-marketplace-14

Standing: UNVERIFIED

## Problem

Known pre-existing failures are not registered anywhere in the marketplace docs: arcus
`gcp_emulator` fails with HCL_UNSUPPORTED, and arcus `sdlc` panics with a nil deref at
`sdlc_test.go:153` (observed this session). Registers in this repo (for example
`/Users/sac/ggen-marketplace/docs/jira/v26.11.5/stale-claims-register.md`) have no row for
them, so a later red run cannot be classed pre-existing vs session-introduced. The parity
matrix also lists arcus aws divergences KD-AW7, KD-AW8, KD-AW9 with no local register copy.

Title: register arcus HCL_UNSUPPORTED and sdlc nil-deref as known divergences.

## Acceptance

- `grep -n "HCL_UNSUPPORTED\|sdlc_test.go:153" /Users/sac/ggen-marketplace/docs/jira/v26.11.14/*.md`
  matches a register row with surface, divergence, evidence receipt, close condition.
- `grep -c "KD-AW7\|KD-AW8\|KD-AW9" <register file>` returns 3 or more.

## Falsifier

A register row cites a failure that no longer reproduces at the cited SHA, or the nil deref
location differs from `sdlc_test.go:153` when re-run.

## Owned files

- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/known-divergences-register.md (new)
- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-14.md

## Depends-on

ggen-marketplace-13 (receipt SHA format).

## Size

S

## References (path : LOC)

- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/known-divergences-register.md : NEW (0 lines, to
  be created; est. LOC: 50, basis: header + 5 rows (HCL_UNSUPPORTED, sdlc nil deref, KD-AW7/8/9) at
  ~8 lines)
- /Users/sac/ggen-marketplace/docs/jira/v26.11.5/stale-claims-register.md : 62 lines
- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-14.md : 38 lines (before this
  annotation)

## Result

Standing: PARTIAL (KD-AW7/8/9 rows are placeholders; matrix text not available locally; nothing executed)

- Created /Users/sac/ggen-marketplace/docs/jira/v26.11.14/known-divergences-register.md (~65 LOC).
- Acceptance: `grep -n "HCL_UNSUPPORTED\|sdlc_test.go:153" /Users/sac/ggen-marketplace/docs/jira/v26.11.14/*.md; grep -c "KD-AW7\|KD-AW8\|KD-AW9" /Users/sac/ggen-marketplace/docs/jira/v26.11.14/known-divergences-register.md`

## Repair

Standing: UNVERIFIED (supersedes any PARTIAL above; nothing executed).
- Register `/Users/sac/ggen-marketplace/docs/jira/v26.11.14/known-divergences-register.md`: KD-AW7/8/9
  filled from `/Users/sac/arcus/KNOWN_DIVERGENCES.md`; ARC rows carry rerun commands and the real
  sdlc path; SHA caveat stated.
- Rerun: `grep -c "^### KD-" <register>` (expect 5) and `grep -c "not held locally" <register>` (expect 0).
- Also corrected `/Users/sac/smalt/docs/azure-parity/AZ2.md` Standing to UNVERIFIED (smalt ticket not edited;
  AZ2 matrix cells remain UNVERIFIED pending a run).
