# Release v26.9.30

Release notes for ggen-marketplace v26.9.30, covering `v26.9.29..main`. The qualification
numbers below come from one real run of `scripts/qualify_packs.py` with ggen 26.9.28 over all 394
packs. Where a claim rests on fixtures or tests that were not run for this release, it is marked
PARTIAL or UNKNOWN.

## Qualification

```text
python3 scripts/qualify_packs.py --ggen "$(which ggen)" --workers 6 --report qual.json
qualified packs=394 ggen="ggen 26.9.28"            (exit 0)
ALIVE 377 / WARN 12 / SKIPPED 5 / REFUSED 0
python3 scripts/warn_ratchet.py check qual.json    (exit 0; 18 improvements, no regression)
```

- 394 packs: 376 from v26.9.29 plus 18 new. None removed.
- The first full run of this range refused 7 packs (affidavit-pack,
  authzen-spiffe-absorption-pack, canonical-ash-projection-generator, fleet-family-registry,
  repository-reconstitution-pack, sa2a-diataxis-pack, sa2a-semantic-evidence-pack). Each was
  fixed in the pack without weakening a gate; the second full run refused none.
- All 18 new packs are ALIVE under the qualifier. ALIVE here means ggen loads the pack and
  converges to the same filesystem consequence on two passes (plus a real `cargo build` where a
  Rust crate is generated). It does not prove the semantic claims in a pack's README.
- WARN 12 and SKIPPED 5 are the same packs as in the baseline committed before this release.
  WARN is a generated-crate `cargo build` failure; SKIPPED needs a real cargo workspace root.
  `qualification/baseline.json` was re-recorded from this run.

## Known limitations

- ggen pin drift. `marketplace.toml` `[ggen]` still pins `v26.8.11` (release commit and asset
  digests), while qualification ran the installed ggen 26.9.28 through
  `qualify_packs.py --ggen "$(which ggen)"`, as `qualification-baseline.md` documents. The
  `scripts/qualify-marketplace.sh` path would refuse this binary (`GGEN_VERSION_DRIFT`). The
  repo has no script that updates the pin and its per-platform SHA-256 digests, and they were
  not guessed.
  Updating the pin needs the 26.9.28 release asset digests and is not part of this release.
- The industry-closure family (`industry-closure-pack`, `industry-closure-ledger-pack`,
  `industry-closure-retail-lending-profile-pack`) states in its READMEs that real-ggen manufacture
  of its closure artifacts is `BLOCKED:ggen_binary_unavailable` in an environment without the
  binary and that nothing in it is Level-5. Qualifier ALIVE does not change that statement.
- `chicago-graphlaw-court-pack` is UNVERIFIED: its corpus run is REFUSED (see the pack README).
- The Chicago work-equivalent claim (500,000,000 person-years) is UNSUPPORTED: the ledger holds 0
  admitted evidence items.
- `affidavit-consumer-pack`: its real 9-op wasm proof is skip-guarded (needs affidavit.wasm, node,
  wasmtime) and was not run here.
- `graphlaw-ash-capability-pack` is not engine-qualified beyond the ggen run above.
- The lifecycle consolidation review covers 381 of 394 packs; 13 packs are listed there as not
  reviewed.
- 11 existing packs received a version bump only to satisfy `release-check`; see below.

## New packs (18)

| Area | Packs | Standing |
|---|---|---|
| GraphLaw / WASM runtimes | `wasi-json-abi-pack`, `graphlaw-ash-capability-pack`, `chicago-graphlaw-court-pack`, `qri-qualification-profile-pack` | PARTIAL |
| Affidavit | `affidavit-consumer-pack`, `affidavit-trust-plane-pack` | PARTIAL |
| SA2A | `sa2a-semantic-evidence-pack`, `sa2a-semantic-diataxis-pack`, `sa2a-diataxis-pack`, `authzen-spiffe-absorption-pack` | PARTIAL |
| Closure | `capability-closure-pack`, `industry-closure-pack`, `industry-closure-ledger-pack`, `industry-closure-retail-lending-profile-pack` | PARTIAL |
| Fleet / legacy | `fleet-family-registry`, `repository-reconstitution-pack` | PARTIAL |
| Operating model, feedback | `enterprise-operating-model-pack`, `sjira-marketplace-feedback-pack` | UNKNOWN |

`qri-qualification-profile-pack` ships its reference `domain.rs` as a qualification overlay, so
its generated adapter crate really builds under the qualifier.
`affidavit-pack` is now recorded as deprecated in `lifecycle.toml`, superseded by
`affidavit-consumer-pack`.

## Changed packs

- `dfcm-pack` 2.1.0: CI optimization profile and projections.
- `ash-extension-pack` 0.3.1 and `ash-extension-core-pack` 0.1.1: `--target` installer uses
  `Spark.Igniter.add_extension/5`.
- `swe-prometheus-governance-pack` 0.2.1, `errc-ownership-manifest-pack` 26.9.26: gate witnesses.
- Patch bumps for content changes: `adapter-family-registry`, `affidavit-pack`,
  `canonical-ash-projection-generator`, `ex4pm-wasm4pm-bindings-pack`, `projection-matrix-pack`
  (0.1.0 to 0.1.1), `cs2-fleet-contract` (1.0.0 to 1.0.1), and CalVer `cs2-exact-subject-pack`,
  `epistemic-sensor-factory-pack`, `ontostar-mustar-powlv2-agent-pack` (to 26.9.30).

## Infrastructure

- CI is one path-classified workflow with `ci/courts/*.sh` courts.
- `marketplace.py` gains `release-check`, `diff`, `check`, `browse`, `search`, `show`.
- Pack lifecycle registry and the 26.9.30 consolidation review.
- Catalog trust tiers, WARN ratchet, supply-chain tooling, `new_pack` scaffolder, manufacture
  timing, and the Chicago work-equivalent court.

## See Also

- [Qualification baseline](qualification-baseline.md)
- [Pack consolidation review 26.9.30](pack-consolidation-review-26.9.30.md)
- [Chicago work-equivalent court](chicago-work-equivalent-court.md)
- [Pack lifecycle registry](pack-lifecycle-registry.md)
