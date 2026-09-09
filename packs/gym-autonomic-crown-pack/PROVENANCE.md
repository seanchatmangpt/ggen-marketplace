# Provenance — gym-autonomic-crown-pack

Every term in `ontology.ttl` traces to a real surface in
`https://github.com/seanchatmangpt/gym-ecosystem`, read at pack-authoring time.
Nothing here was inferred from a repository name or from field names alone.

## Source surfaces read

| Pack term | Real source |
| --- | --- |
| `crown:CrownReceipt`, `crown:schema` | `artifacts/autonomic-crown.json`, `"schema": "https://ggen.dev/receipts/gym-autonomic-crown/v2"` |
| `crown:SubmoduleEdge`, `crown:edgeName/edgePath/remoteUrl` | `.gitmodules` sections parsed by `scripts/crown-submodules.py::submodules()` |
| `crown:GitlinkObservation`, `crown:gitlinkMode` | `scripts/crown-submodules.py::gitlink()` — asserts mode `160000`, kind `commit`, else `CROWN_BLOCKED[NOT_GITLINK]` |
| `crown:RemoteHeadObservation`, `crown:defaultRef`, `crown:latestSha` | `scripts/crown-submodules.py::remote_head()` — `git ls-remote --symref <url> HEAD` |
| `crown:baseSha` | `scripts/crown-submodules.py::plan()` — `git rev-parse HEAD` |
| `crown:changed`, `crown:Drifted`, `crown:Converged` | `plan()`'s `current != latest` and the receipt's `changed` / `changed_count` keys |
| `crown:GitlinksAndLockOnly` | the literal `"authority_boundary": "gitlinks+lock-only"` the script emits, and its module docstring |

## Public vocabulary reuse

- `sosa:Observation` / `sosa:FeatureOfInterest` / `sosa:usedProcedure` /
  `sosa:hasSimpleResult` — a gitlink SHA and a remote HEAD SHA are literally
  results of a procedure applied to a feature of interest at a time. This is
  what sosa models; no minted term is needed.
- `prov:Entity` — the receipt is a generated artifact.
- `dcat:Distribution` / `dcat:accessURL` — each submodule remote is a
  distribution reachable at a clone URL.
- `dcterms:identifier` (superproperty of `crown:edgeName`), `skos:Concept` /
  `skos:prefLabel` for the two controlled drift states.

Only `crown:` terms are minted: gitlink-mode assertion, crown authority
boundary, and the current-vs-latest drift comparison — none of which a public
vocabulary covers.

## Authority boundary

This pack **observes and serializes**. It carries no runtime actuation
authority. It never runs `git checkout`, `git commit`, `git push`,
`git submodule update`, or writes `ecosystem.lock.toml`. Consequential DO
remains with the superproject's admitted crown workflow
(`.github/workflows/autonomic-crown.yml`), which already enforces:

- `CROWN_BLOCKED[WORKFLOW_MUTATION_OUTSIDE_AUTHORITY]` on any diff outside
  gitlinks + lock,
- `GYM_CROWN_BLOCKED[UNAUTHORIZED_PATH]` on any staged path not declared in
  `.gitmodules`,
- `GYM_CROWN_REFUSED[MAIN_MOVED]` compare-and-swap before promotion.

`gates/040_authority_boundary_is_gitlinks_and_lock_only.rq` refuses to render
any receipt claiming a wider boundary than the one the real script emits.

## Verification performed (ggen 26.8.28, 2026-09-06)

1. `--from-receipt` lift of the committed `artifacts/autonomic-crown.json`,
   rendered through `templates/autonomic_crown.json.tmpl`, `diff` against the
   committed file → **byte-exact, zero diff**.
2. `--observe` live run against `/Users/sac/gym-ecosystem` (13 real
   `git ls-remote --symref` calls, ~10s) → receipt identical to the committed
   one except `base_sha`, which is stale in the committed artifact.
3. All four gates pass on the live graph; a tampered fixture
   (`tests/fixtures/tampered-crown.ttl`) trips gates 020, 030 and 040 →
   `CROWN_GATES BLOCKED failed=3`, exit 1.
