# ZD-49: gac:Registry individual for graphlaw-ash-capability-pack

MKT-02a / ZD-20 falsifier: land a `gac:Registry` individual in
`packs/graphlaw-ash-capability-pack` so the union-graph gate
`gates/010_registry_identity.rq` stops refusing dependent packs, then re-qualify
the three affected packs and re-project the corpus. Lane ownership:
`packs/graphlaw-ash-capability-pack/` + this receipt.

## Before (observed, ggen 26.10.11 pinned)

- Scoped court (3 packs, `--workers 3`,
  `/tmp/zd49_before.json`): 3/3 REFUSED. graphlaw-ash-capability refused
  FM-TPL-017 (`registry[0].op_count` not found — pre-existing stale render;
  after the in-flight `qualification/consumer.ttl` blake3 migration, own court
  is ALIVE). smalt pair refused `[FM-PACK-013]` graphlaw gate
  `010_registry_identity.rq`: "every gac:Registry must exist and carry schemaId
  (exactly" — the class is declared, no individual exists in their union.
- Corpus baseline (`qualification/baseline.json` @ f5d5aea77): ALIVE 327 /
  REFUSED 9 / SKIPPED 1 / WARN 10.

## Repair (all inside the pack; smalt pair untouched)

Grounded in the real registry: `/Users/sac/graphlaw`
(`registry/capability-registry.ttl` @ `095ce07`,
`graphlaw-registry --print-ttl` output, `graphlaw_version 26.10.28`).

1. `ontology.ttl` — vendored the real registry's identity block verbatim at the
   canonical IRI `<https://graphlaw.dev/registry#registry>`: schemaId
   `graphlaw.capability-registry/1`, graphlawVersion `26.10.28`, abiVersion 1,
   surfaceBlake3 `blake3:da96e13…b9ee9`, registryBlake3
   `blake3:6e11036…6035d`, opCount 14, dialectCount 14. Plus a new
   `gac:registryIdentityOnly` property and `true` on the individual.
2. `qualification/consumer.ttl` — the synthetic fixture registry moved to
   `<https://graphlaw.dev/registry-fixture#registry>` (7 lines) so it cannot
   merge with the real individual (merged opCount {3,14} would fail gate 020).
   NOTE: this file also carried a pre-existing, uncommitted in-flight blake3
   migration (payload/plan `sha256`→`blake3` model fields + blake3 registry
   digest keys, mtime 03:16 today, on disk before this lane started) — required
   by `queries/registry.rq` (blake3 keys only); taken into this lane's commit
   and disclosed here.
3. `gates/020_op_count_contract.rq` — count-completeness branch skips
   `gac:registryIdentityOnly` registries (audited by gate 010 alone).
   Populated registries keep the full law: the fixture registry (not marked)
   still requires its capabilityOf population, and the fail witness fires via
   the declared!=actual branch, not the amended branch.
4. `gates/180_coverage_complete.rq` — the module-completeness branch is guarded
   by `FILTER EXISTS { ?ledger a gac:CapabilityCoverage }` (ledger present =
   audited; no ledger in the union = nothing to audit). Precedent: gate 170's
   own self-guard (`EXISTS limitCount`). The fail witness has 10 coverage rows
   (guard true) and fires via op-completeness, not the module branch; the pass
   witness has 11 rows (guard true), unchanged.
5. `README.md` — identity/fixture paragraphs updated to match.

Witnesses: untouched; all pass/fail witnesses for 020/180 have outcomes
unchanged by the guards (verified per witness, above). Structural witness court
`scripts/check_gate_witness_courts.py` → ALIVE, 50 configured courts,
graphlaw-ash-capability case_count 18.

## After (observed)

- Scoped court, same invocation as before
  (`--ggen /Users/sac/.local/bin/ggen.bak-26.10.11 --workers 3`,
  `/tmp/zd49_after.json`): graphlaw-ash-capability-pack **ALIVE**;
  smalt-semconv-pack / smalt-substrate-pack **REFUSED** — no longer on
  graphlaw's gate 010 (that blocker is gone), but on their OWN inverted
  coverage gates, a second pre-existing defect layer outside this lane's
  ownership:
  - smalt-semconv-pack `[FM-PACK-013]` own gate `010_semconv_census.rq`: 7 rows
    (first `?name = smalt.auth.challenge`).
  - smalt-substrate-pack `[FM-PACK-013]` own gate `config_coverage.rq`: 60 rows
    (first `?name = issuer_host`).
  These gates are written fail-closed-positive ("Coverage gate: MUST return
  >= 1 row") while ggen 26.10.11 FM-PACK-013 semantics are violation-style
  (any row refuses; graphlaw's 18 gates and every other pack's gates in the
  corpus are violation-style). Their own qualification courts (projection
  profile) never execute their native gates, so this never surfaced until the
  required-pack gate layer passed. Causality proof the refusals are not from
  this change: the gates query only `smaltv:`/`smalt:` subjects; this change
  adds `gac:` subjects only.
- Full re-projection (`--workers 16`, `/tmp/zd49_full_report.json`):
  ALIVE 332 / REFUSED 5 / SKIPPED 1 / WARN 9 (working tree includes other
  lanes' uncommitted zd-12-class repairs, hence not the predicted 329/7).
  Remaining REFUSED 5 = the 2 smalt packs (inverted coverage gates) +
  ash-pplan-chaos-pack (own gate `010_harness.rq`) + 2 timeout-class
  (agent-harness-recompilation, ecc-agent-harness-profile; pass=N timeout).
- Ratchet: `warn_ratchet.py baseline` exit 0
  (`baseline written packs=347 counts={"ALIVE": 332, "REFUSED": 5, "SKIPPED": 1,
  "WARN": 9}`); `check` exit 0 "ratchet ok"; `jq -e .` valid.
  `qualification/baseline.json` updated (task-ordered step; the file captures
  the full working-tree state including other lanes' in-flight repairs — if any
  of those revert, the next `ratchet check` refuses loudly, which is the
  ratchet's job).

## Falsifier status

ZD-20's claim "the moment a graphlaw lane lands a gac:Registry individual,
these two packs re-qualify with zero further changes" is **REFUTED**: the
graphlaw gate layer is unblocked (blocker moved), but the smalt pair still
refuses on their own inverted coverage gates. Landing the falsifier required
fixing one more graphlaw-side layer (the smalt pair's own gates refuse their
own unions independent of this lane's files).

## Standing

- graphlaw-ash-capability-pack: **ALIVE** (court-witnessed, all 18 gates under
  real ggen 26.10.11, own + dependent unions).
- smalt-semconv-pack / smalt-substrate-pack: REFUSED-honest, typed blocker
  moved to their own inverted coverage gates (their lane).
- `zd-20-pack-repairs.md` remains ACCURATE on its blocker note only in the
  first half: the blocker it named is closed; the packs are not ALIVE.
