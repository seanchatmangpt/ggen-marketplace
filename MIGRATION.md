# Initial ggen pack extraction receipt

The marketplace began by extracting the complete `packs/` subtree from the ggen monorepo without editing the imported bytes.

## Bound identities

- source repository: `seanchatmangpt/ggen`
- source commit: `c37b46015b8e5ab40be771d61aafe3d7c7af084c`
- source root tree: `b592334147fe46964a50b0e3f83df45fa7f62a30`
- source `packs/` tree: `4d70ae027004db829a8c334d201ad8e4f5b75ce1`
- destination repository: `seanchatmangpt/ggen-marketplace`
- destination initial base: `40a17c2e24a04b5bb2d66f6a0a30d12a8611cb2d`
- purpose branch: `agent/seed-ggen-marketplace`

## Migration actuation

A one-shot GitHub Actions workflow checked out the source repository at the exact source SHA, asserted `HEAD` identity, copied `packs/` byte-for-byte, and committed the result to the purpose branch.

- workflow run: `31304289256`
- job: `93222025172`
- import commit: `adb908cd6b55cf18bfcd83fc2c9a9213010dacf2`
- one-shot actuator removal commit: `70c985de72bea9a1e24df269d62d85cd880da124`

The permanent repository does not retain the write-enabled migration workflow.

## Strong correspondence proof

After import, the destination `packs/` Git tree was `4d70ae027004db829a8c334d201ad8e4f5b75ce1`, exactly equal to the source `packs/` tree at the admitted source commit. This proves subtree identity for the migration without relying on a file-count heuristic.

## Post-import admission repair

The exact import intentionally precedes marketplace cleanup so provenance and modernization are not conflated. The first exhaustive marketplace validator then surfaced historical corpus debt.

Three source directories are excluded from the published marketplace because their own READMEs establish that they are not live reusable packs:

- `sbb-capability-density-pack` — explicitly `ORPHANED / SUPERSEDED`, zero consumers, with its README prescribing deletion;
- `vision-2030-phase-change-pack` — explicitly `ORPHANED — zero consumers`, not compatible with the live Vision 2030 CLI input shape;
- `rust-dialect-pack` — explicitly experimental, not wired into `ggen sync`/CI, and contains no `pack.toml`.

Five live packs had valid names/versions but missing descriptions; their descriptions were repaired from each pack's own README rather than invented from outside context.

The validator also learned the actual corpus contract: `.tera` and `.tmpl` are both template sources, project packs may keep RDF under `ontology/`, semantic packs need not contain templates, `.gitkeep` is scaffolding rather than executable content, and manifests may carry pack-specific extension tables in addition to `[pack]`.

The historical source-tree identity remains the extraction receipt; subsequent admission commits establish the curated marketplace state.

## 2026-08-10 second-wave extraction (10 packs, three source repositories)

A local filesystem search across the maintainer's machine found 34 real, non-duplicate ggen
pack candidates outside this marketplace. Ten were selected by richness (ontology depth,
`sparql:`-driven template coverage, real domain grounding) and copied byte-for-byte, excluding
any candidate whose design depends on a symlink to its source repository's own files (this
marketplace's pack contract refuses symlinks under `packs/` — see
[`docs/reference/pack-contract.md`](docs/reference/pack-contract.md) — so `gymact-bridge-pack`,
`multicloud-gym-pack`, and `otel-weaver-pack` were excluded rather than imported as stale
snapshots that silently lose their "always the same file as the source" guarantee).

Bound identities at copy time (each source repository's own `HEAD`, working tree clean at the
copied paths — verified via `git status --porcelain` before copying):

| Pack | Source repository | Source commit |
|---|---|---|
| `nextjs-ai-sdk-pack` | `seanchatmangpt/ggen` (`examples/nextjs-ai-sdk/pack`) | `657a0befbd331be7c6c7da3dbe23b153342c1c8e` |
| `lean-math-pack` | `~/praxis` (`packs/lean-math-pack`) | `bc1272b2605a66d3efaa7a5ab11a5f49e96d67c3` |
| `chatman-engine-pack` | `~/praxis` (`packs/chatman-engine-pack`) | `bc1272b2605a66d3efaa7a5ab11a5f49e96d67c3` |
| `post-release-pack` | `~/praxis` (`packs/post-release-pack`) | `bc1272b2605a66d3efaa7a5ab11a5f49e96d67c3` |
| `quadrature-pack` | `~/praxis` (`packs/quadrature-pack`) | `bc1272b2605a66d3efaa7a5ab11a5f49e96d67c3` |
| `soc2-audit-pack` | `~/praxis` (`packs/soc2-audit-pack`) | `bc1272b2605a66d3efaa7a5ab11a5f49e96d67c3` |
| `togaf-adm-pack` | `~/praxis` (`packs/togaf-adm-pack`) | `bc1272b2605a66d3efaa7a5ab11a5f49e96d67c3` |
| `dry-run-publish-pack` | `~/praxis` (`packs/dry-run-publish-pack`) | `bc1272b2605a66d3efaa7a5ab11a5f49e96d67c3` |
| `azure-terraform-pack` | `~/praxis` (`packs/azure-terraform-pack`) | `bc1272b2605a66d3efaa7a5ab11a5f49e96d67c3` |
| `ggen-legacy-assurance-pack` | `~/ggen-legacy` (`packs/ggen-legacy-assurance-pack`) | `982fea0a476ae7c74d2c31ab876650bdae1bd6d4` |

`~/praxis` and `~/ggen-legacy` are local-only working repositories (not GitHub remotes this
document can point a reader at); the commit SHAs above are the exact, reproducible bound
identity at copy time within those local repos, in the same spirit as this file's own initial
extraction receipt above, not a claim that they're publicly fetchable.

No content was edited during the copy. Each pack was then admitted by
`python3 scripts/marketplace.py validate` unchanged (94 packs total post-import) and composed
with `pack-maturity-pack` in a real consumer to verify `l5p:cap03`/`cap04`/`cap09` — see each
pack's own `pack.toml` for its specific maturity disclosure.
