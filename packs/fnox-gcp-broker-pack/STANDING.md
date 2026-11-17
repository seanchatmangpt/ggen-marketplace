# fnox-gcp-broker-pack Standing

Standing: UNVERIFIED

- Authored 2026-11-16 (fnox v26.11.16 lane L19) with no shell: nothing in this pack has been run
  through `python3 scripts/marketplace.py validate`, `ggen sync run`, pyshacl, or `terraform validate`.
- `ggen.toml` + frontmatter SPARQL in `templates/*.tera` are intended to emit
  `infra/gcp/broker/{preamble,variables,identity,pubsub,intake,egress_workers,gateway}.tf` and
  `infra/gcp/broker/topology.md`.
- `gates/010..040` (any row = refusal) and `shapes/fgb.shacl.ttl` encode the three required refusals;
  `tests/mutations/*.ttl` are the falsifiers (each must produce >= 1 gate row / SHACL non-conformance
  when unioned with the ontology).
- Coordinator round 1 (ggen 26.11.5): scratch `ggen graph validate`/`ggen sync run` REFUSED
  `[FM-CONFIG-101]` (ambiguous schema). Fixed: `[project].version` added, `[validation]` moved from
  `ggen.toml` to `pack.toml`. Re-run pending.
- Coordinator round 2 (ggen 26.11.5, scratch): `[project].version` removed again by the coordinator
  (frontmatter schema treats it as a declarative marker); `ggen graph validate` PASS (341 quads,
  8 templates); `ggen sync run --skip-ea-admission` rendered 8 files; `terraform validate` Success;
  `terraform fmt -check` flagged gateway.tf; rdflib court: 010/030 flip, 040 clean, SHACL flips on
  worker_two_secrets; gates/020 failed to parse (UNION outside group). Fixed in-lane: 020 rewritten
  as standard `{ } UNION { }` with HAVING; gateway heredoc moved into `locals`. Re-run pending.
- Repair lane R5 (2026-11-16, S02 L2/L3, no shell): `tests/mutations/push_no_oidc.ttl` authored as the
  040 falsifier (sibling push subscription without OIDC SA/audience; expected 2 rows from 040, 0 from
  010/020/030); `gates/010_topic_dedup.rq` comment aligned with the real fixture (additive sibling
  topic, not a dropped attribute). "040 clean" above is still never-flipped until the coordinator
  runs the rdflib loop with the new fixture (commands in
  `/Users/sac/fnox/docs/jira/v26.11.16/receipts/R05-pack-kd-repair.md`).
- Flip this line only from a receipt that cites the exact commands and their exit codes.
