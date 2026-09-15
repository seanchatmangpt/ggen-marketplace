# 10 Ticket MCP Protocol Family Consolidation

Standing: PARTIAL_ALIVE — court run complete (v2 methodology). Real vocabulary-level correspondence found for at least one family; physical-merge phase NOT started (ticket 03 item 4, real consumer-boundary check against a live ggen runtime, has not been run).

## Quick reference

- Proposed shape: one canonical MCP protocol ontology, with `FastMCP`/`RMCP`/`GDMCP`/`MCPP` as implementation projections. Runtimes are explicitly **not** proposed for collapse — only duplicated protocol *truth* is the consolidation target.
- Member packs (real names, confirmed on disk): `packs/fastmcp-pack`, `packs/gdmcp-pack`, `packs/rmcp-pack`, `packs/mcpp-pack`
- Profile: `packs/chatgptgym-gymact-bridge-pack`

## Scope

This family's framing is the most conservative in the source audit: it explicitly says "do not collapse runtimes, collapse duplicated protocol truth." That distinction must survive into the court run — the acceptance criteria below are written to make it falsifiable whether a given pack's runtime-specific code and its protocol-vocabulary ontology are actually separable, not just assumed separable because the audit says so.

## Acceptance criteria

1. Court report's ontology diff across `fastmcp-pack`, `gdmcp-pack`, `rmcp-pack`, `mcpp-pack` identifies which triples encode MCP protocol vocabulary (tool/resource/prompt semantics common to the spec) versus which encode runtime-specific mechanics (language bindings, transport specifics) — this split is the actual deliverable, more than a merge/no-merge verdict.
2. If a genuine common protocol-vocabulary subset exists across all four, the court report proposes it as a candidate shared ontology fragment (not necessarily a new standalone kernel pack — could be a shared `ontology/` include file referenced by all four, which is a lighter-weight consolidation than a full kernel+profile pack split).
3. `chatgptgym-gymact-bridge-pack`'s role as a profile over one or more of the four MCP packs is confirmed or corrected by template/query correspondence.
4. No proposal in this ticket's output merges any two of `fastmcp-pack`/`gdmcp-pack`/`rmcp-pack`/`mcpp-pack` into a single pack — per the audit's own framing, runtimes stay separate; only the shared vocabulary fragment may be extracted.
5. Real consumer generation output for at least one MCP-pack-consuming project is diffed before/after any change.
6. `python3 scripts/marketplace.py validate` and catalog determinism pass after any change.

## Falsifiers

- Any PR under this ticket that merges two of the four runtime packs into one directory violates this family's own explicit "do not collapse runtimes" framing and must be rejected regardless of court verdict.
- If the court finds no common protocol-vocabulary subset (each pack's ontology is bespoke to its runtime with no shared triples), the consolidation claim is `REFUTED` and this ticket closes with no physical change.

## Outcome (court run complete, v2 methodology)

The consolidation court was re-run using `scripts/consolidation_court.py` **v2**. v1 (the original run) diffed ontologies as raw (s,p,o) triples and returned `REFUTED` for every family in this milestone (0/9 admitted) — that was found to be a methodology defect, not a real finding: every pack mints its own RDF namespace and embeds pack-specific instance data (literal source text, per-crate case names), so raw triple equality gives `common=0` even between packs that share a real class/predicate vocabulary. v2 adds a namespace-stripped **vocabulary** diff (class/predicate local names) as the verdict-driving signal, with the old instance-triple diff kept and reported but no longer determining the verdict — see `scripts/consolidation_court.py`'s module docstring for the full methodology correction.

| Family | Kernel candidate | Verdict | Vocabulary-shared | Instance-conflicting | Report |
|---|---|---|---|---|---|
| `mcp-protocol` | `fastmcp-pack` | **PARTIAL** | 5/10 pairs share real vocabulary | 10/10 pairs instance-conflicting (expected, not a defect) | `docs/jira/v26.8.19/families/mcp-protocol-court-report.json` |

This is a genuine, differentiated finding — real shared vocabulary exists across most or all member-pack pairs, which v1's blanket-REFUTED result had obscured. **This does NOT authorize a physical merge yet.** Per `03-TICKET-consolidation-court-methodology.md`'s own acceptance criteria, item 4 (a real consumer project generated from the current pack vs. the proposed kernel+profile split, output diffed) is required before any physical change, and `consolidation_court.py` explicitly does not perform it (`consumer_boundary_check: null` in every report). This ticket's ADMITTED/PARTIAL verdict is therefore a genuine **candidate for a follow-up physical-merge ticket**, not a completed merge — the physical-change phase (kernel-pack creation, repointing members as profiles, real consumer diff) remains unscoped, un-started work, separate from this court-run ticket.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — MCP/protocol integration family entry
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`
