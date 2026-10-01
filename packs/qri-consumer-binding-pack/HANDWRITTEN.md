# HANDWRITTEN.md - qri-consumer-binding-pack ledger

Every element not emitted by a ggen rule or template is listed here. Generated files under
`generated/` are never hand-edited: change the binding, `ontology.ttl`, a gate or a template and
regenerate with `runners/consume.py`.

## Handwritten sources and residue

| path | kind | standing | reason |
|---|---|---|---|
| ontology.ttl, ontology/alignments.ttl | ontology | n/a (source graph) | the qcb delta itself; everything generated derives from it |
| shapes/qcb.shacl.ttl | shapes | n/a (source graph) | SHACL admission over the ontology |
| gates/*.rq, witnesses/** | gate, witness | n/a (admission source) | SPARQL violation-row gates and their exact-stem pass/fail witnesses |
| qualification/consumer.ttl, qualification/consumer-node-wasi.ttl | binding | n/a (selection input) | the ConsumerBinding is the consumer's input, not a generated artifact; `consumer-node-wasi.ttl` is `consumer.ttl` minus the beam host-profile closure with `qcb:profileId "node-wasi"` and a recomputed `qri:contractDigest` |
| ggen.toml, ggen-node-wasi.toml, profiles.toml, targets.toml, gate-court.toml, pack.toml, package.toml | manifest | n/a | ggen offers no per-profile conditional `[packs]`, so the node-wasi target is a second manifest that `consume.py` copies over `ggen.toml` in the capsule (precedent: qri `ggen-beam-host.toml`); `targets.toml` is the marketplace language declaration, `profiles.toml` maps `qcb:profileId` to a manifest |
| runners/semantic_runner.py | runner | UNSUPPORTED(generator-capability) | the gate-court runner is a fixed contract runner; no ggen capability emits court runners |
| runners/consume.py | runner | UNSUPPORTED(generator-capability) | admission before generation (typed refusal JSON, zero files), the scratch capsule and the two-pass receipt are orchestration around `ggen sync run`; ggen has no pre-sync typed-refusal output and cannot render a receipt of its own outputs |
| runners/receipt.py | runner | UNSUPPORTED(generator-capability) | content digests (RDFC-1.0 contract and binding digests via the qri `qualification/rdfc.py`, pack-content and output listings) and the ProjectionReceipt facts; ggen computes none of them. The receipt JSON itself is rendered by ggen from those facts |
| consume.py check `CONTRACT_DIGEST_MISMATCH`, SHACL pre-check `SHAPE_NONCONFORMANT` | runner-side admission | UNSUPPORTED(generator-capability) | both codes are concepts of `qcb:generation-refusals` (ontology.ttl) and are typed refusals (exit 2), but neither can be a SPARQL gate: RDFC-1.0 canonicalization and SHACL are not SPARQL. Direct `ggen sync run` does not run them, so a wrong declared `qri:contractDigest` or a SHACL-only defect (byte size 0) is refused by `consume.py` only; every authority, pin-cardinality and realization defect is a SPARQL gate that ggen itself enforces |
| consume.py composed gate `030_authority_not_from_capability` (qri) | composed gate | n/a (reuse) | ggen rejects `..` in `[law].gates`, so the qri gate cannot be listed in a manifest; ggen enforces it through the `[packs]` dependency on the beam target, `consume.py` runs it for every target (`profiles.toml [compose]`). Gate 160 is the in-pack superset (any node of the binding graph) enforced by ggen on both targets |

## Generated (never edited)

| path (under `generated/`) | rule | source |
|---|---|---|
| artifact-pin.json | templates/artifact-pin.json.tmpl | qcb:ArtifactPin of the binding |
| contract.json | templates/contract.json.tmpl (projection `op-names`) | contract + qcb:logicalOperation names |
| MANIFEST.json | templates/manifest.json.tmpl (projection `host`, beam-wasmex) | qri:hostProfile + pin; byte-identical to `ash_affidavit/priv/affidavit/MANIFEST.json` (observed with `cmp`) |
| beam-host/{abi,wasm_config,engine_load,host,pool,vendor_task,verify_task}.ex | qri-qualification-profile-pack beam-host templates, reached through the `[packs]` path dependency | qri:hostProfile; byte-identical to the committed `ash_affidavit/lib` files (observed with `cmp`) |
| profiles/node-wasi/{artifact-pin.json,contract.json,projection-receipt.json} and profiles/node-wasi/node-wasi/{host.mjs,authority-boundary.test.mjs} | same templates, node-wasi binding `qualification/consumer-node-wasi.ttl` (`consume.py --out generated/profiles/node-wasi`) | committed so the node-wasi projection is compared with a fresh consume (tests `test_c8_*`); host.mjs: contract + pin, minimal, zero dependencies, closed refusal classes and `requestBytes` for raw frames |
| tests/authority_boundary_test.exs, node-wasi/authority-boundary.test.mjs | templates/tests/* (projection `tests`) | binding ceiling; the node test runs green against the real module, the Elixir test is rendered here and executed in ash_affidavit |
| projection-receipt.json | templates/projection-receipt.json.tmpl | ProjectionReceipt facts written by `receipt.py` (second ggen pass) |

## Step 0 probe: does a `[packs]` path dependency expose qri queries 50-54 and beam-host templates?

Observed with ggen 26.9.28 in scratch capsules (probe files under the session scratchpad, not shipped):

1. A `[packs]` table together with `[[generation.rules]]` in one `ggen.toml` is refused:
   `[FM-CONFIG-101] ggen.toml ... is ambiguous between the declarative-rules and frontmatter schemas`.
   `[packs]` therefore exists only in the frontmatter schema (templates carry `to:`, `when:`, `sparql:`).
2. With `[packs] qri-qualification-profile-pack = { path = ... }` and `[templates] dir`, the dependency's
   frontmatter templates (`templates/beam-host/*.tmpl`) are discovered and rendered against the consumer's
   graph, and the dependency's gates (010-080) are loaded (the receipt lists their digests).
   Queries 50-54 are exposed as the SPARQL embedded in those templates' frontmatter; the standalone
   `queries/50-54*.rq` files are not separately addressable in the frontmatter schema (inferred: only
   declarative rules read `query = { file = ... }`, and that schema rejects `[packs]`).
3. Result: composition by path dependency works, no vendored copy is needed, and the seven rendered
   beam-host files equal the committed `ash_affidavit/lib` files byte for byte (`cmp`, 7 of 7).
4. Limit: dependency templates carry no `when:` guard, so they render for any graph that matches their
   queries. The node-wasi target therefore omits `[packs]` (second manifest, above); a binding whose
   contract has no `qri:hostProfile` would fail the beam templates with a render error rather than a typed refusal.

## Generator gaps recorded as UNSUPPORTED(generator-capability)

| gap | worked around by |
|---|---|
| typed request/response bindings: the operation registry carries names only, so no typed fields can be projected | `qcb:logicalOperation` names only; `contract.json` lists names; no generated file claims typed fields (UNSUPPORTED(projection)) |
| qri host templates render `generated/beam-host/*.ex` only; no deps fragment, no SPDX header | consumer-side handwritten `mix.exs` deps and `REUSE.toml` (ash_affidavit) |
| generated files carry no SPDX header | consumer-side annotation |

## Exit codes and refusal transport (repair 2026-09-30)

`consume.py`: 0 projection; 2 typed REFUSED (key `refused`); 7 typed UNSUPPORTED (key `unsupported`,
standing literal `UNSUPPORTED:<CODE>`); 3 structural (unparseable binding, pyshacl absent: SHACL fails
closed); 4 ggen failed; 5 post-generation SHACL non-conformance (typed JSON); 6 replay mismatch.
Direct `ggen sync run` reports a gate refusal as a failed sync carrying the code text; it does not
distinguish refused from unsupported.

## G1 addendum (audit repair, 2026-09-30)

| path | kind | standing | reason |
|---|---|---|---|
| ../../docs/rfc/SRFC-001-*.md, ../../docs/rfc/SRFC-INDEX.md | specification | n/a (source text) | prose standard; its neutrality, atomicity and defined-term checks are executed by `tests/test_qri_consumer_binding_pack.py` (`test_srfc_*`), not by a generator: ggen has no capability to render normative prose |
| docs/reference-realization-profiles.md | documentation | UNSUPPORTED(generator-capability) | prose; states which profile each committed `generated/` tree represents, the refusal transport and the pin-record mapping |

Removed: `qcb:contractDigest` (duplicate of `qri:contractDigest`; the receipt JSON reads the contract's own
digest). Renamed in receipt JSON: `ggen_version` to `generator_version`.

## G3 addendum (catalog, navigation, supersession visibility, 2026-09-30)

| path | kind | standing | reason |
|---|---|---|---|
| ../../docs/book.ttl (two `mdp:NavigationEntry` rows, nav:181b and nav:181c) | RDF source edit | n/a (source) | adds SRFC-001 and SRFC-INDEX to the book; `docs/SUMMARY.md` is regenerated by `ggen sync run` (never hand-edited). Made on the clean tip-based export; the owner's dirty local edits to `book.ttl`/`SUMMARY.md` are reconciled by regenerating SUMMARY.md after both land |
| ../../docs/reference/standing.md, ../../docs/context/standing.md | generated | regenerated with `scripts/standing.py --sha <tip>` | the script defaults to `git rev-parse HEAD`; the export is not a git repository, so the recorded head SHA is passed explicitly (provenance only; `--check` ignores it). Upstream already marks `affidavit-pack` deprecated (lifecycle.toml, successor `affidavit-consumer-pack`; pack.toml carries no deprecation keys because the ggen pack loader refuses them, FM-PACK-003); lifecycle.toml leaves the `affidavit-pack` entry as upstream (successor `affidavit-consumer-pack` only) and adds a `keep-separate` entry for this pack related to `affidavit-consumer-pack`; `packs/affidavit-pack/pack.toml` is unchanged |

Typed gap, left unrepointed (not semantically equivalent): `agent-harness-recompilation-pack`
`ahr:targetPack "affidavit-pack"` (securityScanner, verification) names the producer-side receipt
verification catalog (BLAKE3 chain verifier). The successor `qri-consumer-binding-pack` manufactures
consumer integration from a ConsumerBinding; it provides no chain verifier. `scripts/es_chain_qualify.py`
`check_affidavit` models the rolling BLAKE3 chain from `reference/affidavit_v26.6.22_src/chain.rs`, an
engine semantic and not a pack dependency. Both are left unchanged.

## Composition with affidavit-consumer-pack (probe 2026-09-30)

Typed gap, UNSUPPORTED(generator-capability): `templates/node-wasi/host.mjs.tmpl` stays because
`affidavit-consumer-pack`'s host templates cannot be composed (falsifiers F1-F7 in
`docs/relation-to-affidavit-consumer-pack.md`): they have no frontmatter so a `[packs]` path
dependency does not render them, their gates need an `afc:Consumer`, `[ontology].imports` rejects
`..`, they read `wja:` not `qri:` facts, and they do not generate the pin, authority ceiling,
import-surface check or closed refusal classes. Court C10 asserts the two hosts agree per op on
`op-examples.json` and on the `wasm_digest_mismatch` refusal, so the duplication cannot drift.

| path | kind | standing | reason |
|---|---|---|---|
| docs/relation-to-affidavit-consumer-pack.md | documentation | UNSUPPORTED(generator-capability) | prose relation and probe record |
| fixtures/node-wasi/parity-affidavit-consumer.mjs | fixture driver | n/a (test input) | drives the afc-generated `affidavit_host.ts` for C10; contains no ABI glue of its own |
| ../../lifecycle.toml `[packs.qri-consumer-binding-pack]` | registry entry | n/a (source) | `keep-separate`, related to `affidavit-consumer-pack`; the earlier extra successor on `affidavit-pack` was reverted: `affidavit-pack`'s successor remains `affidavit-consumer-pack` only |
