# v26.10.8 — Landing Batch 3 Receipt

Batch of two commits landed in `ggen-marketplace` under the v26.10.8 campaign,
plus witnessed browser-court evidence and the coordinator's symlink-residue
cleanup. Each row verified via `git show --stat` / `git log` at receipt time
(2026-10-08).

## Commits

| SHA (full) | Subject | Pathspec | Notes |
|---|---|---|---|
| `0ba8cb01ba7ba2435518139a7e519b3bba91ca32` | chore(release): v26.10.8 marketplace version bump (fleet campaign) | `marketplace.toml` (+1/−1), `docs/reference/release-v26.10.8.md` (+31, new) | `version = "v26.10.2"` → `"v26.10.8"`. **Skip-from lawfulness**: v26.10.7 exists as a git tag only (no version-bump commit); `git tag -l 'v26.10*'` → v26.10.1, v26.10.2, v26.10.7. Monotonic gate intact. |
| `7b848d2db7002b377c36ca2ea24f2f4880f73f43` | docs(sjira): v26.10.8 landing batch 2 receipt | `docs/sjira/v26.10.8/LANDING-BATCH-2.md` (+45, new) | Docs-only; batch-2 court outputs recorded therein. |

**Omitted**: `a02d45248c867e3f1cc9edb59936fb113cdd677e` (campaign runbook seed +
landing batch 1 receipt) — already receipted in
`docs/sjira/v26.10.8/LANDING-BATCH-1.md` and as a row in LANDING-BATCH-2.md;
not re-receipted here.

## Browser-court evidence (witnessed)

- **SEMANTIC_NEXTJS_PLAYWRIGHT_ALIVE**: 1/1 passed — real `ggen sync` → real
  Next.js build → real Chromium (Playwright). Standing **ALIVE**.
- **nasa-dark-mode headless WebGL2 court**: exit 0, standing **ALIVE**;
  receipt-chain 10/10; `deckGlRuntime` = `BLOCKED_DEPENDENCY_TRANSPORT`
  (pre-existing transport dependency, disclosed, not introduced by this batch).

## Coordinator cleanup (witnessed)

- `generated/frontend/node_modules` symlink residue removed from the checkout.
- **Validate re-witnessed post-cleanup** (2026-10-08, this lane):
  `python3 scripts/marketplace.py validate` → exit 0,
  `validated packs=306 manifests=306 ontologies=504 templates=1837
  native_gates=1868 verifier_gates=21
  profiles={project:101,projection:159,semantic:46} diataxis=20`.
  The batch-2 `REFUSED:PACK_SYMLINK` working-tree caveat is closed for this
  residue source.

## Open items (disclosed)

- **ggen identity plurality**: CI pins ggen **26.9.12**; ambient ggen on PATH
  is **26.9.28**. C20 (generator-plurality court, double-compile identity
  agreement) is the standing falsifier for this skew; unresolved.
- `.tool-versions` still untracked in the checkout (uncommitted).
- `packs/semantic-fullstack-factory-pack/qualification/generated/` remains
  untracked (present in no commit); validate passes with it present.
