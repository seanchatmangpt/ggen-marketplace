# Generator -> Kernel JSONL Closure (gen_workgraph --emit jsonl)

# Summary

`scripts/gen_workgraph.py --emit jsonl` emits one admission candidate per
work axis, in exactly the 16-key shape `GgenIgniter.SemanticJira.admit_work_order/1`
requires. This closes the loop generate -> admit with zero LLM in the
interchange: the JSONL is the canonical interchange (disc-sjira), the Turtle
is the pack-rendered projection.

# Contract deltas vs the TTL view

- `standing` is always `"UNKNOWN"` (a candidate enters at UNKNOWN; standing
  is kernel-derived from receipts, never a stored literal).
- `origin_authority` is the pinned objective IRI
  `...#objective-code-work-authority` of the canonical semantic-jira-pack
  authority index.
- `projections` come from the 15-class vocabulary (`@projection_types`).
- Every SHA field is a full 40-hex SHA; the emitter self-checks all of these
  properties (required keys, UNKNOWN standing, full SHA, 15-class
  projections, IRI origin) and fails loudly rather than emitting a
  malformed line.

# Receipt

Generator selftest (v3 fixtures + jsonl double-run byte-identical, exit 0):

- `/Users/sac/ex4pm` (v26.10.8): 5 candidates, jsonl double-run identical.
- `/Users/sac/zcode-cli` (v26.10.8): 2 candidates, jsonl double-run identical.

Real admission (`mix semantic_jira.admit_candidates --candidates`, canonical
authority index, no epoch / sovereign flags), run 2026-10-08, exit 0:

    admitted 1 SJIRA-26108-SEANCHATMANGPT-EX4PM-001 work_order_digest=sha256:2ccb5c54501c3513...
    admitted 2 SJIRA-26108-SEANCHATMANGPT-EX4PM-002 work_order_digest=sha256:edb8d8328dacc57c...
    admitted 3 SJIRA-26108-SEANCHATMANGPT-EX4PM-003 work_order_digest=sha256:45c8a48c5be1db00...
    admitted 4 SJIRA-26108-SEANCHATMANGPT-EX4PM-004 work_order_digest=sha256:29229292a97846ac...
    admitted 5 SJIRA-26108-SEANCHATMANGPT-EX4PM-005 work_order_digest=sha256:07dc5299f3eed33a...
    admitted 6 SJIRA-26108-SEANCHATMANGPT-ZCODE-CLI-001 work_order_digest=sha256:45794688caaaf047...
    admitted 7 SJIRA-26108-SEANCHATMANGPT-ZCODE-CLI-002 work_order_digest=sha256:488ce716e03d1bc4...
    summary admitted=7 refused=0

Two real defects surfaced by the first admission runs, both fixed:
1. identity was version-derived only -- a multi-repo batch collided
   (refusals `{:duplicate, "identity", ...}`); identities are now
   repo-qualified (`SJIRA-<ver>-<REPO>-<n>`).
2. acceptance must be a LIST of strings (`{:invalid_list, "acceptance"}`);
   the v3 compressed acceptance phrasing (a string) is wrapped in a list.

# See Also

- `ggen_igniter:lib/ggen_igniter/semantic_jira.ex` (@required, @projection_types)
- `ggen_igniter:lib/mix/tasks/semantic_jira.admit_candidates.ex`
- `scripts/gen_workgraph.py` (JSONL contract section of the module docstring)
