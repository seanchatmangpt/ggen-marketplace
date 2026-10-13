# BACKLOG — v26.10.8 unfixed findings (dispatch-ready)

Generated 2026-10-13 from session UNFIXED findings, each re-verified on disk.
Format: `[ID] [rank] [size] [repo] — finding | fix sketch | verify: <cmd> | deps: <IDs>`.
Lanes must re-verify before dispatch; a fixed finding should be closed with a receipt, not silently skipped.

## GATED (blocked on external authority — not briefs, no lane dispatch)

- knhk merge (awaiting merge authority)
- strata kg-42 merge (awaiting merge authority)
- castle push transport (no push authority this session)
- castle-bridge regen (depends on castle push)
- wasm rotation (allowlist expires 2026-10-20 — 7 days)
- ecosystem lock refresh (after merges land)
- xaas v26.9.23 courts decision (operator decision pending)

## HIGH (CI-breaking / court-defeating / real defect)

- [BL-01] [HIGH] [M] [erlmcp] live code calls `.broken` modules: `erlmcp_server.erl:3150` calls `erlmcp_prompt_argument_validator:validate_prompt_arguments/3` but only `apps/erlmcp_core/src/erlmcp_prompt_argument_validator.erl.broken` exists; `erlmcp_schema_registry.erl:100,171` pools `erlmcp_schema_validator` whose only source is `.broken` | repair or restore the two modules from `.broken` (or stub with explicit `REFUSED:broken-module`), never delete the callers blindly | verify: `grep -n "prompt_argument_validator\|erlmcp_schema_validator" apps/erlmcp_core/src/erlmcp_server.erl apps/erlmcp_core/src/erlmcp_schema_registry.erl && find apps -name "*.broken" -path "*src*" | xargs grep -L module` | deps: none
- [BL-02] [HIGH] [M] [erlmcp] `erlmcp_uri_validator` duplicate-module ambiguity: live copy at `apps/erlmcp_validation/src/erlmcp_uri_validator.erl`, dead `.broken` twin at `apps/erlmcp_core/src/erlmcp_uri_validator.erl.broken`, and `erlmcp_server.erl:406,446` (erlmcp_core) calls it cross-app | keep the erlmcp_validation copy as the single authority, delete the `.broken` twin, declare the cross-app dep explicitly in rebar | verify: `find apps -name "erlmcp_uri_validator*" -not -path "*_build*"` | deps: BL-01
- [BL-03] [HIGH] [M] [erlmcp] metrics_collector boot crash root cause: `apps/erlmcp_observability/src/erlmcp_metrics_collector.erl` init/1 (line 176) crashes on boot per session findings | reproduce in shell, fix init path (likely missing table/pool dependency on erlmcp_core), add a boot smoke court | verify: `erl -pa _build/*/lib/*/ebin -eval "erlmcp_metrics_collector:start_link(1000), halt(0)"` exits 0 | deps: none
- [BL-04] [HIGH] [M] [erlmcp] transports undef residue: stray top-level `apps/erlmcp_transport_sse.erl` / `apps/erlmcp_transport_ws.erl` duplicate the real modules under `apps/erlmcp_cli/src/`, producing undef/duplicate-module residue in test runs | delete the two stray top-level copies, keep erlmcp_cli/src as canonical, re-run transport suites | verify: `ls apps/erlmcp_transport_sse.erl apps/erlmcp_transport_ws.erl 2>&1` → both absent | deps: none
- [BL-05] [HIGH] [M] [erlmcp] validation races (root-cause 3): concurrent registry/pool validation races reported by session courts; serialize or partition the poolboy validation path and add a concurrency court | fix in erlmcp_core schema_registry worker path | verify: re-run the failing validation suite 3x, zero flakes | deps: BL-01
- [BL-06] [HIGH] [S] [ferroplan] ci_gen/ggen.lock stale: `scripts/ci_gen/ggen.lock` pins `github-actions-pack` at `blake3:e20e7b3b…` while current pack hash is `22d738b2`-class — version/content court will refuse | re-run `ggen sync` against the current marketplace checkout and commit regenerated lock | verify: `cat scripts/ci_gen/ggen.lock` hash equals recomputed pack hash | deps: none
- [BL-07] [HIGH] [S] [ferroplan] wasm pin re-mint: contract wasm pin minted 2026-10-06 predates current wasm build (`6a6fae53`); Justfile wasm court (`snap()`/wasmSha256 compare) will fail | rebuild wasm32-wasip1 release and re-mint `wja:wasmSha256`/`wasmBytes` in `crates/ferroplan-wasm/ontology/contract.ttl` | verify: `just` wasm court target exits 0 | deps: none
- [BL-08] [HIGH] [S] [ash_a2a] trybuild expects-fail drift UNVERIFIED-LOCATION: session reported 9 `compile_fail` UI cases now compile (expects-fail asserts fail); trybuild/compile_fail corpus not located in ash_a2a, a2a-rs, ggen crates this pass | locate the corpus (likely `tests/ui/` in a Rust consumer), invert each stale `//~ERROR` expect or restore the denied pattern, re-run trybuild | verify: `grep -rln "compile_fail" <repo>/tests | head` then `cargo test trybuild` | deps: none

## MEDIUM (drift)

- [BL-09] [MEDIUM] [S] [castle] generated `docs/reference/generated/reference.md` stale for 3 deleted modules | re-run the doc regen so per-module tables match current crates | verify: `grep -c "<deleted-module>" docs/reference/generated/reference.md` → 0 | deps: GATED castle-bridge
- [BL-10] [MEDIUM] [S] [castle] ISO20022 official-XSD tests env-dependent: `tests/payments_iso20022_official.rs:17` reads `CASTLE_ISO20022_XSD_DIR` (fails loudly when absent) | vendor the pinned XSDs or wire the env var in CI so the court runs everywhere identically | verify: `CASTLE_ISO20022_XSD_DIR=<pinned> cargo test --test payments_iso20022_official` green; CI config references the var | deps: none
- [BL-11] [MEDIUM] [S] [ash_a2a] lib compile warnings: AgentCard struct-update warning + duplicate `dispatch/4` vs `dispatch/5` in `lib/ash_a2a/dispatcher.ex` (dispatch/5 is the live auth-threaded signature per module docs) | rename/remove the dead dispatch/4 clause, fix the struct-update syntax, zero-warning court | verify: `mix compile --warnings-as-errors` | deps: none
- [BL-12] [MEDIUM] [S] [beam4pm] ash_a2a hex-publish cap: `mix.exs:107-120` — BEAM4PM_HEX_PUBLISH swaps git-pin→hex only when ash_a2a 26.9.30+ is on Hex; publish remains blocked upstream | publish ash_a2a to Hex (or re-pin to whatever Hex has), then flip BEAM4PM_HEX_PUBLISH path in CI | verify: `mix hex.info ash_a2a` shows >= 26.9.30; `BEAM4PM_HEX_PUBLISH=1 mix deps.resolve` ok | deps: GATED ecosystem lock refresh
- [BL-13] [MEDIUM] [S] [beam4pm] dep-pin skew (corrected): mix.lock actually carries `ash_affidavit 26.10.1`, not 26.6.22 as session memory claimed — still behind the 26.10.6 fleet line | run the fleet pin-skew sweep (all beam4pm hex deps vs fleet latest), bump in one dependency-closed commit | verify: `grep ash_affidavit mix.lock` shows 26.10.6-class version | deps: BL-12
- [BL-14] [MEDIUM] [S] [erlmcp] cover instrumentation broken (root-cause 4): cover/coverage tooling fails over the multi-app layout | fix rebar cover config for multi-app dirs, add cover court to CI | verify: `rebar3 cover` produces index across all apps, exit 0 | deps: BL-04

## LOW (hygiene)

- [BL-15] [LOW] [S] [ggen] stale comment `Cargo.toml:988` claims wasm4pm/wasm4pm-compat use `#![feature]`/nightly and need redirects — description drifted from current crates | rewrite comment to match current wasm4pm-compat = "26.8" reality at line 185 | verify: `sed -n '185p;985,992p' Cargo.toml` consistent | deps: none
- [BL-16] [LOW] [S] [ggen] `crates/ggen-lsp/Cargo.toml:48` path-dep on ggen-engine carries stale `version = "26.7.13"` (crate is publish=false so version is documentation only) | bump to current workspace version or drop the version field | verify: `grep -n "ggen-engine =" crates/ggen-lsp/Cargo.toml` matches workspace version | deps: none
- [BL-17] [LOW] [S] [ash_pplan] `_build-jrp/` debris, 381 MB orphaned lane build root at `/Users/sac/ash_pplan/_build-jrp` | delete after confirming no lane lease references it (lane-build-root cleanup law) | verify: `ls -d /Users/sac/ash_pplan/_build-jrp` → absent, `mix test` still green | deps: none

## Excluded after on-disk verification

- `/tmp lane-target leftovers` — `/tmp/lane-target*` not found; already cleaned. No row.
- `beam4pm→affidavit 26.6.22` — fact corrected to 26.10.1 (see BL-13); original claim not enqueued as written.
