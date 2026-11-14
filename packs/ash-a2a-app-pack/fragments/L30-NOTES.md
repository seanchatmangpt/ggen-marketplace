# L30 EA graph seam notes

Standing: UNVERIFIED

- Admission: `run_ea_graph_admission` (ggen crates/ggen-engine/src/sync.rs:418) reads
  `<root>/ea.graph.json`; absent without `--skip-ea-admission` is FM-LAW-015 (sync.rs:422).
- Shape: `ggen_abb_sbb::EaGraph` (crates/ggen-abb-sbb/src/lib.rs:184), schema
  `ggen.ea.graph.v1`, `deny_unknown_fields`; `validate()` at lib.rs:529.
- Template `L30_ea_graph.json.tmpl` writes `ea.graph.json` at the project root (`to:` is
  root-relative; coordinator must confirm the sync output root equals the dir holding ggen.toml).
- Emits one capability, ABB, contract per `aap:Domain`; `candidate_sbbs`, `qualifications`,
  `packs` are empty, so admission passes structurally with nothing to admit. Real SBB admission
  needs sha256 canonical digests (lib.rs:620-631) that Tera cannot compute; a follow-up needs a
  digest-capable step.
- Ordering seam: the ggen admission gate runs before rendering (Stage 0), so on a fresh tree
  the file is absent on the first sync; the coordinator must run the sync twice or place the
  generated file before the admission pass. Confirm on the real run.
- Gate `L30_010_ea_shape.rq`: rows = violations; refusing fixture `fixtures/L30-ea-refuse.ttl`
  should yield `domain-missing-moduleName` and `resource-without-domain`.
- Strategy id is the fixed literal `ash-a2a-app`; ids slug the domain moduleName
  (lower, `.` to `-`); two domains whose slugs collide would hit DuplicateElement.

## Retired template (coordinator)

`templates/L30_ea_graph.json.tmpl` collided with the committed `L19_ea_graph.json.tmpl` on
`ea.graph.json` (ggen FM-WRITE-008, igniter DUPLICATE_OUTPUT). L19 is the live emitter; the L30
template is kept as `L30-ea_graph.json.tmpl.retired` for reference. Gate L30_010 stays.
