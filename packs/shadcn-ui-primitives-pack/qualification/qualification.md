# shadcn-ui-primitives-pack qualification

Standing: ALIVE

## Subject

`packs/shadcn-ui-primitives-pack` — pack.toml version 0.3.0 (on-disk head,
2026-11-05). Ontology 126 triples; templates: 7 component templates + cn
helper projection; gates: `010_cn_requires_helper_projection.rq`,
`020_requires_dep_declared.rq`.

## What was verified

Wave receipts (this repo's consumers, cmms v26.11.5):

- `P1.md` — cn helper template rendered via awk and type-checked:
  `tsc --noEmit --strict lib/utils.ts` exit 0 (typescript 5.9.3, pinned after
  7.0.2 hung); render proven non-vacuous earlier in the receipt by inspection.
- `P2.md` — pack.toml parse (tomllib exit 0), version 0.1.0 → 0.2.0 at that
  time, `[consumer_contract]` runtime deps verified against all 7 templates
  (`grep` counts: 7/7 import `@/lib/utils`; clsx / cva / tailwind-merge /
  `@radix-ui/react-tabs`).
- `P3.md` — ontology facts + fail-closed gate: rapper parse exit 0; rdflib
  gate baseline rows=0 exit 0; ANTI-VACUITY FLIP witnessed (HelperProjection
  retyped to OrphanProjection → 7 violation rows, exit 1). ggen gate-runner
  subcommand typed UNSUPPORTED — gates run via rdflib per sibling convention.
- `P4.md` — full scratch-consumer court at `/tmp/p4-consumer`: `ggen sync run
  --skip-ea-admission` exit 0 wrote 8 files (lib/utils.ts + 7 components/ui);
  strict `tsc --noEmit` exit 0; ANTI-VACUITY FLIP `rm lib/utils.ts` → tsc
  exit 2 TS2307 on all 7 components; restore via re-lock exit 0. Re-proven
  against the current pack head after a mid-court substrate move.

Qualification lane re-run against the CURRENT 0.3.0 head (rdflib 7.x,
2026-11-05):

- `ontology.ttl` parse: OK, 126 triples.
- Gate baselines: `010_cn_requires_helper_projection.rq` rows=0;
  `020_requires_dep_declared.rq` rows=0 (both exit-clean via rdflib SELECT).
- Anti-vacuity flip (in-memory mutation, no pack file modified):
  HelperProjection → OrphanProjection retype → 15 violation rows.

Note: P1–P4 receipts were witnessed against 0.1.0/0.2.0-era heads; the gate
baseline + flip above were re-run this session against 0.3.0. Version-skew
disclosed: template bodies unchanged since (P4 substrate-move note), but no
fresh render+tsc court has been witnessed against the 0.3.0 head itself.

## Standing basis

ALIVE: gates executed this session against the current head with a witnessed
flip, plus a full consumer render+tsc court (P4) on the immediately
preceding head with templates unchanged.
