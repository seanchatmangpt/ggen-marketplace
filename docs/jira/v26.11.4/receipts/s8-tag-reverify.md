# S-8: MKT-04 pack-side standing re-verify at the v26.11.3 ggen pin

Standing: PARTIAL_ALIVE

## Scope and gate disclosure (CARRY-19)

- SEED.md scope (ggen `docs/jira/v26.11.4/SEED.md:93-94`, `:124`): MKT-04 =
  pack-side standing re-verify at the v26.11.3 tag, **gated on CARRY-19**
  (SEED.md:49 — mint 3 tags), and SEED.md:94 states "no tag minted yet".
- Verified on disk 2026-11-05: tag `v26.11.3` does not exist in
  /Users/sac/ggen (latest local tag v26.11.0; `git ls-remote --tags origin`
  also shows only `refs/tags/v26.11.0` in the 26.11 range) nor in
  /Users/sac/ggen-marketplace. `git -C /Users/sac/ggen rev-parse v26.11.3`
  → `fatal: unknown revision`.
- Therefore the git-tag-archive replay form of MKT-04 is **BLOCKED on
  CARRY-19**. The executed form is the version-pinned re-verify: the ambient
  court binary is exactly `ggen 26.11.3` (`ggen --version` → `ggen 26.11.3`,
  /Users/sac/.local/bin/ggen), matching the pin. This is the same court
  identity zd-65 used ("ambient ggen 26.11.3", zd-65-smalt-gates.md:46-47).

## Falsifier

A qualified pack fails at-pin re-verify. Outcome: **1 pack REFUSED on the
before-run** (qri-consumer-binding-pack) — falsifier fired once; fixed
forward pack-side and full corpus now exit 0.

## Commands / exits

1. Baseline full corpus (348 packs, workers 6, ggen 26.11.3):
   `python3 scripts/qualify_packs.py --workers 6 --report /tmp/s8_reverify.json`
   → **exit 2**: 329 ALIVE / 17 WARN / 1 REFUSED / 1 SKIPPED.
   REFUSED = `qri-consumer-binding-pack`
   `REFUSED:GGEN_PACK_SYNC_FAILED` — `[FM-PACK-008]` content hash mismatch:
   `packs/qri-consumer-binding-pack/ggen.lock` had
   `blake3:e127bef667949e9c4532673feb9cc779201d11a4518ecd253af0449b6a8936bc`
   but pack on disk hashes to
   `blake3:51567d618c14dd11f3c950f2d77b79fb17826359bedb6a67d91e70ef0354f226`.
2. Root cause: commit `de5678164` (S11 hardening lane) modified
   `packs/qri-qualification-profile-pack/qualification/qualify.py`
   post-lock (lock minted at `8404cdd3d`); the consumer's ggen.lock was
   never regenerated. Pack-side drift, not ggen-side.
3. Fix forward (pack-side, per ggen's own remediation text "delete
   ggen.lock to intentionally re-lock"):
   - `cd packs/qri-consumer-binding-pack && rm ggen.lock && ggen sync run
     --skip-ea-admission` → **exit 0**; new lock hash
     `blake3:51567d618c14...` (byte-diff limited to `ggen.lock` —
     `git status --short .` shows only `M ggen.lock`).
4. Post-fix full corpus (348 packs, workers 6, ggen 26.11.3):
   `python3 scripts/qualify_packs.py --workers 6 --report /tmp/s8_reverify2.json`
   → **exit 0**: 330 ALIVE / 17 WARN / 0 REFUSED / 1 SKIPPED.

## WARN/SKIPPED disclosure

- 17 WARN rows are all `REFUSED:GGEN_PACK_GENERATED_BUILD_FAILED` /
  `_TEST_FAILED` under `CARGO_BUILD_CHECK_BLOCKING=False` (non-blocking
  build-check class). The zd-52 typed baseline was 10 ACCEPTED-WARN; the
  WARN count has drifted 10 → 17. Same refusal class, but the +7 delta is
  **not individually typed** in any receipt I found — flagged as a follow-up
  (each row needs an ACCEPTED-WARN row or a repair lane; not repaired here,
  outside S-8 scope).
- 1 SKIPPED: tcps-pack `GGEN_PACK_GENERATED_BUILD_NEEDS_WORKSPACE_ROOT`
  (known harness limitation, matches zd-52's typed SKIPPED row).

## Lane hygiene disclosure

Pre-existing dirty files from another lane were present and untouched:
`packs/kafka-wire-pack/*` (9 files), `packs/smalt-substrate-pack/ontology.ttl`
(`git status --short`). Both packs graded ALIVE in the post-fix run; my only
owned file change is `packs/qri-consumer-binding-pack/ggen.lock`.

## Files owned (uncommitted, per lane law)

- `packs/qri-consumer-binding-pack/ggen.lock` (re-lock, blake3 updated)

## Standing

PARTIAL_ALIVE: full-corpus at-pin re-verify exit 0 (330/330/0/1, zero
REFUSED), one pack-side defect found and fixed forward. Git-tag replay form
remains BLOCKED on CARRY-19 (tag not minted); WARN delta 10→17 flagged as
open follow-up.
