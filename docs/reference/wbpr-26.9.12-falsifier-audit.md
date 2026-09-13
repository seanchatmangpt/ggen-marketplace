# WBPR 26.9.12 Falsifier Audit — 12-Pack Canonical Consolidation, MSCT, Human Twin

Audits PRs #438, #440, #441, #442 against the WBPR's "Production Invariants" and
"Global Falsifiers" claims (12-pack canonical consolidation, MSCT, Human Twin, BRCE,
receipts). Every row below was checked against real `gh`/`git` state on 2026-09-12;
none is copied from the WBPR text unverified.

## Branch/PR topology (verified)

| PR | head | base | state | mergeable |
|----|------|------|-------|-----------|
| #438 | `dfcm-consolidation-26-9-12` | `main` | OPEN | MERGEABLE |
| #440 | `dfcm-marketplace-closure-26-9-12` | `dfcm-consolidation-26-9-12` | OPEN | MERGEABLE |
| #441 | `human-twin-fond-hddl` | `dfcm-consolidation-26-9-12` | OPEN | MERGEABLE |
| #442 | `msct-machine-experience-26-9-12` | `dfcm-marketplace-closure-26-9-12` | OPEN | MERGEABLE |

## Audit table

| Invariant/Falsifier | PR(s) | Status | Evidence |
|---|---|---|---|
| ActiveMarketplace=12 (canonical 12-pack surface is live on main) | #438, #440, #441, #442 | BLOCKED | `git ls-tree origin/main:packs \| wc -l` = 300 pack dirs on `origin/main` today. `gh pr view --json state` for all four PRs returns `"state":"OPEN"` — none merged. The 12-pack surface exists only on unmerged feature branches. |
| Canonical pack "real manufacture" (12 named packs are functioning ggen packs) | #438 | PARTIAL/UNSUPPORTED | `git ls-tree -r --name-only origin/dfcm-consolidation-26-9-12 -- packs/<name>` run for all 12 canonical dirs (`ggen-platform-pack`, `marketplace-governance-pack`, `semantic-projection-pack`, `evidence-standing-pack`, `decision-optionality-pack`, `planning-policy-pack`, `process-intelligence-pack`, `state-transition-pack`, `protocol-integration-pack`, `repository-lifecycle-pack`, `enterprise-governance-pack`, `experience-projection-pack`) shows each contains exactly `pack.toml` + one `ontology.ttl`/`source.ttl` — no gates, no templates, no qualification queries, no tests. Spot-checked ontology content (`ggen-platform-pack/source.ttl`, `marketplace-governance-pack/ontology.ttl`) shows `mg:standing "CANDIDATE"` declared inline in the RDF itself, i.e. the packs self-report as not-yet-admitted. |
| HistoricalEvidence classification (legacy-pack census run and legacy packs mapped/verified per #439) | #440, #442, issue #439 | BLOCKED | `scripts/consolidation_census.py` exists on `origin/dfcm-marketplace-closure-26-9-12` and `origin/msct-machine-experience-26-9-12`, but no output/report artifact from running it exists anywhere in the repo (searched for `*census*` output files — every hit is a pre-existing, unrelated `.rq`/`.sparql` query file in other packs, not this script's output). `gh issue view 439` confirms scope explicitly: "Keep legacy packs unchanged until coverage, consumer impact, and replacement behavior are verified" — i.e. the classification work is scoped but not yet done. |
| PR #441 lineage (Human Twin is built on the closed 12-pack surface from #440) | #441 | BLOCKED | `git merge-base origin/dfcm-marketplace-closure-26-9-12 origin/human-twin-fond-hddl` differs from `git merge-base --is-ancestor` check, which returns false — `human-twin-fond-hddl` is **not** a descendant of `dfcm-marketplace-closure-26-9-12`; `gh pr view 441 --json baseRefName` confirms its actual base is `dfcm-consolidation-26-9-12` (#438), a sibling of #440, not built on it. `git ls-tree -r --name-only origin/human-twin-fond-hddl \| grep marketplace_scope` returns nothing — the file is genuinely absent on this branch (present only on the closure branch), consistent with a lineage gap rather than a deleted-on-purpose file. |
| PR #441 CI: "Qualify canonical 12-pack closure" | #441 | BLOCKED (confirmed pre-existing lineage gap, not a logic bug) | `gh pr checks 441` shows this check `fail`. Job log (`gh run view 34738928942 --log-failed`) shows the exact failure: `python: can't open file '.../scripts/marketplace_scope.py': [Errno 2] No such file or directory`, exit code 2 — a missing-file error, confirming the lineage gap above is the direct cause, not a bug in the qualification logic itself (the assertions after the file-open never execute). |
| gym-pack-contract failure on #441 | #441 | REFUSED:GYM_PACK_SET_DRIFT (pre-existing, out of scope for the 12-pack effort) | `gh pr checks 441` shows `gym-pack-contract` `fail`. Job log (`gh run view 34738928856 --log-failed`) shows: `REFUSED:GYM_PACK_SET_DRIFT:expected=['autofde-gymact-certification-pack', 'chatgptgym-gymact-bridge-pack', 'lifegym-world-pack', 'ww3gym-planning-pack'] observed=[...11 packs...]` — 4 expected vs 11 observed gym packs. This is drift in an unrelated fixed-manifest check (`scripts/verify-gym-packs.py`) against the gym pack family, unrelated to Human Twin/HDDL/FOND content or the 12-pack consolidation; flagged here so it is not conflated with the marketplace_scope.py lineage failure above. |
| MSCT / Machine Experience compiles DfCM semantics into a runtime (PR #442) | #442 | UNSUPPORTED | `gh pr diff 442 --name-only`: `packs/decision-optionality-pack/ontology.ttl`, `packs/experience-projection-pack/ontology.ttl`, `packs/ggen-platform-pack/source.ttl`, `packs/marketplace-governance-pack/ontology.ttl`, `packs/semantic-projection-pack/ontology.ttl`, `scripts/verify_msct_profile.py`. The diff touches only RDF ontology files inside 5 of the 12 skeleton packs plus one verification script — no runtime, no BRCE authority-boundary implementation, no receipt-emission code exists anywhere in the diff or elsewhere in the repo. |
| Human Twin / HDDL / FOND models a permanent human twin with real planning (PR #441) | #441 | UNSUPPORTED | `gh pr diff 441 --name-only`: touches `packs/planning-policy-pack/ontology.ttl` + a new `packs/planning-policy-pack/profiles/permanent-human-twin.ttl`, plus ontology edits in `evidence-standing-pack`, `process-intelligence-pack`, `semantic-projection-pack`, `state-transition-pack`, a query file and two template edits in unrelated packs (`ash-extension-starter-pack`, `github-controloutcome-observation-pack`), and `packs/ash-extension-core-pack/errc-tracker.md`. This is RDF/ontology + one profile `.ttl` + a tracker note — no HDDL solver, no FOND planner, no runtime executing any plan exists in the diff or repo. |
| BRCE authority boundary / receipts (WBPR claims these are production-grade) | #438, #440, #441, #442 | UNSUPPORTED | No BRCE runtime code (parse/route/admit/actuate/receipt) appears in any of the four PR diffs — all four are RDF/ontology + verification-script + tracker-note changes. Receipts referenced in the WBPR (e.g. gym-pack receipt, qualification receipt) are produced only by pre-existing CI scripts (`scripts/verify-gym-packs.py`), not by new code introduced in these PRs. |

## What was NOT independently re-verified (named explicitly, not silently assumed)

- Full byte-for-byte diff review of every `.ttl` file changed in #441/#442 (confirmed file lists via `gh pr diff --name-only`, not full content review of every triple).
- Whether `scripts/verify_msct_profile.py` (#442) or `scripts/consolidation_census.py` pass when actually run locally — only their presence/absence and CI failure logs were checked, not a local execution.
- The full 300-pack `origin/main` count was taken from `git ls-tree origin/main:packs | wc -l` (a direct listing), which is more reliable than the `git ls-tree -d origin/main -- packs` pathspec form (which returned 1, an artifact of pathspec matching against a tree-ish, not a real count — noted here so this discrepancy isn't silently dropped).

## See Also

- `packs/ash-extension-core-pack/errc-tracker.md` — tracker referenced by this audit's requested format (as of 2026-09-12 that file itself contains no markdown table; the table style above uses the four-column shape requested directly: Invariant/Falsifier | PR(s) | Status | Evidence).
- Issue #439 — "Qualify the 80/20 canonical pack topology" (open, scopes the legacy-pack classification work this audit found BLOCKED).
