# shacl-to-zod-pack qualification

Standing: PARTIAL

## Subject

`packs/shacl-to-zod-pack` — pack.toml version 0.3.0 (on-disk head,
2026-11-05). Ontology 8 triples (thin: composition contract + schema
target facts); gates: `gates/010_template_literal_scan.py` only (no .rq).

## What was verified

Wave receipts (cmms v26.11.5):

- `L10.md` — pack binding resolved by `ggen sync run --dry-run` probe
  (exit 0, content hashes); planned writes witnessed for
  `src/shacl_zod_schemas.ts` / `src/shacl_zod_schemas.js`. Disclosed there:
  an `output_dir` override key in ggen.toml was silently ignored, so zod
  schemas land at `src/` not `lib/schema/` unless pack templates change.
  No render or type-check of the projected schemas was receipted for this
  pack.
- `L11.md` — consumer files carry the `PROJECTION-TARGET: shacl-to-zod`
  header and must be re-sealed by this pack's projection; the projection
  itself was not re-run in that lane.

Qualification lane re-run against the CURRENT 0.3.0 head (2026-11-05):

- `ontology.ttl` parse: OK, 8 triples (rdflib).
- Gate: `python3 gates/010_template_literal_scan.py` → exit 0,
  output `ALIVE: templates ontology-driven, no banned literals`. The gate
  is fail-closed by construction (unreadable template file also exits 1);
  no mutation flip was run by this lane — non-vacuity is by code structure
  (banned-literal tuple + hardcoded-export regex), not witnessed firing.

## Standing basis

PARTIAL: the pack parses, its gate exits clean this session, and binding +
planned-writes are receipted (L10), but no render of the projected zod
schemas nor a type-check court has been witnessed at any head this wave.
