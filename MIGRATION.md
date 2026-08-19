# Initial ggen pack extraction receipt

The marketplace began by extracting the complete `packs/` subtree from the ggen monorepo without editing the imported bytes. This file is a **historical migration receipt**. It records what was observed at each migration epoch; it is not the current pack contract, current marketplace version, or current Level-5 standing. For current law, use `AGENTS.md`, `marketplace.toml`, and `docs/reference/**`.

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

The exact import intentionally preceded marketplace cleanup so provenance and modernization were not conflated. The first exhaustive marketplace validator then surfaced historical corpus debt.

Three source directories were excluded from the published marketplace because their own READMEs established that they were not live reusable packs:

- `sbb-capability-density-pack` — explicitly `ORPHANED / SUPERSEDED`, zero consumers, with its README prescribing deletion;
- `vision-2030-phase-change-pack` — explicitly `ORPHANED — zero consumers`, not compatible with the live Vision 2030 CLI input shape;
- `rust-dialect-pack` — explicitly experimental, not wired into `ggen sync`/CI, and contained no `pack.toml`.

Five live packs had valid names/versions but missing descriptions; their descriptions were repaired from each pack's own README rather than invented from outside context.

The marketplace validator also learned the observed corpus packaging shapes: `.tera` and `.tmpl` template sources, project packs with RDF under `ontology/`, semantic packs without templates, and dotfile scaffolding such as `.gitkeep`. That marketplace observation must not be confused with the real ggen loader's manifest schema. Current loader/marketplace compatibility law is documented in [`docs/reference/pack-contract.md`](docs/reference/pack-contract.md); do not infer that arbitrary `[pack]` extension keys are accepted by ggen merely because a lenient catalog parser can inspect them.

The historical source-tree identity remains the extraction receipt; subsequent admission commits establish the curated marketplace state.

## 2026-08-10 second-wave extraction (10 packs, three source repositories)

A local filesystem search across the maintainer's machine found 34 real, non-duplicate ggen pack candidates outside this marketplace. Ten were selected by richness (ontology depth, `sparql:`-driven template coverage, real domain grounding) and copied byte-for-byte, excluding any candidate whose design depended on a symlink to its source repository's own files. The marketplace contract refuses symlinks under `packs/`, so those candidates were excluded rather than imported as stale snapshots that silently lost their source-link guarantee.

Bound identities at copy time (each source repository's own `HEAD`, working tree clean at the copied paths — verified via `git status --porcelain` before copying):

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

`~/praxis` and `~/ggen-legacy` were local working repositories at the migration epoch. The commit SHAs above bind the exact source identity observed in those repos; they are not a claim that those historical local paths remain publicly fetchable.

No content was edited during the copy. Each pack was then admitted by the marketplace validator unchanged (94 packs total at that historical epoch) and composed with the then-current `pack-maturity-pack` to exercise its generic `l5p:cap03`/`cap04`/`cap09` mechanics.

That result was **not** a global Level-5 crown for those packs. It established only the generic mechanical boundaries that `pack-maturity-pack` could prove for those exact migration subjects. Current Level-5 promotion requires the seven-dimensional closure and Diátaxis correspondence defined in [`docs/reference/level5-maturity-contract.md`](docs/reference/level5-maturity-contract.md).

## Post-migration class closure

As the marketplace grows, future migrations should avoid converting every imported project/profile into a new independent semantic authority. After byte/provenance preservation is receipted, modernization may classify imported packs as kernels, capabilities, profiles/worlds, compatibility surfaces, evidence packs, release-control packs, or umbrellas.

Consolidation is a **separate transition** from migration. Before removing or merging source, prove semantic equivalence/supersession, target ownership compatibility, admission/refusal correspondence, consumer migration, and authority non-escalation. See:

- [`docs/reference/pack-classes.md`](docs/reference/pack-classes.md)
- [`docs/how-to/consolidate-a-pack-family.md`](docs/how-to/consolidate-a-pack-family.md)
- [`docs/explanation/class-closure-and-consolidation.md`](docs/explanation/class-closure-and-consolidation.md)

This preserves the core migration principle: exact provenance first, lawful modernization second.
