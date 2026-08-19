# Agent instructions — ggen Marketplace

## Mission

Preserve this repository as the canonical, reviewable corpus of reusable ggen pack source. Prefer deterministic manufacture, fail-closed validation, exact-subject evidence, and class closure over duplicated metadata, duplicated semantic authority, or generated-output ownership.

## Source hierarchy

1. `marketplace.toml` declares marketplace operational law and must be admitted through `star-toml` before installer/qualification execution.
2. `packs/<name>/pack.toml` declares pack identity.
3. `packs/<name>/**/*.ttl` carries admitted semantic facts.
4. templates/project rules project those facts.
5. `gates/` may refuse invalid facts before generation.
6. pack/project `ggen.toml` files remain ggen generation contracts; they are not the marketplace control plane.
7. `docs/book.ttl` is the canonical mdBook navigation source; generated `docs/SUMMARY.md`/`book.toml` are projections, not editing surfaces.
8. consumer outputs are generated consequences and do not belong here unless they are explicit pack source fixtures.

## Required discipline

- Work on a purpose branch; do not write directly to `main`.
- Keep pack directory name identical to `[pack].name`.
- Do not hand-maintain a second catalog. Use `python3 scripts/marketplace.py catalog`.
- Do not introduce `generated/` as a source namespace for marketplace metadata.
- Do not use symlinks under `packs/`; marketplace packs must be self-contained and path-safe.
- Do not let CI rewrite or push pack corrections. PR CI is read-only evidence.
- Do not duplicate ggen release versions, release commits, platform asset names, SHA-256 digests, qualification worker counts, or timeout bounds in shell/Python/docs. They belong in `marketplace.toml` and become executable only after `star-toml` admission.
- Keep Diátaxis categories distinct: tutorials teach, how-to guides solve tasks, reference specifies, explanation develops understanding.
- Preserve exact provenance when moving pack source between repositories.
- Treat packaging profile (`projection|semantic|project`) separately from semantic class (`Kernel|Capability|Profile|World|Compatibility|Evidence|ReleaseControl|Umbrella`).
- Consolidate duplicated semantic/protocol/lifecycle/projection law into canonical classes/kernels; preserve non-equivalent domain worlds, runtimes, and compatibility seams until equivalence/migration is proved.
- Never infer Level 5 from pack existence, generated docs, CI metadata, or one green court.

## Level-5 discipline

Level 5 is closure over seven independently evidenced dimensions:

1. semantic source;
2. admission;
3. manufacture;
4. execution;
5. receipt/replay;
6. authority fencing;
7. composition/class closure.

Level-5 documentation additionally requires Tutorial + How-to + Reference + Explanation correspondence to the same contract.

`pack-maturity-pack` may supply generic fixed-point, receipt, and Diátaxis infrastructure. It must not manufacture missing domain semantics, negative witnesses, consumer runtime results, external observations, or DO authority.

Before promoting a pack, read `docs/reference/level5-maturity-contract.md`. Before merging/deleting overlapping packs, read `docs/reference/pack-classes.md` and `docs/how-to/consolidate-a-pack-family.md`.

## Authority

Preserve SELECT / CONSTRUCT / DO separation. Marketplace admission and ggen manufacture may construct artifacts/intents but do not grant consequential execution authority. When a consumer uses BRCE, it remains the separately admitted DO path.

Documentation, semantic derivation, planner output, generated files, proofs, hooks, and receipts have no ambient actuation authority.

## Validation

Run before publication:

```bash
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
python3 scripts/marketplace.py fingerprint
GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json \
  bash scripts/qualify-marketplace.sh \
  /tmp/ggen-marketplace-admitted.json \
  /tmp/ggen-marketplace-qualification.json
```

`marketplace.toml` is raw observation until `star-toml` admits it with a witness. A green marketplace validator proves the repository contract only. All-pack qualification proves bounded ggen load/manufacture/replay for the exact subject it executes. Consequential pack behavior must additionally be exercised at the matching real consumer/runtime boundary when that behavior is claimed.

## Standing

Use `UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE`, `BLOCKED`, `BUILD_BROKEN`, `UNSUPPORTED`, plus typed `REFUSED:*`. A workflow is not a successful run; a generated artifact is not authority; historical success at another SHA does not transfer without identity/equivalence proof.
