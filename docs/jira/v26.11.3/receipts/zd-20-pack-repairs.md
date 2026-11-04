# ZD-20: pack repairs for the 7 ZD-12 REFUSED packs

Repair the real defects behind the 7 REFUSED entries in
`qualification/baseline.json` (see `zd-12-baseline-reconcile.md`). No court was
relaxed: every fix is a real file-level repair, and each pack was re-qualified
through the real court.

## Per-pack repairs and court outcomes

| pack | before | repair | after |
|---|---|---|---|
| court-kit-pack | REFUSED | ontology.ttl line 25 used `rdf:Property` with no `@prefix rdf:` declared — added the missing prefix declaration | **ALIVE** |
| fortune5-enterprise-architecture-pack | REFUSED | shipped zero `templates/*.tmpl`; added `templates/f5ea_vocabulary_census.md.tmpl` + `queries/classes.rq` (real SPARQL-backed Tera census of the f5ea: vocabulary: owl:Class / owl:ObjectProperty terms with their rdfs:comment contracts), scratch-rendered exit 0 with 7 real rows | **ALIVE** |
| pack-bootstrap-pack | REFUSED | zero `templates/*.tmpl`; added `templates/bootstrap_vocabulary_census.md.tmpl` + `queries/classes.rq` (census of the bp: meta-vocabulary — the BootstrapTarget contract classes/properties), scratch-rendered exit 0 with real rows | **ALIVE** |
| rust-doc-hdit-pack | REFUSED | zero `templates/*.tmpl`; added `templates/code_surface_census.md.tmpl` + `queries/classes.rq` (census of the dhs:/doc: code-surface extraction vocabulary — the tree-sitter extraction contract), scratch-rendered exit 0 with real rows | **ALIVE** |
| smalt-semconv-pack | REFUSED | zero `templates/*.tmpl`; added `templates/semconv_mapping_table.md.tmpl` + `queries/mapping_rules.rq` (renders the sealed smaltv:OcelMappingRule OTEL→OCEL mapping table as a markdown table), scratch-rendered exit 0 with real rows | **REFUSED (blocked)** |
| smalt-substrate-pack | REFUSED | zero `templates/*.tmpl`; added `templates/store_table_registry.md.tmpl` (renders the smalt:StoreTable registry via the pack's canonical `queries/store_tables.rq`, unmodified), scratch-rendered exit 0 with real rows | **REFUSED (blocked)** |
| typer-azure-pack | REFUSED | FM-GEN-008: template used `row.kind` but ggen's SPARQL engine drops the UNION branch whose bindings are all `BIND` placeholders, so `?kind` never reached the template. Removed the phantom discriminator: `queries/typer.rq` is now a single BGP (`SELECT ?appName ... ORDER BY ?appName ?flag`), and `templates/typer_commands.py.tera` groups real option rows by app via Tera `group_by(attribute="appName")` with key-value iteration, rendering a complete, py-renderable Typer module (24 option rows, exact az flag names) | **ALIVE** |

Blocker for the two smalt packs (disclosed, not repaired here): their
`capabilities.requires` declare `graphlaw-ash-capability-pack`; its union-graph
gate `gates/010_registry_identity.rq` refuses because the sibling's ontology
declares the `gac:Registry` class but no `gac:Registry` individual. That pack
dir is outside this lane's file ownership (one of zd-12's other 7 regressions,
owned by another pack lane) and was not touched. Per lane law the blocker
branches the search graph rather than terminating it: the moment a graphlaw
lane lands a `gac:Registry` individual, these two packs re-qualify with zero
further changes — their own defects are already repaired and locally proven
(scratch renders exit 0).

## Toolchain pin (disclosed)

The baseline was courted under ggen 26.10.11 (recorded in
`qualification/baseline.json.ggen_version`). Mid-wave, the PATH `ggen` moved to
26.11.3 (binary swapped 2026-11-04 02:20). Under 26.11.3, [FM-LAW-015] refuses
EVERY `ggen sync run` without `--skip-ea-admission` or an `ea.graph.json` —
observed refusing the scratch consumers AND packs that qualify ALIVE under
26.10.11, i.e. a corpus-wide toolchain regression affecting all 347 packs, not
a pack defect. All court runs in this receipt are pinned:
`--ggen /Users/sac/.local/bin/ggen.bak-26.10.11`. Corpus-wide 26.11.3 adoption
(including the court script's ggen invocation) is a separate, cross-lane
finding — never silently mixed into this baseline.

## Commands / exits

- Scoped before-court (PATH ggen, then 26.10.11): exit 2, 7/7 REFUSED, real
  defect output captured per pack (FM-PACK-005 ×5, FM-GRAPH-002 court-kit,
  FM-GEN-008 typer-azure).
- Scratch render proofs (ggen 26.10.11, `/tmp/packv/*`): each new
  template+query renders exit 0 with real ontology rows; `smalt-substrate`
  verified with the pack's canonical, unmodified `store_tables.rq`.
- Scoped after-court:
  `python3 scripts/qualify_packs.py --ggen /Users/sac/.local/bin/ggen.bak-26.10.11 --workers 7 --report /tmp/zd20_report.json --pack <each of 7>`
  -> exit 2 (2 honest REFUSED remain, the blocked smalt pair); 5 ALIVE.
- Full re-projection:
  `python3 scripts/qualify_packs.py --ggen /Users/sac/.local/bin/ggen.bak-26.10.11 --workers 16 --report /tmp/zd20_full_report.json`
  -> exit 2 (`REFUSED:...:failed=9 total=347`), report written.
  `python3 scripts/warn_ratchet.py baseline /tmp/zd20_full_report.json`
  -> exit 0, "baseline written packs=347 counts={ALIVE: 327, REFUSED: 9, SKIPPED: 1, WARN: 10}"
  `python3 scripts/warn_ratchet.py check /tmp/zd20_full_report.json`
  -> exit 0 "ratchet ok"; `jq -e . qualification/baseline.json` -> valid;
  `jq -c .counts` -> {"ALIVE":327,"REFUSED":9,"SKIPPED":1,"WARN":10}
  (baseline: ALIVE 322->327, REFUSED 14->9; remaining 9 REFUSED = the 2
  blocked smalt packs + zd-12's 7 regressions owned by other lanes).

## Standing

ALIVE for the 5 repaired packs (court-witnessed). REFUSED-honest for
smalt-semconv / smalt-substrate with a typed, disclosed blocker. The corpus
counts live in the ratchet baseline, recomputed mechanically — never
hand-stated here.
