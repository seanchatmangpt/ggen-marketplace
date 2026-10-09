# PACK_FEEDBACK Item 425 — CLOSED

- **Item**: frozen-duckdb `docs/sjira/v26.9.21/PACK_FEEDBACK.md`, G10 table item 1
  (pack defect: `readme-diataxis-pack` `templates/index.md.tmpl:53` emitted
  `[Playground](../playground/)` unconditionally, producing a permanent dead
  link in a GENERATED consumer file whenever the consumer declares zero
  `rdx:PlaygroundFile` rows; observed as `FILE MISS` in frozen-duckdb
  `docs/index.md:34`).
- **Status**: CLOSED 2026-10-09 (lane R151).
- **Fixing commit**: `66462b92b` on `ggen-marketplace` branch `hdit-v2-structs`
  — `fix(readme-diataxis-pack): gate Playground link on declared
  rdx:PlaygroundFile rows`.
- **Fix shape**: template frontmatter declares a `playground` SPARQL query over
  `rdx:PlaygroundFile` rows; the link line is wrapped in `{% if playground %}`.
  No declared rows → no Playground section.
- **Witnesses** (all executed on the fix commit's subject):
  1. Court `tests/test_readme_diataxis_playground_gate.py` — 4/4 passed
     (real template, real frontmatter SPARQL via rdflib over the pack's real
     `qualification/consumer.ttl`, real jinja2 render): present-with-rows and
     absent-without-rows both witnessed.
  2. Real ggen 26.9.28 end-to-end scratch render
     (`/tmp/rdx-g5.rHpo`, `/tmp/rdx-gzero.F67b`): consumer with the pack
     fixture renders the Playground line (`docs/index.md:36`); the same
     consumer with PlaygroundFile rows stripped renders with **zero**
     Playground references (case-insensitive grep rc=1).
  3. frozen-duckdb `docs/index.md` (branch `docs/doc-hdit-scaffold`, head
     `c963899`+): contains no Playground link (consumer-side hand correction
     `5e933a3` already removed it; the upstream pack defect is now closed so a
     future schema-convergence re-render cannot reintroduce it).
  4. Link check over frozen-duckdb `docs/**/*.md` (110 files): **0 broken
     links on doc surfaces**; the only 2 grep hits are the item-425 evidence
     quotes inside `PACK_FEEDBACK.md` itself, not doc links.
- **Consumer consequence**: frozen-duckdb docs lane (R148b) is done; its
  `docs/index.md` needs no further edit — the dead link is gone and the pack
  can no longer regenerate it.
