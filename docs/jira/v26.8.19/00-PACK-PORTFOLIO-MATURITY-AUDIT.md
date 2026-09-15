# 00 Pack Portfolio Maturity Audit

Standing: **PARTIAL_ALIVE** — inventory and representative family structures are observed on live `main`; consolidation equivalence is INFERRED and therefore NOT YET ADMITTED. No pack may be deleted or physically merged off the back of this document alone. Ticket 03 (consolidation-court methodology) must exist and run before any merge/delete lands.

## Quick reference

- Corrected inventory count: **143** pack directories on disk (not 142 — see Corrections).
- 1 pack self-declares legacy and names its successors: `clap-noun-verb-pack` (ticket 01).
- 0 cited pack names failed to resolve to a real directory under `packs/`.
- Target shape: ~15-25 canonical pack classes + parameterized profiles, replacing flat proliferation — gated by ticket 02 (taxonomy) and ticket 03 (proof methodology) before any physical action.

## Methodology

This audit does not treat "pack exists" as maturity. It reads the repository's own source hierarchy from `AGENTS.md`/`CLAUDE.md` — `pack.toml -> ontology.ttl -> templates -> gates`, with consequential behavior requiring a real consumer boundary beyond catalog validation — and asks, per grouping of packs, whether they are:

1. Distinct semantic authorities that should stay independent (real domain truth diverges), or
2. Multiple manufacturing instances of the same underlying ontology/grammar that should converge on a shared kernel with parameterized profiles.

Evidence standard applied in this pass: a claim is **verified true** only if grep/`ls`/file-read confirms it directly (pack.toml/README content, directory contents, git log). A claim about semantic *equivalence between families* is explicitly **not** verifiable this way — it requires the pairwise graph/query/template correspondence defined in ticket 03, and is marked `INFERRED` throughout this document, never `TRUE`.

## Corrections applied to the source audit

The raw audit that seeded this milestone made a few errors, corrected here before any ticket references it:

- **Count**: audit said "142 pack directories"; actual `ls -d packs/*/ | wc -l` = **143**. The disposition-count arithmetic in the raw audit ("13/20/64/38/3/3/1") is built on the miscounted inventory and is not restated as authoritative anywhere in this milestone — treat it as a rough historical estimate only, not a ledger.
- **Missing packs**: two on-disk packs were entirely absent from the raw audit's family taxonomy: `castle-pack`, `castle-board-pack`. Neither is assigned to a family in this milestone; they remain ungrouped pending a future audit pass.
- **Missing family member**: `otel-weaver-ocel-pack` exists on disk and belongs conceptually with the OBSERVABILITY/PROCESS family alongside `otel-weaver-pack`, but was not named in the raw audit. Noted here for completeness; not assigned a ticket in this milestone (no high-confidence, individually-verified consolidation claim was made about it).
- **No false-name claims found**: every pack name cited in the raw audit (~140 names) resolved to a real directory. No fabricated pack names needed to be dropped.

## 7-axis maturity matrix

Each family below is scored on 7 axes. `TRUE` means directly verified against file contents in this pass; `INFERRED` means asserted by the source audit but not independently checked (semantic-equivalence claims, by construction, require ticket 03's methodology to become checkable at all).

| Axis | What it measures |
|---|---|
| 1. Ontology presence | Does the pack ship a real `ontology.ttl` (or ontology under `ontology/`)? |
| 2. Template presence | Does the pack project facts via `.tmpl`/`.tera` templates? |
| 3. Gate presence | Does the pack refuse invalid facts via `.rq`/`.py` gates? |
| 4. Evidence/verification | Does the pack carry SHACL shapes, evidence docs, or verification artifacts? |
| 5. Self-declared status | Does the pack's own `pack.toml`/`README.md` state deprecation, successor, or scope limits? |
| 6. Family cohesion | Do sibling packs in the family share a naming/ontology convention suggesting one underlying grammar? |
| 7. Consolidation confidence | Is the specific consolidation claim VERIFIED (file-level) or only INFERRED (semantic, needs ticket 03)? |

### Verified-true findings (axis 5, self-declared status — directly checked)

1. `clap-noun-verb-pack` — **TRUE**. `packs/clap-noun-verb-pack/pack.toml` states: "DEPRECATED. Superseded by clap-noun-verb-schema-pack, clap-noun-verb-crate-pack, clap-noun-verb-routing-pack, clap-noun-verb-behavior-pack, clap-noun-verb-boundary-pack, and clap-noun-verb-verification-pack."
2. `pack-maturity-pack` — **TRUE**. States it cannot manufacture authoritative domain semantics, negative witnesses, domain verification, or documentation/provenance; explicitly does not close `l5p:cap01/02/05/06/07/08/10/11/12` (`packs/pack-maturity-pack/README.md`, `packs/pack-maturity-pack/pack.toml`).
3. `fortune5-enterprise-architecture-pack` — **TRUE**. Contains `README.md`, `ontology.ttl`, `queries/010_architecture_surface.rq`, `shapes/fortune5-profile.shacl.ttl`, `gates/010_admission.rq`, `evidence/composition-contract.md`.
4. `pack-authoring-pack` — **TRUE**. Has `ontology.ttl`, `gates/`, `templates/`.
5. `wasm4pm-pack` — **TRUE**. Has `ontology.ttl`, `gates/`, `templates/`.
6. Git history — **TRUE**. Commit `846a590 fix(clap-noun-verb-pack): pack.toml [pack] admits only name/version/description` is present in `git log`, consistent with the pack's own admission-gap note (FM-PACK-003: `[pack]` admits only `name`/`version`/`description`).

### Families with an INFERRED consolidation claim (axis 7)

All family groupings below (semantic/control kernel, TCPS, wasm4pm, Fortune5/EA, release-lifecycle, repo-lifecycle, MCP, UI-projection-kernel, and the remainder) carry `axis 7 = INFERRED` — the grouping is a structural/naming-convention observation, not a proven graph/query/template correspondence. See ticket 03 for what would promote a family from INFERRED to ADMITTED.

## Priority order for structural work (unchanged from source audit, still INFERRED priority, not an approved sequence)

1. Retire true legacy (`clap-noun-verb-pack`) from normal discovery — ticket 01, does not require ticket 03 because it is a discovery/documentation change, not a merge or delete.
2. Introduce pack classes (KernelPack/CapabilityPack/ProfilePack/WorldPack/CompatibilityPack/EvidencePack/ReleaseControlPack) — ticket 02, admission-required, does not itself move or delete any pack.
3. Define the consolidation-court methodology — ticket 03, gates every family ticket.
4. Per-family consolidation tickets (05+), each explicitly `BLOCKED on ticket 03`.

## See Also

- `docs/jira/v26.8.19/README.md` — milestone index and standing ceiling
- `docs/jira/v26.8.19/01-TICKET-retire-clap-noun-verb-legacy.md`
- `docs/jira/v26.8.19/02-TICKET-pack-class-taxonomy.md`
- `docs/jira/v26.8.19/03-TICKET-consolidation-court-methodology.md`
- `AGENTS.md` — authoritative source hierarchy this audit's methodology is derived from
- `CLAUDE.md` — marketplace architecture and pack profile derivation
