# ADMISSION-NOTE — semantic-case-study-pack v0.1.0

Status: **admission-ready, NOT admitted.** Admission is a coordinator/court
act; this lane does not edit `marketplace.toml` or the catalog projection.
This note hands the coordinator everything the admission step needs.

## 1. Corrected admission mechanics (premise in the lane brief was false)

The brief asked for "the exact `[pack]` TOML block for marketplace.toml".
Inspection of `marketplace.toml` (HEAD c04bb6dd) shows it carries **no
per-pack registry table** — packs are discovered from `packs/` and the
catalog is a projection (`scripts/marketplace.py`); comments in
marketplace.toml confirm the registry snapshot is "this exact packs/ tree +
the catalog it projects to". Therefore there is no marketplace.toml block to
apply. Admission consists of:

1. the pack living at `packs/semantic-case-study-pack/` with its operative
   identity in its own `pack.toml` (already authored — that `[pack]` table
   IS the registry entry; nothing else is applied by hand);
2. the gate↔witness court qualifying ALIVE (done, see §3);
3. the catalog projection being re-run by the coordinator as part of the
   marketplace-wide projection, never hand-edited.

## 2. Consumer adoption block (operative form)

Per ggen-marketplace-consumer-laws: `[ontology].imports` is operative;
`[ontology.pack]` DOES NOT EXIST. A consumer (e.g. xaas for the WD case
study) adopts via:

```toml
[ontology]
source = "priv/ontology/my_domain.ttl"
imports = [
  "semantic-case-study-pack/ontology",
  "evidence-standing-pack/ontology",
  "decision-optionality-pack/ontology",
]
```

## 3. Verification receipts (exact-head ladder)

Receipt heads: authoring tree at c04bb6dd; first commit f491458bf (witness
binding moved to it); final amended head carries the same pack content
modulo the witness subject literals. Receipts re-earned after rebind where
marked. python3.14 (tomllib+rdflib+pyshacl); `python3` is 3.9.6 without
tomllib.

| Layer | Command | Head | Exit | Result |
|---|---|---|---|---|
| Structural court | `python3.14 scripts/check_gate_witness_courts.py --report /tmp/scsp-court-structural.json` | c04bb6dd, re-earned post-rebind | 0 | court ALIVE, case_count 4, require_pass=require_fail=true; repo-wide standing ALIVE (7 configured packs) |
| Semantic pass | `python3.14 runners/semantic_runner.py --gate gates/<stem>.rq --witness witnesses/pass/<stem>.ttl --expectation pass` ×4 | f491458bf, re-earned post-rebind | 0,0,0,0 | SHACL conforms + 0 refusal rows on all gates |
| Semantic fail | same runner, `--expectation fail` on `witnesses/fail/<stem>.ttl` ×4 | f491458bf, re-earned post-rebind | 0,0,0,0 | exactly the named gate fired (1 row), zero collateral gates |
| Anti-vacuity mutation | mutated fail/040 (`"DO"`→`"SELECT"`) rerun with `--expectation fail` | c04bb6dd | 2 | `REFUSED_EXPECTED_GATE_DID_NOT_FIRE` — a vacuous gate is refused by the court |
| Seed-compat falsifier | shapes+gates run against real `/Users/sac/xaas/priv/packs/wd_cs2_pack/claims.ttl` | c04bb6dd | 0 | SHACL conforms True; gates 010/020/040 = 0 rows; gate 030 = 11 rows, single reason (see §4) |

## 4. Failed edges (recorded, not silently pruned)

1. `pres:`/pptx-presentation-pack: no such pack (or any `pres:` namespace)
   exists in this marketplace (grep over packs/, 0 hits). `cs:Projection`
   stays native; `templates/slide-facts.md.tmpl` consumes the seed's own
   projection conventions (`cs:rendersClaim`/`cs:renderedBy`/
   `cs:noClaimReason`). A future presentation pack can map cs:→pres:.
2. No semantic runner instance existed repo-wide for the
   gate-witness-court contract (the court delegates to a caller-supplied
   runner by design). `runners/semantic_runner.py` is the first concrete
   instance; it implements the argv contract of
   `semantic-gate-witness-court-pack/templates/semantic-gate-witness-court.py.tera`.
3. Real WD cs2 ledger (`xaas:priv/packs/wd_cs2_pack/claims.ttl`) fires
   gate 030 branch 3 (`claim-rendered-by-undeclared-projection`) on 11
   slides because the seed deck slides carry no `rdf:type cs:Projection`.
   Remediation is consumer-side (type the slides in xaas); the gate is not
   weakened. Handoff to the WD-lane owner.
4. python3 (3.9.6) lacks `tomllib`; the repo court script requires 3.11+.
   Use `python3.14` (tomllib + rdflib + pyshacl all present).

## 4b. Side diagnosis handed to the owning lane (publish-packages.yml)

`Publish GitHub Packages` FAILING ×2+ on origin/main (runs 36077005876,
36076886081, 36051906165, 35810209710 — identical signature across SHAs
420bc91e/dafc1d45/5eb71f7e). All publish jobs succeed (snapshot + 8 pack
shards); the failing job is always "Verify exact packaged factory", step
"Pull by exact digest, extract, and execute ggen":
`verified-factory/bin/ggen: Permission denied`, exit 126 (EACCES, not
ENOEXEC — arch mismatch ruled out). Stage side proves the exec bit exists
(`materialize_factory_ggen.sh` line 66 `chmod 0755`; snapshot job executes
`bin/amd64/ggen --version` successfully). Classification per R25-015:
**configuration/packaging failure of the verify extraction path** (docker
cp from the created container losing/presenting a non-executable mode), NOT
transport (digest-exact pull + extract succeeded) and NOT pack-subject
(all shards published on the same runs). This verify job has never passed
(its workflow_run trigger only started firing 2026-09-23 when upstream
Publish first concluded success). Fix hypotheses for the owner: inspect the
image's stored mode (`docker create` + `docker export | tar -tv`), prefer
`docker save`-based extraction (mode-faithful) or an explicit
`chmod +x "$root/bin/ggen"` only if the image layer mode is proven correct;
R25-016: no unchanged re-run without a new hypothesis.

## 5. Standing

Pack standing: **PARTIAL_ALIVE → ALIVE on its own court** (structural ALIVE
+ semantic 8/8 + anti-vacuity witnessed). NOT yet:
marketplace-admitted (coordinator), cold-replayed in a clean clone
(R25-010 is release-crown scope), or consumed by a real case (WD remediation
in §4.3).
