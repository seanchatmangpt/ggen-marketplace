#!/usr/bin/env bash
# COMMITTED (non-generated) bootstrap copy of scripts/agent-preamble.sh.
#
# Why this file exists -- the same chicken-and-egg ggen-verify-pack's
# bootstrap solves: this pack's gates run on every sync, including the
# very first sync that would generate scripts/agent-preamble.sh. A fresh
# consumer has no preamble script and no fleet:CwdAssertion evidence, so
# sync refuses (gates/030_cwd_assertion_missing.rq) before the generator
# that would produce the real script ever runs.
#
# Resolution (two-phase bootstrap):
#   Phase 1: from the consumer root, run THIS committed copy once per
#            agent: bash packs/agent-fleet-isolation-pack/bootstrap/agent-preamble-bootstrap.sh <agent-name> <expected-worktree>
#            It records a real fleet:CwdAssertion directly.
#   Phase 2: `ggen sync run` now passes the gates and generates
#            scripts/agent-preamble.sh (which resolves the expected
#            worktree from the live union graph instead of a CLI arg);
#            use THAT from then on.
#
# KEEP IN SYNC with templates/agent_preamble_sh.tmpl -- same emission shape.
set -uo pipefail

agent_name="${1:?usage: agent-preamble-bootstrap.sh <agent-name> <expected-worktree>}"
expected="${2:?usage: agent-preamble-bootstrap.sh <agent-name> <expected-worktree>}"

actual_pwd="$(pwd)"
actual_toplevel="$(git rev-parse --show-toplevel 2>/dev/null || echo "NOT_A_GIT_REPO")"
actual_head="$(git log -1 --oneline 2>/dev/null || echo "NO_HEAD")"

matches="false"
if [ "$actual_toplevel" = "$expected" ]; then
  matches="true"
else
  echo "MISMATCH: agent '$agent_name' expected worktree '$expected', actual toplevel '$actual_toplevel' (pwd '$actual_pwd')" >&2
fi

mkdir -p evidence
name_safe="$(echo "$agent_name" | tr -c 'a-zA-Z0-9_-' '_')"
cat >> evidence/ontology.ttl <<EOF
@prefix fleet: <http://seanchatmangpt.github.io/packs/agent-fleet-isolation#> .
fleet:assertion-${name_safe} a fleet:CwdAssertion ;
    fleet:agentName "${agent_name}" ;
    fleet:actualToplevel "${actual_toplevel}" ;
    fleet:actualHeadOneline "${actual_head}" ;
    fleet:matchesAssigned ${matches} .
EOF

echo "agent '$agent_name' cwd assertion recorded (bootstrap): matchesAssigned=${matches}"
if [ "$matches" != "true" ]; then
  exit 1
fi
