# 01 Ticket Retire Clap Noun Verb Legacy

Standing: PARTIAL_ALIVE (see `00-PACK-PORTFOLIO-MATURITY-AUDIT.md`). This ticket does not require ticket 03's consolidation-court methodology because it retires a pack from *discovery*, not from disk — no merge, no delete.

## Quick reference

- Target: `packs/clap-noun-verb-pack`
- Action: remove from normal marketplace discovery/catalog listing; keep the directory and its content on disk as a compatibility lookup.
- Verified successors (named by the pack itself): `clap-noun-verb-schema-pack`, `clap-noun-verb-crate-pack`, `clap-noun-verb-routing-pack`, `clap-noun-verb-behavior-pack`, `clap-noun-verb-boundary-pack`, `clap-noun-verb-verification-pack`.

## Evidence for this ticket

`packs/clap-noun-verb-pack/pack.toml` states, in the pack's own words: "DEPRECATED. Superseded by clap-noun-verb-schema-pack, clap-noun-verb-crate-pack, clap-noun-verb-routing-pack, clap-noun-verb-behavior-pack, clap-noun-verb-boundary-pack, and clap-noun-verb-verification-pack." This is a self-declared, file-level fact — directly verified, not inferred.

All six named successor directories exist on disk under `packs/`.

Separately, `clap-noun-verb-specimen-pack` and `clap-noun-verb-zeroconfig-pack` also exist and are related to this family (specimen/fixture and umbrella roles respectively per the source audit), but neither is self-declared deprecated by `clap-noun-verb-pack`'s own text, so this ticket does not fold them in — they are out of scope here.

## What "retire from normal discovery" means

- `packs/clap-noun-verb-pack` stays on disk (provenance and compatibility).
- `scripts/marketplace.py catalog` output should mark it non-default/deprecated rather than silently continuing to list it as a first-class equal to the six successor packs. Exact mechanism (a `deprecated = true` marker respected by `catalog_record()`, or a documented exclusion list) is an implementation decision for whoever picks up this ticket — this ticket specifies the acceptance criteria, not the code.
- Existing consumers pinned to `clap-noun-verb-pack` by path must continue to resolve (no breaking their `ggen.toml`).

## Acceptance criteria

1. `python3 scripts/marketplace.py validate` continues to pass with `clap-noun-verb-pack` present on disk.
2. `python3 scripts/marketplace.py catalog` output marks `clap-noun-verb-pack` as deprecated/non-default (exact field TBD by implementer, but must be machine-readable, not just prose in a README).
3. The six successor packs remain independently cataloged and unaffected.
4. A consumer project with `ggen.toml` pointing at `packs/clap-noun-verb-pack` by path still resolves and generates successfully (fix-forward compatibility, not a breaking removal).
5. `docs/` — any tutorial/how-to/reference page that currently points a new user at `clap-noun-verb-pack` as the entry point is updated to point at the appropriate successor pack or at `clap-noun-verb-zeroconfig-pack` if that umbrella role is realized first (cross-reference with the source audit's zeroconfig umbrella framing — that framing is INFERRED, not a dependency of this ticket).

## Falsifiers

- If any consumer's `ggen sync run` against `packs/clap-noun-verb-pack` breaks after this change, the ticket has failed its compatibility requirement — revert the discovery change, do not delete the pack.
- If `scripts/marketplace.py catalog` a/b/cmp determinism check (per `CLAUDE.md`) fails after adding a deprecation marker, the marker mechanism is wrong — fix forward.
- If no machine-readable deprecation signal exists (i.e., the only change is a comment or doc edit), this ticket is not done — "normal discovery" must actually change, not just be documented as changed.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — source evidence and standing
- `packs/clap-noun-verb-pack/pack.toml` — the self-declaration this ticket is grounded in
- `docs/jira/v26.8.19/README.md` — milestone index
