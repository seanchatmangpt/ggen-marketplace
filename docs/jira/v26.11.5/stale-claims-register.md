# Stale-Claims Register — ggen-marketplace

Standing: PARTIAL — 7/8 rows verified on disk this session; row 4c (baseline `ggen_version` re-read) UNVERIFIED, disclosed per-row.

Census date: 2026-11-05. Source docs NOT edited; packs/, scripts/ untouched; nothing committed. All observed states re-read on disk this session with commands cited. Each row's close condition names the later decision — this register only census, no fixes.

## 1. `docs/context/ggen-pin-bump.pending.md` (whole file; mtime 2026-10-13, last commit 325569eca)

- **Claim**: "Status: BLOCKED. Execute when the v26.10.5 release lands."
- **Observed**: already self-superseded in-file — header banner (2026-10-13) reads "SUPERSEDED 2026-10-13 ... the marketplace repo has since released v26.10.8 while the upstream `[ggen]` pin remains `v26.8.11`". Confirmed `marketplace.toml:36` still `version = "v26.8.11"`; the pin never moved. v26.10.5 artifacts remain the gating condition that never arrived.
- **Close**: re-derive pin-bump steps from current `marketplace.toml` + actual v26.10.x artifacts; then archive/delete the note. Until then the body's BLOCKED status is inert (superseded by its own banner).

## 2. `docs/context/next.md` (whole file; mtime 2026-10-08, last commit 3a5758710 2026-10-05)

- **Claim**: entire file is v26.10.5-era — "Release Target: v26.10.5", branch `feat/aaif-gcp-roadmap-v26.10.5`, HEAD `907053ab1`, "all 20 waves committed — FINAL".
- **Observed**: repo has since released v26.10.8 → v26.11.3 → current v26.11.5 cycle (CHANGELOG top section `[v26.11.3] — 2026-11-04`). Branch/HEAD/phase table point at a milestone two-plus releases old. File says "FINAL" but no successor handoff ever replaced it.
- **Close**: replace with a current-cycle handoff, or archive under `docs/context/archive/`. Until replaced, treat `next.md` as historical, not the live frontier.

## 3. `docs/sjira/v26.10.8/BACKLOG.md:11-17` (GATED section)

- **Claim**: 7 items "blocked on external authority — not briefs, no lane dispatch"; `:13` "wasm rotation (allowlist expires 2026-10-20 — 7 days)".
- **Observed**: allowlist expiry 2026-10-20 is 16 days past (today 2026-11-05). The 7 items (knhk merge, strata kg-42 merge, castle push transport, castle-bridge regen, wasm rotation, ecosystem lock refresh, xaas v26.9.23 courts decision) — per-item current authority status unre-verified this session; the expiry clock is definitively expired.
- **Close**: re-pull the 7 items' current authority status; mint a fresh BACKLOG for the current cycle. Allowlist extension is an operator decision.

## 4. `docs/jira/v26.11.3/closure/marketplace-closure.md:73-76` + `CHANGELOG.md:14`

- **Claim**: "Tags unminted: no v26.11.3 tag minted on this repo (CHANGELOG carries the `[v26.11.3] — 2026-11-04` section; the tag does not exist)."
- **Observed**: still true — `git tag | grep 26.11.3` → 0 matches. `CHANGELOG.md:14` carries `[v26.11.3] — 2026-11-04`. The closure doc's claim is current, not stale; the stale surface is CHANGELOG publishing a version whose tag never existed.
- **Close**: mint the v26.11.3 tag on the closure commit, or amend the CHANGELOG header to record the tag was never minted. Operator decision.

### 4c. Adjacent BLOCKED item, same closure doc (:77-81)

- **Claim**: `qualification/baseline.json` `ggen_version` reads `"ggen 26.10.11"` while ambient court is 26.11.3.
- **Observed**: UNVERIFIED this session — not re-read on disk in this lane's sweep.
- **Close**: re-read `qualification/baseline.json` at next seal; restamp mechanically on next full-corpus re-projection.

## 5. `docs/superpowers/plans/2026-08-15-adversarial-review.md`

- **Claim**: 11 unchecked `- [ ]` plan steps (lines 45, 197, 203, 222, 289, 307, 316, 322, 332, 340, 346; `grep -c "^- \[ \]"` → 11).
- **Observed**: deliverable already on disk — `.claude/skills/adversarial-review/` contains `SKILL.md` + `workflow.js`. The plan asserts pending work that is delivered; it is a stale execution artifact, not a pending obligation.
- **Close**: check the boxes off with a delivered note, or archive the plan with "delivered-elsewhere". Later decision.

## 6. `marketplace.toml:12` vs `marketplace.active.toml:2`

- **Claim**: version divergence — `marketplace.toml` `version = "v26.10.8"`; `marketplace.active.toml` `version = "26.10.7"`.
- **Observed**: both read directly on disk. Divergence real, and includes a format difference (v-prefix vs none). Whether the two version fields are independent axes (repo-release vs active-set-snapshot) or one should track the other: UNVERIFIED — no doc found this session declaring their relationship.
- **Close**: re-read both tomls plus any doc declaring their relationship; then bump active to current or document intentional divergence. Later decision.

## 7. `README.md:9` — pack count

- **Claim**: "As of 2026-11-04 the corpus is 347 packs" citing `ls -d packs/*/` as its own re-verify command.
- **Observed**: same command run today → **348**. The README contradicts its own cited verification method post-seal pack churn.
- **Close**: re-run the README's own command and restamp (348 as of 2026-11-05) at next README touch.

## 8. `docs/pack-consumer-contract.md:89`

- **Claim**: "This is the lawful target for F1/F2/F3 packs' helper templates; it is NOT yet landed in any of the four packs."
- **Observed**: same-day claim (2026-11-05, in-flight v0.2.0 consumer-contract wave) — not stale today, but time-sensitive: once the wave lands the `import { cn } from "cn"` helper change, line 89 becomes false.
- **Close**: at wave seal, grep the four packs' helper templates for the landed form; update line 89 on landing.

---
*Disclosure: first Write of this register was mid-generation-corrupted (garbled table rows + phantom prose); this file is the clean rewrite. Nothing else touched.*
