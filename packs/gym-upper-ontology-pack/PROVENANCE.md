# Provenance and qualification

Every term in `ontology.ttl` was derived by reading a real file. No term was inferred from
a repo name. The gym submodules under `gym-ecosystem/vendor/` are, at the time of writing,
uninitialized (`ls vendor/<gym>/` returns 0 entries for biblegym, chatgptgym, claudecodegym,
fdegym, gitgym, gymact, lifegym, rrgym, SREGym, ww3gym), so the marketplace pack ontologies
plus `vendor/ggen-ecosystem/ecosystem.ttl` are the only real domain evidence available; the
pack is grounded in those and claims nothing about the gyms' runtime source.

## Found repetitions (real, verified)

- `shasum ggen-marketplace/packs/{chatgptgym-gymact-bridge-pack,lifegym-world-pack}/shapes/profile.shacl.ttl`
  returns the same digest `c6b0a7dbcf3d7b6ea2020798526c038225f5c4a3` for both files — the same
  SHACL shape is duplicated verbatim into two packs. `grep -c sosa:Procedure
  lifegym-world-pack/ontology.ttl` returns `0`: in lifegym that copied shape constrains nothing.
- `<urn:gymact:consequence:read>` / `<urn:gymact:consequence:do>` are referenced by three
  marketplace files and typed by none.
- The same consequence concept appears as an IRI (chatgptgym `dct:type`), a `dct:relation "DO"`
  literal (ww3gym), and a `dcp:consequence "DO"` literal (domain-capability-pack).

## Qualification (real runs, ggen 26.8.28)

- `qualification/union_four_packs.ttl` — this pack's ontology concatenated with the real
  ontologies of chatgptgym-gymact-bridge-pack, lifegym-world-pack, ww3gym-planning-pack and
  domain-capability-pack (579 lines). `ggen sync run` over it emits
  `qualification/expected_crosswalk.rs`: 35 capabilities from three separate source repos
  resolved through all three encodings; graph hash
  `ff38bb07a9f9275677ec9df4cdb934b860f41faec51cd29a5e05c1cfbd5a067c`.
- Gate `gates/010_untyped_consequence_refused.rq`, executed through ggen as a template SPARQL
  block: **0 rows** over the union graph (admitted) and **26 rows** over the identical union
  with this pack's ontology removed (`qualification/negative_gate_rows_without_upper.txt`) —
  the falsifier for "the shared upper ontology is doing real work."

## Authority boundary

Carried over verbatim from `chatgptgym-gymact-bridge-pack/gates/010_execution_boundary.rq` and
its PROVENANCE: `gu:DO` classifies an *intent*. This pack ships no runtime actuation authority;
consequential DO stays behind external GymAct/BRCE admission. `gates/010` refuses any subject
that is both a capability and an authority policy.
