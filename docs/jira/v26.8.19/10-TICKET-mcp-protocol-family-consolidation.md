# 10 Ticket MCP Protocol Family Consolidation

Standing: PARTIAL_ALIVE — court run complete, CLOSED (no merge, per REFUTED falsifier).

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

## Outcome (court run complete)

The consolidation court was run for real against this family (`docs/jira/v26.8.19/families/mcp-protocol.toml`):

```
$ python3 scripts/consolidation_court.py docs/jira/v26.8.19/families/mcp-protocol.toml > /tmp/court-mcp-protocol.toml.json; echo EXIT:$?
EXIT:0

$ python3 -m json.tool < /tmp/court-mcp-protocol.toml.json > /dev/null && echo VALID_JSON
VALID_JSON
```

- **Family**: `mcp-protocol` (members: `chatgptgym-gymact-bridge-pack`, `fastmcp-pack`, `gdmcp-pack`, `mcpp-pack`, `rmcp-pack`)
- **Verdict**: `REFUTED`
- **Report path**: `docs/jira/v26.8.19/families/mcp-protocol-court-report.json`
- **Conflicting pairs**: `ontology_conflicting_pairs: 10` of `total_pairs: 10` — all 10 pairs among the 5 members show `ontology_conflict: True` with 0 common ontology terms in every pair.

Per this ticket's own falsifier: "If the court finds no common protocol-vocabulary subset (each pack's ontology is bespoke to its runtime with no shared triples), the consolidation claim is `REFUTED` and this ticket closes with no physical change." That condition is met (10/10 pairs conflicting, no shared ontology terms in any pair), so this ticket is **closed with no physical change** — no merge, no shared `ontology/` include extraction, no kernel pack. The four runtime packs (`fastmcp-pack`, `gdmcp-pack`, `rmcp-pack`, `mcpp-pack`) remain fully separate, consistent with acceptance criterion 4 and the family's "do not collapse runtimes" framing.

No merge/physical-consolidation phase applies to this ticket following this result — a REFUTED court verdict is itself an acceptable complete outcome per the falsifier above, not a precursor to further merge work.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — MCP/protocol integration family entry
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`
