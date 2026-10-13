# STRATA Namespace Unification Map

> **STATUS: LANDED 2026-10-13 (commit bc54e0869). This document records the PRE-migration state and the old→new mapping. All rows below describe the state BEFORE the migration; current disk state uses the Target column values everywhere (verified by audit lane A10: zero `urn:strata:` IRIs remain in pack data surfaces; capability tokens unchanged by design).**

Authoritative old→new IRI mapping for the strata namespace unification (v26.10.8). Verified against the working tree of `strata-hardening-wave` (pre-migration state), 2026-10-12. Execution of the migration is the coordinator's, after this document lands.

## Migration targets

| current | target | notes |
|---|---|---|
| `urn:strata:protocol:pdu#` (pdu:) | `https://strata.chatman.ai/ontology/pdu#` | protocol pack |
| `urn:strata:protocol:wire#` (wire:) | `https://strata.chatman.ai/ontology/wire#` | protocol pack; also borrowed by valve pack |
| `urn:strata:protocol:` (base_iri / pack.toml namespace) | `https://strata.chatman.ai/ontology#` | protocol base |
| `urn:strata:valve#` (valve:) | `https://strata.chatman.ai/ontology/valve#` | valve pack |
| `urn:strata:valve:` (base_iri / pack.toml namespace) | `https://strata.chatman.ai/ontology/valve#` | valve base has no fragment of its own; bare valve IRIs (e.g. `<urn:strata:valve#refusalReceiptLen>`) fold under `/valve#` |
| pn64/cas/signer/stratus/temprun `st:` = `https://strata.chatman.ai/ontology#` | UNCHANGED | already on target host |

Capability tokens are UNCHANGED (opaque `urn:` identifiers; `urn:` is the house convention for capability tokens, not ontological IRIs):

- `urn:ggen:pack:strata-protocol-pack`
- `urn:ggen:pack:strata-valve-pack`
- `urn:ggen:pack:strata-pn64-pack`
- `urn:ggen:pack:strata-cas-pack`
- `urn:ggen:pack:strata-signer-pack`
- `urn:ggen:pack:strata-stratus-pack`
- `urn:ggen:pack:strata-temprun-pack`
- `urn:strata:protocol:clap-pdu-v1`
- `urn:strata:protocol:refusal-receipt`
- `urn:strata:valve:refusal-taxonomy`

## Mapping table (file-level)

Columns: file | current IRI/prefix | target IRI/prefix | notes.

### strata-protocol-pack

| file | current IRI/prefix | target IRI/prefix | notes |
|---|---|---|---|
| pack.toml:8 | `namespace = "urn:strata:protocol:"` | `https://strata.chatman.ai/ontology#` | namespace field |
| ggen.toml:10 | `base_iri = "urn:strata:protocol:"` | `https://strata.chatman.ai/ontology#` | protocol base |
| ggen.toml:17 | `pdu = "urn:strata:protocol:pdu#"` | `https://strata.chatman.ai/ontology/pdu#` | `[ontology.prefixes]` |
| ggen.toml:18 | `wire = "urn:strata:protocol:wire#"` | `https://strata.chatman.ai/ontology/wire#` | `[ontology.prefixes]` |
| ontology.ttl:4 | `@prefix pdu: <urn:strata:protocol:pdu#>` | `https://strata.chatman.ai/ontology/pdu#` | @prefix |
| ontology.ttl:5 | `@prefix wire: <urn:strata:protocol:wire#>` | `https://strata.chatman.ai/ontology/wire#` | @prefix |
| gates/010_header_layout.rq:6 | `PREFIX pdu: <urn:strata:protocol:pdu#>` | `https://strata.chatman.ai/ontology/pdu#` | gate query |
| gates/020_refusal_receipt_len.rq:5,7 | `PREFIX pdu:` / `PREFIX wire:` (urn:strata:protocol:*) | pdu#/wire# targets | gate query |
| queries/frame_constants.rq:2 | `PREFIX pdu: <urn:strata:protocol:pdu#>` | `https://strata.chatman.ai/ontology/pdu#` | generation query |
| queries/wire_classes.rq:3 | `PREFIX wire: <urn:strata:protocol:wire#>` | `https://strata.chatman.ai/ontology/wire#` | generation query |
| templates/pdu_constants.rs.tera:1 | provenance comment `from urn:strata:protocol:` | `https://strata.chatman.ai/ontology` | regenerated via ggen sync |
| templates/wire_constants.rs.tera:1 | provenance comment `from urn:strata:protocol:wire` | `https://strata.chatman.ai/ontology/wire` | regenerated via ggen sync |
| generated/pdu_constants.rs:1 | provenance header embeds `urn:strata:protocol:` | new IRI via regeneration | do not hand-edit |

### strata-valve-pack

| file | current IRI/prefix | target IRI/prefix | notes |
|---|---|---|---|
| pack.toml:8 | `namespace = "urn:strata:valve:"` | `https://strata.chatman.ai/ontology/valve#` | namespace field |
| ggen.toml:10 | `base_iri = "urn:strata:valve:"` | `https://strata.chatman.ai/ontology/valve#` | valve base |
| ggen.toml:17 | `valve = "urn:strata:valve#"` | `https://strata.chatman.ai/ontology/valve#` | `[ontology.prefixes]` |
| ggen.toml:18 | `wire = "urn:strata:protocol:wire#"` | `https://strata.chatman.ai/ontology/wire#` | cross-pack borrow of protocol's wire prefix |
| ontology.ttl:4 | `@prefix valve: <urn:strata:valve#>` | `https://strata.chatman.ai/ontology/valve#` | @prefix |
| ontology.ttl:5 | `@prefix wire: <urn:strata:protocol:wire#>` | `https://strata.chatman.ai/ontology/wire#` | cross-pack borrow |
| gates/010_refusal_atom_closure.rq:4 | `PREFIX valve: <urn:strata:valve#>` | `https://strata.chatman.ai/ontology/valve#` | gate query |
| gates/020_wire_class_present.rq:3,10,14 | comment + `PREFIX valve:` + `BIND(<urn:strata:valve#refusalReceiptLen>)` | `/valve#` target | gate query; line 3 comment embeds full wire IRIs `<urn:strata:protocol:wire#RefusalReceipt>` |
| queries/receipt_len.rq:2 | `PREFIX valve: <urn:strata:valve#>` | `https://strata.chatman.ai/ontology/valve#` | generation query |
| queries/refusals.rq:2 | `PREFIX valve: <urn:strata:valve#>` | `https://strata.chatman.ai/ontology/valve#` | generation query |
| templates/refusals.ex.tera:3 | provenance comment `from urn:strata:valve:` | `/valve#` target | regenerated via ggen sync |
| generated/refusals.ex:3 | provenance header embeds `urn:strata:valve:` | new IRI via regeneration | do not hand-edit |

### strata-pn64-pack, strata-cas-pack, strata-signer-pack, strata-stratus-pack, strata-temprun-pack

No migration required. All five ontologies, ggen.toml base_iri/prefixes, gates, and queries already use `st: <https://strata.chatman.ai/ontology#>`. Capability `provides` entries are `urn:ggen:pack:*` (unchanged).

Verified @prefix lines (all identical): `@prefix st: <https://strata.chatman.ai/ontology#>` at ontology.ttl:3 in pn64, cas, signer, stratus, temprun.

## Lockstep checklist (per pack, every transition in one commit)

For protocol and valve packs, in this order, per pack:

1. `ontology.ttl` — all `@prefix` lines.
2. `ggen.toml` — `base_iri` and every `[ontology.prefixes]` entry.
3. `pack.toml` — `namespace` field.
4. Every `queries/*.rq` `PREFIX` line.
5. Every `gates/*.rq` `PREFIX` line (and embedded IRI comments/BINDs — see hazards).
6. Templates embedding the namespace string in provenance comments.
7. Regenerate `generated/` via `ggen sync run` — provenance headers embed the IRIs; do not hand-edit.
8. Row-count-equality guard: capture SELECT row counts per query before and after; a missed PREFIX returns 0 rows and, with `skip_empty=false`, emits an empty file silently.

## Hazards

- **Silent empty output.** A missed `PREFIX` in a `.rq` makes the query match 0 rows; with `skip_empty = false` ggen still emits an (empty) file and exits 0. Require a row-count-equality check per query before/after migration.
- **Cross-pack prefix borrow.** `strata-valve-pack` borrows protocol's `wire:` prefix (`packs/strata-valve-pack/ontology.ttl:5`, `ggen.toml:18`). Migrating protocol's wire namespace without valve in the same commit breaks valve's gates/queries.
- **Embedded IRIs in gate comments/BINDs.** `strata-valve-pack/gates/020_wire_class_present.rq` line 3 embeds full wire IRIs in a comment and line 14 has a `BIND(<urn:strata:valve#refusalReceiptLen> ...)` — a PREFIX-only sweep misses these.
- **Historical st: embed.** `strata-protocol-pack/ggen.toml` declares no `st` prefix, but `strata-pn64-pack/templates/pn64_masks.rs.tmpl:3` embeds an `st:` SPARQL query string. If protocol templates ever gain an `st:` embed, protocol ggen.toml would need the `st` prefix added. Note: pn64 has BOTH `pn64_masks.rs.tmpl` (frontmatter+SPARQL form, embedded `st:` query) and `pn64_masks.rs.tera` — the dead `.tmpl` variant should be retired separately; it is not part of this migration.
- **Valve base namespace collapse.** `urn:strata:valve:` (base) and `urn:strata:valve#` (prefix) both fold to `https://strata.chatman.ai/ontology/valve#`; confirm no IRIs of the form `urn:strata:valve:<local>` (non-fragment) exist in the graph before collapsing. Current scan found none outside capability tokens.

## Rollback

Single revert of the migration commit restores all old IRIs; the old→new table above is retained here as the receipt.

## Post-migration verification

- Row-count guard: 79/28/108 SELECT row counts identical pre/post migration (no query silently returned 0 rows).
- Generated provenance headers (`generated/pdu_constants.rs`, `generated/refusals.ex`) now cite the `https://strata.chatman.ai/ontology*` IRIs.
- 7/7 strata courts ALIVE after migration.
