# WARN-1: WARN-baseline reconcile (17-row recount, typed)

Standing: PARTIAL_ALIVE

## Scope / owned files

- REPO: /Users/sac/ggen-marketplace. Owned file changed: `qualification/baseline.json`
  only (re-record + typed annotations + provenance). `scripts/qualify_packs.py` was
  temporarily patched (120s→600s cargo bound) for one diagnostic run and **reverted**
  (verified: absent from `git diff --stat` below). MK-1's dirty files
  (kafka-wire-pack, smalt-substrate-pack) and S-8's (qri-consumer-binding-pack/ggen.lock)
  untouched.
- Baseline identity: zd-52 typed baseline
  (`docs/jira/v26.11.3/receipts/zd-52-warn-typing.md`) typed 11 rows (10 WARN +
  1 SKIPPED) at ggen 26.10.11. A later regeneration (81faeab6c, 2026-11-04) overwrote
  the typed annotations — on-disk baseline had **0 `warn_class` fields** before this
  task (the typing itself was already rotted; `git log -- qualification/baseline.json`
  shows 81faeab6c as last writer: projected ggen 26.10.11 report, counts 338/0/1/9).
- S-8 receipt (`docs/jira/v26.11.4/receipts/s8-tag-reverify.md`) witnessed the same
  17-WARN shape at the same court identity (ggen 26.11.3) and registered the 10→17
  delta as untyped follow-up. This receipt closes that registration.

## Per-row classification (all 17 WARN + 1 SKIPPED typed)

Fresh full-corpus run: `python3 scripts/qualify_packs.py --report /tmp/warn1-report.json`
(default workers 8) → **exit 0**, 330 ALIVE / **17 WARN** / **0 REFUSED** / 1 SKIPPED,
ggen 26.11.3, 348 packs.

**Class A — typed-known, 7 rows.** zd-52 ratchet-residue lineage
(`ACCEPTED-WARN:missing-external-path-dependency` etc.; per-pack evidence in
`packs/<pack>/qualification.toml:1-8`, zd-52 table). Path deps resolve only inside
sibling repos (ggen / wasm4pm / tcps); correct in the intended consumer workspace.

| # | pack | warn_reason (current) |
|---|---|---|
| 1 | automatic-autonomic-operations-pack | missing path dependency: failed to read `ggen-graph/Cargo.toml` |
| 2 | certification-assist-evidence-control-pack | missing path dependency: failed to read `ggen-graph/Cargo.toml` |
| 3 | certification-assist-pack | missing path dependency: failed to read `ggen-graph/Cargo.toml` |
| 4 | ex4pm-wasm4pm-bindings-pack | missing path dependency: failed to read `miniml-core/Cargo.toml` |
| 5 | ontostar-mustar-powlv2-agent-pack | missing path dependency: failed to read `ggen-architecture/Cargo.toml` |
| 6 | speedrun-talent-network-pack | missing path dependency: failed to read `ggen-architecture/Cargo.toml` |
| 7 | tcps-release-pack | missing path dependency: failed to read `tcps-core/Cargo.toml` |

zd-52 typed tcps-release-pack as `ACCEPTED-WARN:workspace-members-not-pack-outputs`;
the current warn_reason is the missing-path-dependency form of the same
ratchet-residue class; the baseline annotation preserves the zd-52 slug.

**Class B/C — environment-wedge, 10 rows**, annotation
`ACCEPTED-WARN:cargo-build-check-timeout-syspolicyd-wedge`. All are
"cargo build/test timed out after 120s" under `CARGO_BUILD_CHECK_BLOCKING=False`
(`REFUSED:GGEN_PACK_GENERATED_BUILD_FAILED` / `_TEST_FAILED`, non-blocking):

| # | pack | warn_reason |
|---|---|---|
| 8 | clap-noun-verb-crate-pack | cargo build timed out after 120s manifest=consumer/Cargo.toml |
| 9 | clap-noun-verb-schema-pack | cargo build timed out after 120s manifest=consumer/Cargo.toml |
| 10 | clap-noun-verb-zeroconfig-pack | cargo build timed out after 120s manifest=consumer/Cargo.toml |
| 11 | cnv-any-manifest-pack | cargo build timed out after 120s manifest=consumer/Cargo.toml |
| 12 | cyberpunk-tv-platform | cargo build timed out after 120s manifest=wasm/Cargo.toml |
| 13 | ggen-combinatorial-maximalism-pack | cargo build timed out after 120s manifest=cmd-cell/Cargo.toml |
| 14 | mfw-pcp-level5-pack | cargo build timed out after 120s manifest=mfw-pcp-generated/Cargo.toml |
| 15 | otel-weaver-ocel-pack | cargo build timed out after 120s manifest=generated/Cargo.toml |
| 16 | qri-qualification-profile-pack | cargo test timed out after 120s manifest=adapter/Cargo.toml |
| 17 | rust-pack | cargo test timed out after 120s manifest=consumer/Cargo.toml |

Reason-drift note: 2 of the 10 are packs zd-52 already typed with *different* causes
(clap-noun-verb-crate-pack: E0583 → timeout; otel-weaver-ocel-pack:
dependency-requires-nightly → timeout) — same pack, drifted reason, still non-blocking
WARN; the 8 remaining are new WARN packs (were ALIVE at the last baseline record).

**SKIPPED (1):** tcps-pack, `SKIPPED:GGEN_PACK_GENERATED_BUILD_NEEDS_WORKSPACE_ROOT`,
class `harness-limitation` (zd-52 row, unchanged).

## Environment-wedge evidence chain (why the 10 timeout rows are not pack regressions)

1. Solo re-runs (`--pack rust-pack --pack clap-noun-verb-schema-pack --pack
   qri-qualification-profile-pack`) also time out at 120s → not full-run contention only.
2. rust-pack consumer `cargo test` in a manually-prepared capsule **passes in seconds**
   with a normal environment (witnessed 11:38; `Finished 'test' profile in 1.46s` after
   deps compiled).
3. The same command under the court's redirected-HOME env **hangs**; the hung process
   is the *test binary* itself stuck at `_dyld_start` (sample of pid 71571: 10+ min,
   0% CPU, never reaches main).
4. **System-level wedge witnessed**: a freshly-compiled trivial clang binary
   (`int main(){return 0;}`) hangs at exec (rc=124); a *copied* `/bin/echo` blocks;
   a binary built at 11:04 in ~/ggen/target/debug hangs; system binaries (/bin/echo,
   /usr/bin/true, ggen, python3) run fine. syspolicyd at 98-100% CPU. Wedge onset
   ~11:40 (the 11:38 run was healthy).
5. A 600s-bound diagnostic re-run of rust-pack still timed out (`cargo test timed out
   after 600s`) → not slow-but-completing builds.
6. `sudo -n killall syspolicyd` → `sudo: a password is required` (rc=1) →
   **BLOCKED:syspolicyd-sudo** for remediation. Wedge still active at receipt write
   (clang probe rc=124; syspolicyd 100.2%).

## Baseline transition (typed, never silent)

- `python3 scripts/warn_ratchet.py baseline /tmp/warn1-report.json` → re-record
  338/0/1/9 → 330/0/1/17; then a mechanical annotation pass (python3 json round-trip,
  sort_keys/indent=2 preserved): every WARN entry gets `warn_class` (7 ratchet-residue,
  10 environment-wedge) + `annotation` slug; tcps-pack SKIPPED gets
  `harness-limitation`; top-level `provenance` field added citing this recount, the
  syspolicyd evidence chain, and this receipt path.
- Close condition (recorded in the provenance field): rerun on a healthy system.
  Recovery of the 10 timeout rows to ALIVE is a lawful ratchet improvement — re-record
  then. If they remain WARN on a healthy system, they are genuine >120s cold-build
  packs — reclassify then.
- Registered limitation (not fixed here): `warn_ratchet.py project()` drops
  `warn_class`/`annotation`/`provenance` on the next re-record — the same rot channel
  that erased zd-52's typing. Mechanical re-annotation is required after every
  re-record until the projection carries annotations through.

## Verify commands / exits

1. `python3 scripts/qualify_packs.py --report /tmp/warn1-report.json` → exit 0,
   330 ALIVE / 17 WARN / 0 REFUSED / 1 SKIPPED (all 18 non-ALIVE rows typed)
2. `python3 scripts/warn_ratchet.py check /tmp/warn1-report.json` → **exit 0**,
   `ratchet ok counts={"ALIVE": 330, "REFUSED": 0, "SKIPPED": 1, "WARN": 17}`
3. `python3 -m json.tool qualification/baseline.json` → exit 0
4. `git diff --stat scripts/qualify_packs.py` → empty (diagnostic patch reverted);
   owned-diff inventory: `qualification/baseline.json` (M) +
   `docs/jira/v26.11.4/receipts/warn1-baseline-reconcile.md` (new) only
5. Confirmation re-qualify (`--workers 6 --report /tmp/warn1-confirm.json`) → exit 0,
   **identical counts** 330 ALIVE / 17 WARN / 0 REFUSED / 1 SKIPPED, zero per-pack
   status changes vs run 1; `python3 scripts/warn_ratchet.py check
   /tmp/warn1-confirm.json` → **exit 0**, `ratchet ok counts={... WARN: 17}`

## Standing

PARTIAL_ALIVE: all 18 non-ALIVE rows typed, both full-corpus runs exit 0 with 0 REFUSED
and identical counts (reproduced), ratchet check exit 0 against both reports. Close
condition for the 10 environment-wedge rows is BLOCKED:syspolicyd-sudo — the macOS
syspolicyd exec-policy wedge is fleet-wide (every locally-built binary exec-blocks, so
other lanes' cargo gates are degraded too); remediation needs an interactive
`sudo killall syspolicyd` (launchd restarts it; non-interactive sudo unavailable).
