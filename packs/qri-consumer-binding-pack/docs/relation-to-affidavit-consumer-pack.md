# Relation to affidavit-consumer-pack

Non-normative. Records how `qri-consumer-binding-pack` (prefix `qcb:`) and `affidavit-consumer-pack`
(prefix `afc:`) relate, and the exact result of the composition probe (2026-09-30, ggen 26.9.28).

## Roles

| | affidavit-consumer-pack | qri-consumer-binding-pack |
|---|---|---|
| input | `afc:Consumer` vocabulary plus the module's `wja:` facts | `qcb:ConsumerBinding` (contract, realization, profile, pin, ceiling) |
| emits | typed event constants and object-ref builders (TypeScript, Python), a CI verify action, `affidavit_host.ts` and `affidavit_host.py` | `artifact-pin.json`, `contract.json`, `projection-receipt.json`, BEAM host (via qri), `node-wasi/host.mjs`, authority-boundary tests |
| audience | a third-party project adopting affidavit | a consumer binding a specific wasm artifact under authority NONE |
| lifecycle | live successor of the deprecated `affidavit-pack` | live, `keep-separate`, related to `affidavit-consumer-pack` and `qri-qualification-profile-pack` |

`qri-consumer-binding-pack` is not a replacement for `affidavit-consumer-pack`. Use
`affidavit-consumer-pack` for the event vocabulary and the TypeScript or Python host projections;
use this pack when the consumer must state an exact artifact pin, a realization, an authority
ceiling and receive a typed refusal or a projection receipt.

## What the packs share

Both hosts instantiate the same module through `node:wasi` preview1 and call the same
`af_alloc` / `af_call` / `af_free` ABI. Court C10 (`tests/test_qri_consumer_binding_pack.py`)
renders both hosts, drives all nine `op-examples.json` requests through each against the real
`affidavit.wasm`, and asserts the per-operation JSON responses are equal, and that both refuse a
tampered module with the code `wasm_digest_mismatch`.

## Composition probe: result NOT_VIABLE

The question: can the node-wasi profile render through `affidavit-consumer-pack`'s host templates
instead of owning `templates/node-wasi/host.mjs.tmpl`? Observed falsifiers, each reproduced:

| id | observation | consequence |
|---|---|---|
| F1 | `affidavit-consumer-pack/templates/*.tmpl` carry no `to:` frontmatter (0 of 5). ggen discovers dependency templates only in the frontmatter schema, which is the only schema that accepts `[packs]` | a `[packs]` path dependency cannot render them |
| F2 | with the dependency declared, ggen runs its gates on the union graph: `010_single_consumer.rq` refuses (`consumers=0`, FM-PACK-013) because a qcb binding has no `afc:Consumer` | the binding would have to carry the consumer vocabulary |
| F3 | `[ontology].imports` rejects `..` paths (FM-CONFIG-003), so the pack's `wja:` facts cannot be imported from the sibling pack | the module facts would have to be copied or regenerated |
| F4 | `host.rq` reads `wja:WasmModule` / `wja:hasOp`; a binding carries `qri:opName` and `qcb:logicalOperation` | a handwritten qri-to-wja mapping layer would be needed |
| F5 | the afc TS host takes the pin as an optional caller argument; it is not baked from `qcb:ArtifactPin` | pin equality would be a caller duty, not a generated property |
| F6 | the afc TS host has no authority constant, no import-surface or required-export check, no closed refusal classes, no raw-frame entry point, and throws on `ok:false` instead of returning the typed envelope with `class` | the qcb authority and refusal semantics (`AUTHORITY`, `classOf`, `requestBytes`, `--check` exit 3) would be lost or re-added by handwritten glue |
| F7 | the afc TS host is `.ts` (needs `--experimental-strip-types` or a build step); the qcb host is plain ESM that runs under `node` | different deployment contract |

Observed equal: sha256 pin verified before compile; typed `wasm_digest_mismatch`; same per-op
responses on all nine examples. Those equalities are what C10 keeps true; they do not make the
templates interchangeable.

Reversal condition: if afc templates gain `to:`/`sparql:` frontmatter and the pin, authority
constant and import checks are generated from facts the binding already carries, composition
becomes a path dependency like the beam-wasmex profile. Until then the node-wasi host template
is a recorded gap in `HANDWRITTEN.md` (UNSUPPORTED(generator-capability)), not an accepted
duplicate.
