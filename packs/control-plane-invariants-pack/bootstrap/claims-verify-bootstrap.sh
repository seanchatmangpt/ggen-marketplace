#!/usr/bin/env bash
# COMMITTED (non-generated) bootstrap copy of scripts/claims-verify.sh.
#
# Why this file exists -- the same chicken-and-egg ggen-verify-pack and
# agent-fleet-isolation-pack solve: this pack's gates run on every sync,
# including the very first sync that would generate scripts/claims-verify.sh.
# A freshly-authored ctrl:Claim (claimId/claimText/evidenceCommand, no
# verdict yet) trips gates/020_claim_without_verdict.rq before the
# generator that would actually run evidenceCommand and record a verdict
# ever gets to run.
#
# Resolution (two-phase bootstrap):
#   Phase 1: from the consumer root, run THIS committed copy once per
#            claim: bash packs/control-plane-invariants-pack/bootstrap/claims-verify-bootstrap.sh <claim-id> <evidence-command...>
#            It runs the command for real and appends a real verdict fact
#            directly to evidence/ontology.ttl.
#   Phase 2: `ggen sync run` now passes gates/020 and generates the real
#            scripts/claims-verify.sh (which resolves every unverdicted
#            claim's evidenceCommand from the live union graph instead of
#            CLI args); use THAT for every subsequent claim.
#
# KEEP IN SYNC with templates/claims_verify_sh.tmpl -- same emission shape,
# same CONFIRMED-on-exit-0 / REFUTED-on-nonzero rule, same claimId join key.
set -uo pipefail

claim_id="${1:?usage: claims-verify-bootstrap.sh <claim-id> <evidence-command...>}"
shift
cmd="${*:?usage: claims-verify-bootstrap.sh <claim-id> <evidence-command...>}"

echo "=== claim: $claim_id (bootstrap) ==="
echo "+ $cmd"
output="$(eval "$cmd" 2>&1)"
exit_code=$?
if [ "$exit_code" -eq 0 ]; then
  verdict="CONFIRMED"
else
  verdict="REFUTED"
fi
echo "$output"
echo "verdict: $verdict (exit $exit_code)"

mkdir -p evidence
id_safe="$(echo "$claim_id" | tr -c 'a-zA-Z0-9_-' '_')"
escaped_output="$(printf '%s' "$output" | awk '{gsub(/\\/,"\\\\"); gsub(/"/,"\\\""); printf "%s\\n", $0}')"
cat >> evidence/ontology.ttl <<EOF
@prefix ctrl: <http://seanchatmangpt.github.io/packs/control-plane-invariants#> .
ctrl:evidence-${id_safe} a ctrl:Claim ;
    ctrl:claimId "${claim_id}" ;
    ctrl:literalEvidence "${escaped_output}" ;
    ctrl:verdict "${verdict}" .
EOF

echo "claim '$claim_id' verdict recorded (bootstrap): ${verdict}"
