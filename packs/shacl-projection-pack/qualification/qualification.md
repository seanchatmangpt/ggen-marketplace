# shacl-projection-pack qualification

Standing: PARTIAL

## Subject

`packs/shacl-projection-pack` — pack.toml version 0.3.0 (on-disk head,
2026-11-05). Ontology 23 triples; gates: `010_shape_validity.rq`,
`020_schema_model_named.rq`, `030_literal_scan.py`. qualification/ already
held `consumer.ttl` and `rich/` (fixture + ggen.toml + templates) before
this file; no qualification.md existed.

## What was verified

Wave receipts (cmms v26.11.5):

- `L10.md` — this pack was bound in the cmms manifest as a REQUIRED
  composition (shacl-to-zod-pack's pack.toml requires composing it);
  planned writes witnessed in the /tmp dry-run probe:
  `schemas/shacl_projection.schema.json`, `docs/shacl-projection-vocab.md`.
  No render of those outputs was receipted.

Qualification lane re-run against the CURRENT 0.3.0 head (2026-11-05):

- `ontology.ttl` parse: OK, 23 triples (rdflib).
- Gate baselines (rdflib SELECT): `010_shape_validity.rq` rows=0;
  `020_schema_model_named.rq` rows=0. Both exit-clean.
- Gate: `python3 gates/030_literal_scan.py` → exit 0, output
  `ALIVE: no banned literals in templates/`.
- No anti-vacuity flip was run by this lane for the two .rq gates —
  non-vacuity not witnessed here (the python gate is fail-closed by
  construction; the .rq gates were baseline-run only).

## Standing basis

PARTIAL: real gates run clean this session against the current head, but
no flip witnessed on the .rq gates and no render court of the pack's own
outputs (schema.json / vocab doc) has been receipted this wave.
