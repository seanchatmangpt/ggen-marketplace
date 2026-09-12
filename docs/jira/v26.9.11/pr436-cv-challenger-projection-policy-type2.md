# Merge PR #436 + close CROSS_PACK_REFERENCE_UNQUALIFIED findings

## Summary

`cv:ChallengerProjectionPolicy` in `challenger-value-framing-pack` carried real
facts (`cv:authorityCeiling`, `odrl:prohibition`) but was never itself typed,
which left a real `CROSS_PACK_REFERENCE_UNQUALIFIED` finding open against
`ash-r2rml-paas-pack` (the referencing pack) via
`scripts/check_cross_pack_references.py`. Prior PRs in this session had
correctly left the finding BLOCKED rather than fabricate a type. This work
types the individual as `odrl:Policy` (vocabulary the pack already imports)
and adds the referencing pack's own opt-in
`qualification/consumer.ttl` fixture restating the one fact it relies on, per
the checker's documented instance-value admission path. PR #436 was merged to
main and origin/main was subsequently merged back into three other branches.

## Status

Done - already merged/committed.

## Commits

- `aeddb6c2c` Merge pull request #436 from seanchatmangpt/fix/cv-challenger-projection-policy-type2
- `2188fc710` fix(cross-pack-refs): close the last real CROSS_PACK_REFERENCE_UNQUALIFIED finding
- `9f96f00e5` merge: bring in origin/main (cross-pack-reference + timeout-minutes fixes)
- `9c95bbc5a` merge: bring in origin/main (cross-pack-reference + timeout-minutes fixes)
- `0293440b3` merge: bring in origin/main (timeout-minutes + cross-pack-reference fixes)

## Changes

- `packs/challenger-value-framing-pack/ontology.ttl`: added `cv:ChallengerProjectionPolicy a odrl:Policy .` — types the individual using the pack's own already-imported W3C ODRL 2.2 vocabulary, no new local class invented.
- `packs/ash-r2rml-paas-pack/qualification/consumer.ttl` (new file): added the minimal qualification fixture `cv:ChallengerProjectionPolicy a odrl:Policy .`, restating the one fact the referencing pack relies on. `ash-r2rml-paas-pack` had no `qualification/` directory before this commit.
- Net diff at the PR-merge commit (`aeddb6c2c`): 2 files changed, 20 insertions(+), 1 deletion(-).
- `0293440b3` additionally brings in a large batch of unrelated `origin/main` changes merged into that branch at the same time (new `.github/actions/setup-ggen-factory/action.yml`, `ci.yml` and several workflow files touched — visible in `git show --stat`), consistent with a routine "bring in origin/main" merge rather than new work authored by this ticket's fix.

## Verification

From the `2188fc710` commit message (real, this session, as stated by the author):

- `python3 scripts/check_cross_pack_references.py --mode warn` — before: printed `CROSS_PACK_REFERENCE_UNQUALIFIED: pack=ash-r2rml-paas-pack ...`; after: no violation printed.
- `python3 scripts/check_cross_pack_references.py --mode gate` — before: exit 2 (REFUSED); after: exit 0.
- `python3 scripts/marketplace.py validate` — validated packs=299, manifests=299, ontologies=450, templates=1799, native_gates=1458, verifier_gates=37 (no regression).
- `python3 -m pytest tests/ scripts/ -q` — 3 failed, 168 passed. Failures (`test_book_nav_coverage.py`, `test_cross_pack_turtle_literals.py` x2) stated as pre-existing, confirmed against unmodified main via earlier sessions' git-stash checks, unrelated to this change.
- Real `ggen sync --dry-run` from each pack's own `ggen.toml`: `ash-r2rml-paas-pack` → ADMITTED, 3 files (`mix.exs`, `paas.ex`, `paas_test.exs`); `challenger-value-framing-pack` → ADMITTED, 3 files (`docs/*.generated.md`).

No independent CI run evidence is included in this ticket beyond what the commit message states.

## Related

- PR #436 (`fix/cv-challenger-projection-policy-type2`)
- Referenced Claude session in commit `2188fc710`: `https://claude.ai/code/session_01XDybKfXcyKkTchdA5YrXcC`
