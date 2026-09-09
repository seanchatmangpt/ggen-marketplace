# Source provenance

## Capability facts (`ontology.ttl`)

Derived from `autofde-lab` working tree at
`/Users/sac/gym-ecosystem/vendor/autofde-lab`, exact head
`edca036e02526014c5298b0cefd287c68ec0eab4`, file
`src/autofde_lab/openclaw_bridge.py` (`_TOOL_SPECS`, 4 entries) and
`src/autofde_lab/openclaw_runtime.py:357` (`TOOL_NAME_PREFIX = "autofde_lab_"`).

No capability was invented: each `sosa:Procedure` individual corresponds to one
real entry in `_TOOL_SPECS`, and its `dct:title` is that entry's `name`.

## Pack shape

Derived from GymAct's own `ggen/consumer-bridge-pack-template/` at `gymact` head
`33e49c18ac10b37978b70aa9fd2ca500e6431052`, generalized the same way
`chatgptgym-gymact-bridge-pack` was.

## SHACL shape (`shapes/profile.shacl.ttl`)

Copied from `chatgptgym-gymact-bridge-pack/shapes/profile.shacl.ttl`; sha256
re-verified as `1b64989f8097c58bdada3ad7cb793098288d042f1c4ded6cbfefd6e3af0022f5`,
matching that pack's recorded `shapes/DIGESTS.txt`. GymAct source commit
`5a40c8f402aeb14699e216e17b2ef7aae9f0bc8f`, source path
`src/gymact/ontology/profile.shacl.ttl`.

Standing: `PARTIAL_ALIVE_PROVENANCE` — inherited from the chatgptgym pack, not
independently re-fetched. Promotion requires a real `gymact export-profile` run
and a digest comparison before claiming GymAct-export provenance.

## Consequence-class divergence found while grounding this pack

`vendor/autofde-lab/gymact/ontology/gymact.ttl` mints a **local** four-value
consequence vocabulary (`ga:consequenceClass` in `READ`/`PREPARE`/`DO`/`VERIFY`,
lines 62-119) that is **not** GymAct's real two-IRI classification
(`urn:gymact:consequence:read` / `urn:gymact:consequence:do`). That file's own
header comment (lines 27-33) acknowledges the divergence and defers adoption.

This pack does not reconcile that vocabulary; it classifies autofde-lab's real
OpenClaw MCP surface directly against GymAct's two real IRIs. `gates/020_no_custom_tbox.rq`
refuses any attempt to smuggle the local `ga:` vocabulary into this pack's graph,
and the real SHACL shape refuses it at sync time (verified — see below).

## Authority boundary

Generated artifacts are classification and documentation only. A `Do` row records
that an operation *can* cause a consequence, never that a caller is permitted to
cause it. Consequential DO stays behind GymAct/BRCE admission and autofde-lab's
own runtime gate. This pack has no runtime standing.

## Verification actually run (ggen 26.8.28)

- `ggen sync run` wrote 3 files, graph hash
  `1f94eaadb00c885c719c936ce1f3df3e35aa8d71390b77bbc94fa60f33088c77`.
- Replay: second `ggen sync run` wrote 0 files, all skipped "unchanged: content
  identical"; `shasum -a 256` before/after byte-identical.
- `rustc --edition 2021 --crate-type lib` compiles both generated `.rs` files clean.
- Sabotage falsifier: appending one `sosa:Procedure` with
  `dct:type <urn:autofde-lab:consequence:PREPARE>` makes `ggen sync run` exit 1 with
  `[FM-TPL-025] ... A GymAct capability must classify consequence as READ or DO`,
  and **zero** files are written (fail-closed, verified by `ls src docs` after).
- Gate replay via rdflib: both gates return 0 refusal rows on the clean ontology;
  `010_execution_boundary.rq` returns 1 row
  (`unknown-consequence-class-refused`) on the sabotaged one.
