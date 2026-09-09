# agent-fleet-isolation-pack

Reusable manufacturing capital for isolating a parallel multi-agent fleet
across a repo tree. `ggen sync run` refuses (FM-PACK-013) when a fleet plan
declares two agents sharing a worktree or build-cache directory, when an
agent never proved it actually ran in its assigned worktree, or when an
agent's jidoka stop was left unresolved.

## What the pack ships

| Piece | File | Role |
|---|---|---|
| Vocabulary | `ontology.ttl` | `fleet:Agent` (the plan) / `fleet:CwdAssertion`, `fleet:JidokaStop`, `fleet:EvidenceCommand` (the evidence) |
| Gates | `gates/010..050*.rq` | worktree collision, build-cache collision, missing cwd assertion, cwd mismatch, unresolved jidoka stop |
| Generated manifest | `templates/fleet_manifest_sh.tmpl` | renders `scripts/fleet-manifest.sh` — creates one `git worktree` + build-cache dir per declared `fleet:Agent` |
| Generated preamble | `templates/agent_preamble_sh.tmpl` | renders `scripts/agent-preamble.sh` — every agent's mandatory first action; records a real `fleet:CwdAssertion` |
| Generated report | `templates/fleet_report_md.tmpl` | renders `FLEET_REPORT.md`: repo \| worktree \| verdict \| jidoka stops |
| Bootstrap copy | `bootstrap/agent-preamble-bootstrap.sh` | committed, non-generated preamble for the first run (see below) |

## Consumer contract

1. Declare the fleet plan in your own ontology source (`fleet:Fleet` +
   `fleet:Agent` individuals: `fleet:name`, `fleet:assignedRepo`,
   `fleet:worktreePath`, `fleet:buildCacheDir` — each path unique per agent).

2. Wire the pack and a local evidence mini-pack in `ggen.toml`:

   ```toml
   [packs]
   agent-fleet-isolation-pack = { path = "../../packs/agent-fleet-isolation-pack" }
   fleet-evidence             = { path = "evidence", lock = false }  # regenerated every run
   ```

3. Two-phase bootstrap (same reason `ggen-verify-pack` needs one: the
   gates run on every sync, including the first one that would generate
   the preamble script itself):
   - **Phase 1**: `bash packs/agent-fleet-isolation-pack/bootstrap/agent-preamble-bootstrap.sh <agent-name> <expected-worktree>` once per agent to scaffold `evidence/ontology.ttl`.
   - **Phase 2**: `ggen sync run` now passes gates/030 and generates the real `scripts/agent-preamble.sh`; dispatch every subsequent agent with `scripts/agent-preamble.sh <agent-name>` as its literal first action, before any other tool call.

4. Run `scripts/fleet-manifest.sh` to create the declared worktrees and
   build-cache dirs before dispatching agents.

5. If an agent hits ambiguity (which branch is canonical, whether to
   delete something, conflicting requirements) it must record a
   `fleet:JidokaStop` (agent name + reason) rather than guess — gates/050
   refuses sync while any stop lacks `fleet:resolved true`.

6. `ggen sync run` refuses on any worktree/build-cache collision, missing
   or mismatched cwd assertion, or open jidoka stop. Once green, sync
   renders `FLEET_REPORT.md` from the admitted plan + evidence facts.

## Qualification

`qualification/consumer.ttl` is a synthetic 2-agent green fixture (disjoint
worktrees/caches, both cwd assertions matching, no jidoka stops) — proven
`0 rows` against all 5 gates with `rdflib` 7.6.0. A companion
deliberately-broken fixture (shared worktree/cache between two agents, a
third agent with no cwd assertion, a fourth with a mismatched assertion and
an open jidoka stop) was built and run against the same gates: each fired
exactly the row(s) matching its named violation, confirmed this session —
not an eyeball claim.
