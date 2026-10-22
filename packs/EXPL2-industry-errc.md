# EXPL2 — industry pack skeptic sweep (EXPLORE, read-only)

Lane: standing explorer, EXPL2. Date: 2026-10-22. Surface:
`~/ggen-marketplace/packs/industry-*` (6 packs) + `~/ggen/examples/industry/*`.
Method: rdflib cross-gate interference matrix over every (gate × witness × gate)
cell, real court-runner executions, BOT spec fetch, smalt file:line spot-checks
(10+ cites verified against ~/smalt at current HEAD). No commits. Nothing repaired.

## Standing summary

| pack | witness court | cross-gate exact-one-law | ontology vs real vocab | court executable |
|---|---|---|---|w
| industry-manufacturing-dflss | strict runner, exactly-one enforced | clean | OCEL 2.0 prefix inline, honest | YES (best of six) |
| industry-pharma-21cfr | verify.py, own-gate-only | clean (observed matrix all-clean) | PROV-O IRIs correct | YES |
| industry-legal-ediscovery | witnesses clean (ASK matrix verified) | clean | PROV-O declared, unused in gates | config only — no `runner` key |
| industry-aero-defense | verify.py, own-gate-only | **VIOLATED (observed)** | PROV-O used correctly | verify.py present, no gate-court.toml |
| industry-semantic-cad-bim | verify.py, own-gate-only | **VIOLATED (observed)** | **bot:containedIn is NOT a BOT term** | YES |
| industry-financial-ledger | NONE (no runner, no verify.py, combined witnesses) | n/a — no per-gate isolation at all | n/t | NO |

## F1 (TOP) — industry-aero-defense: fail/pass witnesses violate a second law; court is blind to it

File: `industry-aero-defense/witnesses/{pass,fail}/020_cross_level_flow.ttl`

The 020 witnesses' ClassifiedArtifacts carry classification + caveat but NO
`ad:needToKnowPrincipal`. Gate `010_artifact_classification_complete.rq` fires
**2 rows** over BOTH the 020 pass witness and the 020 fail witness (verified with
rdflib, ontology.ttl mixed in as verify.py does):

```
020_cross_level_flow pass x 010_artifact_classification_complete: 2  <-- PASS DIRTY
020_cross_level_flow fail x 010_artifact_classification_complete: 2  <-- CROSS-FIRE
```

So the 020 **pass** witness is itself non-compliant with law 010, and the 020
fail witness breaks two laws at once. `qualification/verify.py` checks each
witness only against its own gate, so this is structurally invisible to the
court that exists; `scripts/marketplace.py check` (run: `check ok packs=1
turtle=ok qualify=ok` for all six packs) does not execute witness courts at all.
The one-liner receipt `{"failures": [], "gate_count": 3, "standing": "ALIVE"}`
is therefore over-claimed: "ALIVE" hides a pass witness that violates a refusal
law. Exactly-one-law-per-fail-witness is asserted in the pack description
("classified artifacts MUST carry classification + caveat + cleared principal")
and is factually violated by the pack's own fixtures.

Close condition (repair-lane dispatch): give the 020 witnesses' artifacts a
`ad:needToKnowPrincipal` (and an `ad:Principal` individual), or have verify.py
run the full gate×witness matrix (dflss's runner already implements exactly this
contract: `REFUSED_MORE_THAN_ONE_GATE_FIRED` / `REFUSED_GATE_ROWS_ON_PASS`).

## F2 — industry-semantic-cad-bim: same court blindness, observed cross-fire

`witnesses/pass/030_orphan_geometry.ttl` fires gate 010 (2 rows: its elements
have no `bot:containedIn` storey); `witnesses/fail/030_orphan_geometry.ttl`
cross-fires 010 (1 row). verify.py is own-gate-only → silent. Same repair
template as F1: adopt the dflss runner contract.

## F3 — industry-semantic-cad-bim: `bot:containedIn` is not in BOT

The pack claims "real vocabularies: BOT (https://w3id.org/bot#)" but
`bot:containedIn` does not exist in BOT — containment is expressed container→
contained (`bot:hasElement`/`bot:containsElement`/`bot:containsZone`; spec
verified via w3c-lbd-cg.github.io/bot). The phantom term is load-bearing: gate
`010_element_storey_containment.rq`, `ontology.ttl`, `cad-shacl.ttl.tera`,
`walkthrough.md.tera`, and the generated consumer at
`~/ggen/examples/industry/semantic-cad-bim/{ontology.ttl,generated/cad-bim/shapes.ttl,walkthrough.md}`
all use it (5/2/1 occurrences). Any real BOT tooling/dataset round-trip will not
recognize the containment edge. Either adopt BOT's actual direction
(`bot:hasElement`/`bot:containsElement` storey→element) or declare a pack-local
`cad:containedIn` with rdfs:subPropertyOf/seeAlso to BOT honestly.

## F4 — industry-financial-ledger has no executable court

Only pack with neither `gate-court.toml` nor a verifier, and its witnesses are
combined (`witnesses/pass.ttl`, `witnesses/fail.ttl`) rather than per-gate
exact-stem — the fail.ttl deliberately breaks all three laws at once. Nothing
executes anywhere: `marketplace.py check` passes it (`qualify=ok` — the check
does not run witness courts, which is itself a coverage gap in the check). The
gates are good SPARQL; the court leg is missing entirely.

## F5 — gate-court.toml wiring gaps

- `industry-legal-ediscovery/gate-court.toml` has NO `runner` key (schema/
  dirs/require_pass/require_fail only) — the court cannot be executed from the
  config; the RECEIPT instead ran an inline heredoc. Its witnesses are actually
  clean (ASK matrix verified clean) — this is a wiring gap, not a fixture defect.
- `industry-aero-defense` has no gate-court.toml at all (verify.py exists but is
  unreferenced by a court config).

## F6 (minor) — stale copy-paste in the dflss runner docstring

`industry-manufacturing-dflss/runners/semantic_runner.py` docstring says it
"judges strategic-doctrine-pack witnesses against strategic-doctrine-pack
gates" — names the wrong pack (adapted-from residue). The code is correct and
is the strictest court of the six (exactly-one-law enforced, cross-pack stem
guard).

## Verified-clean legs (receipt for the sweep)

- Qualification determinism (task c): `verify.py` for aero-defense, pharma, and
  cad-bim each run twice — byte-identical JSON/output, exit 0 both runs.
- smalt file:line citations (task d): 10+ cites verified at ~/smalt HEAD —
  `workspace/lib/smalt.ts:11,22`, `AttestRoutes.ex:17,38-58`,
  `cosmos.ex:133` (ETag return), `blob_storage.ex:273/305/516` (WORM arms),
  `egress_router.ex:1313/1563/2282` (immutabilityPolicy routes),
  `KvRoutes.ex:28,147` (create/jwk_for_kty), `AppConfigRoutes.ex:50`,
  `event_hubs/listener.ex:3`, `event_hubs.ex:847`, `powl2/andon.ex`,
  `powl2/sb_rules.ex`, `amqp_broker.ex:35`, `ocel_ndjson.ex` — ALL resolve and
  name what the walkthroughs claim.
- legal-ediscovery witnesses fully clean under the ASK cross-matrix (an earlier
  SELECT-row count misread was my harness artifact — ASK yields one row
  regardless of answer; corrected run: zero dirty/cross/vacuous cells).
- dflss and pharma witness sets: zero cross-fire, zero vacuous legs.
- OCEL 2.0 usage (dflss) matches what `Smalt.Telemetry.OcelNdjson` writes
  (`ocel:events/objects/eventTypes/objectTypes` keys confirmed in
  lib/smalt/telemetry/ocel_ndjson.ex:46).
