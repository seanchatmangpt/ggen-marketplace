# CI standing policy

Grounded in a real 34-repo ecosystem health audit (2026-08-13) across reconstitution manifests, this policy separates two failure classes that are easy to conflate: CI that exists but has never established default-branch standing, and CI whose declaration cannot establish default-branch standing because it lacks the relevant trigger.

## Failure class 1: green CI only on a working branch

A real, currently-passing workflow on a feature branch does not establish the default branch's standing. This is a merge/history/evidence gap, not necessarily a CI-authoring gap.

Detect it with a live run-history/default-head check such as the ecosystem reconstitution tooling in `autofde-lab`, not by asserting from workflow YAML that a run must have happened.

## Failure class 2: no push trigger declared

A primary CI workflow with no push trigger cannot discharge an obligation to re-establish the standing of a pushed default-branch ref. This is an authoring-time defect that can be caught by `github-actions-pack` admission law.

Legitimate workflow-call/manual-only/release-only cases can remain supported when the exception is explicit rather than silently absent.

## Policy

1. **Primary CI must declare the trigger needed to establish the standing it claims, or explicitly state why that trigger is not applicable.**
2. **A green run on a feature branch is not evidence of default-branch standing.** Standing is attached to the exact ref/SHA that actually ran.
3. **`BUILD_BROKEN` and `UNKNOWN` must stay distinct.** A real failing run is failure evidence; zero applicable execution history is absence of evidence.
4. **A workflow file is not a workflow run.** Authored YAML, badges, and expected triggers are inspection evidence only.
5. **A subcourt remains scoped.** A green pack-specific exact-head court can establish that boundary even when an unrelated aggregate guard fails, after dependency independence is proved. The reverse also holds: aggregate green cannot erase an owning domain failure.

## Merge/promotion boundary

This policy does not automatically merge green work or grant release/production authority. Merge, release, and consequential actuation remain separate transitions governed by their own authority and evidence requirements.

## Live-history boundary

Schema/ggen gates can catch declaration defects. They cannot prove that GitHub actually executed a green run against a particular live ref. That half of the policy requires observation of live run history and exact subject identity.

## Relationship to Level 5

CI is evidence infrastructure, not the definition of Level 5. A Level-5 pack may use CI to execute its maturity courts, but the claim still requires the semantic/admission/manufacture/execution/receipt/authority/composition and Diátaxis closure named by [the Level-5 maturity contract](level5-maturity-contract.md).

A repository-wide green workflow cannot promote a domain runtime or external actuation boundary that the workflow did not execute. Likewise, generated Level-5 docs do not become ALIVE because Pages built them; the Pages run proves only the documentation manufacture/build boundary.

## See also

- `packs/github-actions-pack/gates/030_push_trigger_required.rq` — authoring-time push-trigger obligation.
- `packs/github-actions-pack/qualification/consumer.ttl` — bounded fixtures for that gate.
- ecosystem live-history/default-head drift checks in `seanchatmangpt/autofde-lab` — observation-time evidence for default-branch standing.
- [Standing](standing.md) — state vocabulary and exact-subject law.
