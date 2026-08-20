# vendor-readmes/ — primary-source Ash ecosystem package pages, not agent paraphrase

Per explicit user correction mid-session: two research agents (an Explore-agent survey and a
`/deep-research` workflow, both this session) independently claimed `ash_iam` and `ash_onetime`
do not exist on hex.pm. **Both claims were wrong**, caught by the user, then confirmed wrong by
directly fetching `https://hex.pm/packages/ash_iam` and the real hex.pm API for `ash_onetime`.
`ash_onetime` was in fact published just 11 days before this session (first release
2026-08-09) — plausibly after whatever cutoff the research agents' training/crawl reflected, but
that is a guess, not a confirmed root cause; the actionable fact is that the claim was wrong and
is now corrected from a primary source, not that the mechanism of the error is understood.

**The fix, per the user's own instruction**: don't trust agent-summarized package-existence
claims — save the actual primary source (the real hex.pm package page, which renders each
package's real README) locally, so every future check is against a real, re-fetchable artifact,
not a paraphrase.

## Contents

- `PACKAGE-LIST.txt` — the real, authoritative list of all 137 packages that directly depend on
  `ash` on hex.pm, fetched from `hex.pm/api/packages?search=depends:hexpm:ash&sort=total_downloads`
  (paginated, real JSON API, not the scraped HTML search UI used in earlier session passes).
- `hexpm-pages/*.html` — the real hex.pm package page for every one of those 137 packages,
  fetched directly (`curl https://hex.pm/packages/<pkg>`), **all 137 succeeded, zero failures**.
  Each page includes the package's real description, current version, and rendered README.
- `*.md` (top-level of this dir) — real `README.md` files fetched directly from GitHub for the 18
  packages this session's `xaas-ash-build-ecosystem.sh` actually installs (a curated subset of
  the 137, chosen for XaaS relevance — persistence, identity, API surfaces, admin UI, background
  jobs, entitlement/audit, billing, compliance, authorization).

## Verified corrections, traceable to these files

- `ash_iam` — real, v2.1.0, "AWS IAM-style policy evaluation for Ash Framework", first published
  2025-08-27. GitHub link in hex.pm metadata (`wearecococo/ash-iam`) 404s — repo may be private,
  renamed, or deleted since publishing; the hex.pm package itself and its docs
  (`ash-iam.hexdocs.pm`) are real and live, confirmed via `hexpm-pages/ash_iam.html`.
- `ash_onetime` — real, v1.0.0 (10 releases total, first 2026-08-09), "An Ash extension for
  explicit idempotency and one-time nonce semantics", `github.com/baselabs/ash_onetime`
  (real README fetched, `ash_onetime.md`).
- `ash_policy_authorizer` — re-checked independently this pass (not just repeated from the
  earlier claim): last release `0.16.5` on 2022-03-23, no releases since. The "deprecated since
  2022" claim holds up under direct re-verification.
