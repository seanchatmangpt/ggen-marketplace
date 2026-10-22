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

---

# EXPL2R — REPAIR lane receipt (2026-10-22)

Repairs EXPL2 F1-F6. Original findings preserved above, untouched.
Verification gate: the strict exact-stem runner
(`runners/semantic_runner.py`, dflss exemplar ported to all four packs)
executed over every (gate x witness x expectation) cell, plus
`python3 scripts/marketplace.py validate` (exit 0, packs=338 validated),
plus a non-vacuity mutation probe (below). No commits.

## F1/F2 — cross-fire eliminated (before/after)

Observed cross-gate interference matrix (SELECT rows per gate-witness cell;
ontology mixed in; `.` = zero rows, X = rows fired):

| cell (witness x gate) | before | after |
|---|---|---|
| aero pass/020 x 010 | **2 (PASS DIRTY)** | . |
| aero fail/020 x 010 | **2 (CROSS-FIRE)** | . |
| cad-bim pass/030 x 010 | **2 (PASS DIRTY)** | . |
| cad-bim fail/030 x 010 | **1 (CROSS-FIRE)** | . |
| all other 56 cells (5 packs) | . | . |

After state, executed matrix (5 packs x 3 gates x pass+fail = 30 cells, all exit 0):

- industry-aero-defense ALL-CELLS-GREEN
- industry-semantic-cad-bim ALL-CELLS-GREEN
- industry-financial-ledger ALL-CELLS-GREEN
- industry-legal-ediscovery ASK-tolerant runner ALL-CELLS-GREEN (confirms EXPL2's cleanliness finding)
- industry-manufacturing-dflss ALL-CELLS-GREEN (runner untouched; F6 docstring only)

Witness fixes:
- aero `witnesses/{pass,fail}/020_cross_level_flow.ttl`: both artifacts now
  carry `ad:needToKnowPrincipal` + an `ad:Principal` individual with
  `ad:clearanceLevel` (pass witness now satisfies law 010; fail witness breaks
  ONLY the cross-level law). SHACL-clean under shapes.ttl (ClassConstraint on
  ad:Secret/TopSecret resolves via merged ontology graph).
- cad-bim `witnesses/pass/030`: elements given storey membership;
  `witnesses/fail/030`: wall1 given storey membership -- the orphan-geometry
  law is the ONLY law broken. (Fixture texts also converted to the F3 property
  fix, below.)

Exactly-one-law enforcement now live in aero/cad-bim/financial/legal runners:
- `REFUSED_MORE_THAN_ONE_GATE_FIRED` (fail witness trips a second gate -> exit 2)
- `REFUSED_GATE_ROWS_ON_PASS` (pass witness fires any gate -> exit 2)
- `REFUSED_EXPECTED_GATE_DID_NOT_FIRE` (fail witness silent on its own gate -> exit 2)
- cross-pack stem guard (`REFUSED_STRUCTURAL`, gate outside gates/)
- aero + cad-bim `qualification/verify.py` rewritten as strict full-matrix
  aggregators over the runner (old own-gate-only verify.py retired; exit 0).
- Non-vacuity probe (real mutation, real restore): appending an artifact with
  classification-but-no-caveat to aero fail/020 (breaks a second law) ->
  `{"refusal":"REFUSED_MORE_THAN_ONE_GATE_FIRED","others":{"010...": [["...extra","caveat"]]}}`, exit 2; restored witness -> exit 0. A court that cannot flip was the EXPL2 failure mode; this one flips.

## F3 — bot:containedIn -> bot:hasElement (real spec defect)

BOT 0.3.2 fetched live (w3c-lbd-cg/bot master bot.ttl): `bot:containedIn` does
not exist; element membership is storey->element via `bot:hasElement`
(`bot:containsElement`/`adjacentElement`/`intersectingElement` subproperties).
Replaced throughout cad-bim pack + consumer:

- gates/010 (FILTER NOT EXISTS { ?storey a bot:Storey ; bot:hasElement ?element })
- queries/10-design-surface.rq
- ontology.ttl law comment, README.md, pack.toml description
- templates/cad-shacl.ttl.tera G1 shape -> `sh:path [ sh:inversePath bot:hasElement ]`
  with `sh:qualifiedValueShape [ sh:class bot:Storey ] ; sh:qualifiedMinCount 1`
  (building-level hasElement edges lawful; a first-cut inversePath+sh:class
  draft penalized them -- caught by the court itself, fixed to qualified)
- templates/walkthrough.md.tera
- new pack-local `ontology/shapes.ttl` (static SHACL for the runner SHACL leg;
  G2 root-exemption reworked to a sh:SPARQLTarget -- the prior sh:not pattern
  fired on roots under subclass closure, caught by the court, fixed)
- witnesses pass/fail 010 + 030 rewritten in the hasElement direction
- consumer `~/ggen/examples/industry/semantic-cad-bim`: ontology.ttl triples
  flipped to storey->element, `ggen sync run` regenerated
  generated/cad-bim/{shapes.ttl,walkthrough.md}; 5 consecutive re-syncs
  byte-identical (sha1 bc2cdbd2..., walkthrough cab83878...).
- Zero `bot:containedIn` triples remain anywhere (only honest prose notes that
  BOT 0.3.x defines no such term).

## F4 — financial-ledger executable court built

- witnesses split from combined pass.ttl/fail.ttl into per-gate exact-stem
  witnesses/pass|fail/{010,020,030}.ttl; each fail witness breaks EXACTLY one
  law (010: 250!=240 balanced-otherwise; 020: dangling+missing account on
  otherwise-balanced, unique ids; 030: dup id on otherwise-balanced, declared
  accounts). Combined fixtures deleted.
- runners/semantic_runner.py ported + gate-court.toml (dflss contract,
  REFUSED_MORE_THAN_ONE_GATE_FIRED enforced). All 6 cells exit 0.
- SHACL leg reports `shacl: not-configured` loudly (pack ships no shapes) --
  a skip is loud, not a fake pass.

Legal-ediscovery gates are ASK-shaped: runner teaches `result.type == "ASK"`
-> `askAnswer` maps True -> one refusal row. Three repair iterations visible
in-session: merged-ontology graph (aero levelOrder visibility), qualified
value shape (cad-bim G1), SPARQLTarget (cad-bim G2) -- the court found each
first-draft defect, not the skeptic.

## F5 — wiring

- aero gate-court.toml created (runner key + dirs + require_pass/fail)
- legal-ediscovery gate-court.toml `runner` key added (was config-only)
- cad-bim gate-court.toml runner key repointed from legacy verify.py to the
  strict runner

## F6 — dflss runner docstring corrected (strategic-doctrine-pack -> industry-manufacturing-dflss).

## Verification summary

- 30/30 witness-court cells green across 5 packs (exit 0 each)
- aero + cad-bim qualification/verify.py (strict aggregator) exit 0
- `python3 scripts/marketplace.py validate` exit 0 (packs=338)
- `marketplace.py check`: 8 REFUSED rows, ALL pre-existing in unrelated packs
  (chicago-tdd-tools, cnv-any-manifest, fortune5-, greene-, pack-bootstrap,
  rust-doc-hdit, smalt-semconv, smalt-substrate); zero industry-* refusals
- cad-bim consumer: `ggen sync run` x5 byte-identical outputs
- no commits made
