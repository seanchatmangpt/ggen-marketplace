# v26.8.19 Pack Portfolio Consolidation Milestone

Standing ceiling: **PARTIAL_ALIVE**. Inference across this entire milestone is not yet ADMITTED. **No pack should be deleted or merged off the back of this milestone directory alone** — every family ticket (05-11) is explicitly `BLOCKED on ticket 03` until a real family-consolidation proof exists for that specific family.

## Quick reference

This directory is a milestone-ticket exception to this repository's strict Diátaxis documentation structure (`docs/tutorials/`, `docs/how-to/`, `docs/reference/`, `docs/explanation/`), matching the convention already used for milestone tickets in sibling repos (e.g. `ggen-legacy/tickets/*.md`). Nothing here is a Diátaxis page and nothing here should be treated as one.

## Milestone summary

The pack-consolidation portfolio audit that seeded this milestone found that `ggen-marketplace`'s pack count (143 on disk, corrected from the source audit's "142") has crossed the point where adding more packs is the dominant maturity strategy — the next jump is class closure and consolidation of repeated projection grammars, not new pack creation. The audit is grounded in this repository's own source hierarchy (`pack.toml -> ontology.ttl -> templates -> gates`, real consumer boundary required for consequential claims) rather than treating "pack exists" as maturity.

One concrete, individually-verified finding anchors the milestone: `clap-noun-verb-pack` already self-declares deprecated in its own `pack.toml`, naming six real successor packs. Everything else — family groupings, proposed kernel/profile shapes, disposition counts — is `INFERRED`: a structural/naming observation, not a proven graph/query/template correspondence, and is documented as such throughout.

## Ticket index

| File | What it is | Depends on |
|---|---|---|
| `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` | Source-of-truth analysis: 7-axis maturity matrix, methodology, corrections to the raw audit's count/omissions | — |
| `01-TICKET-retire-clap-noun-verb-legacy.md` | Retire one verified-deprecated pack from discovery (not delete) | — (independently actionable) |
| `02-TICKET-pack-class-taxonomy.md` | Introduce 7 portfolio-role pack classes; ADMISSION-REQUIRED, no physical pack moves | — (independently actionable) |
| `03-TICKET-consolidation-court-methodology.md` | The proof machinery every physical merge must pass through | — (independently actionable; gates 05-11) |
| `05-TICKET-tcps-family-consolidation.md` | TCPS family plan | BLOCKED on 03 |
| `06-TICKET-wasm4pm-family-consolidation.md` | wasm4pm family plan | BLOCKED on 03 |
| `07-TICKET-fortune5-ea-family-consolidation.md` | Fortune5/Enterprise Architecture family plan | BLOCKED on 03 |
| `08-TICKET-release-lifecycle-family-consolidation.md` | Release/CI/publication control family plan | BLOCKED on 03 |
| `09-TICKET-repo-lifecycle-family-consolidation.md` | Repository lifecycle family plan | BLOCKED on 03 |
| `10-TICKET-mcp-protocol-family-consolidation.md` | MCP protocol family plan (runtimes stay separate) | BLOCKED on 03 |
| `11-TICKET-ui-projection-kernel-family-consolidation.md` | UI projection kernel family plan (largest family, 14-15 members) | BLOCKED on 03 |

## What was corrected from the raw audit before drafting these tickets

- Pack count corrected from 142 to the actual on-disk **143**.
- Two on-disk packs entirely missing from the raw audit's family taxonomy are noted (`castle-pack`, `castle-board-pack`) but not assigned a ticket in this milestone — no consolidation claim was made about them to correct.
- One on-disk pack (`otel-weaver-ocel-pack`) belonging to the OBSERVABILITY family was missing from the raw audit's family list; noted in `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` but not given its own ticket since no specific claim about it was made to verify.
- The raw audit's "disposition counts" (13/20/64/38/3/3/1) are explicitly not restated as authoritative anywhere in this milestone — they were computed against the miscounted 142-pack inventory and are noted as a rough historical estimate only.
- Every other pack name cited in the raw audit resolved to a real directory; none were dropped for non-existence.

## Explicit standing ceiling

Read every ticket in this directory as `PARTIAL_ALIVE`. The self-declared-deprecated finding for `clap-noun-verb-pack` (ticket 01) and the file-content findings cited in `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` are directly verified and safe to act on for *discovery-level* changes. Every family consolidation ticket (05-11) requires ticket 03's court to return a real, cited, machine-generated report before a single pack is physically merged or deleted. Treat any PR that skips that gate as a process violation, not as a shortcut this milestone endorses.

## See Also

- `../../../CLAUDE.md` — marketplace architecture, pack profile derivation, control-plane admission doctrine
- `../../../AGENTS.md` — authoritative source hierarchy and discipline list
- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — full methodology and evidence this milestone is built on
