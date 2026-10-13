#!/usr/bin/env bash
# Court git-trust-court -- CI wiring for scripts/git_trust_court.py.
#
# git_trust_court.py has a runner-compatible CLI (--file repeatable, --json
# OUT) but previously had no wired home: the launchd fleet-courts job runs it
# only via the aggregate runner. This court gives it a direct ci/courts.json
# entry. Degraded mode for CI: sibling fleet repos may be absent on a runner;
# the script itself has no skip flag, so this wrapper
#   1. censuses the fleet workgraph files under $HOME (mirrors FLEET_WORKGRAPHS
#      in scripts/run_fleet_courts.py) and fails only if ZERO are present,
#   2. passes only the workgraph files that exist via --file,
#   3. classifies each UNRESOLVED: detail "no local checkout for owning repo"
#      is absence-class (degraded skip in CI); any other UNRESOLVED (a SHA the
#      owning repo, which IS present, does not contain) is a real failure.
# Local launchd remains the primary execution home; CI is supplemental
# read-only evidence.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"

TMP="${RUNNER_TEMP:-/tmp}/git-trust-court-ci.$$"
mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT

FLEET_WORKGRAPHS=(
  ash_a2a/docs/sjira/v26.10.8/WORKGRAPH.ttl
  ash_affidavit/docs/sjira/v26.10.8/WORKGRAPH.ttl
  ash_pplan/docs/sjira/v26.10.8-1/WORKGRAPH.ttl
  ash_r2rml/docs/sjira/v26.10.8/WORKGRAPH.ttl
  ash_surface/docs/sjira/v26.10.8/WORKGRAPH.ttl
  beam4pm/docs/sjira/v26.10.8/WORKGRAPH.ttl
  castle/docs/sjira/v26.10.8/goal.ttl
  ex4pm/docs/sjira/v26.10.8/WORKGRAPH.ttl
  ggen-ecosystem/docs/sjira/v26.10.8/WORKGRAPH.ttl
  ggen-marketplace/docs/sjira/v26.10.8/WORKGRAPH.ttl
  xaas/docs/sjira/v26.10.8/WORKGRAPH.ttl
  zcode-cli/docs/sjira/v26.10.8/WORKGRAPH.ttl
)

echo "::group::git-trust-court: sibling workgraph census"
present=0
absent=0
for rel in "${FLEET_WORKGRAPHS[@]}"; do
  if [ -f "$HOME/$rel" ]; then
    echo "  present: ~/$rel"
    present=$((present + 1))
  else
    echo "  absent : ~/$rel"
    absent=$((absent + 1))
  fi
done
echo "census: $present present / $absent absent"
if [ "$present" -eq 0 ]; then
  echo "GIT_TRUST_NO_SIBLINGS: zero fleet workgraphs present under \$HOME;"
  echo "the trust court has no subject to observe. Failing."
  exit 1
fi
echo "::endgroup::"

echo "::group::git-trust-court: run git_trust_court.py over present workgraphs"
GT_FILES=()
for rel in "${FLEET_WORKGRAPHS[@]}"; do
  [ -f "$HOME/$rel" ] && GT_FILES+=(--file "$HOME/$rel")
done
python3 scripts/git_trust_court.py "${GT_FILES[@]}" \
  --json "$TMP/git-trust.json" \
  >"$TMP/stdout.txt" 2>"$TMP/stderr.txt"
GT_RC=$?
cat "$TMP/stderr.txt"
echo "git_trust_court.py exit: $GT_RC (adjudicated below)"
echo "::endgroup::"

echo "::group::git-trust-court: absence-aware adjudication"
ADJ_RC=0
python3 - "$TMP/git-trust.json" <<'PYEOF' || ADJ_RC=$?
import json, sys

gt = json.load(open(sys.argv[1]))
failures = []
absent_skipped = 0
rooted = unrooted = 0
for wg in gt.get("workgraphs", []):
    for r in wg.get("results", []):
        v = r["verdict"]
        if v == "RESOLVED-ROOTED":
            rooted += 1
        elif v == "RESOLVED-UNROOTED":
            unrooted += 1
        else:  # UNRESOLVED
            if r.get("detail") == "no local checkout for owning repo":
                absent_skipped += 1
            else:
                failures.append(
                    f"git-trust: UNRESOLVED {r['sha']} "
                    f"({r['owning_repo']}): {r.get('detail')}"
                )
for f in failures:
    print(f"FAIL: {f}")
print(f"git-trust-court degraded verdict: "
      f"{'FAIL' if failures else 'PASS'} "
      f"({rooted} rooted / {unrooted} unrooted / "
      f"{absent_skipped} absence-class skipped)")
sys.exit(1 if failures else 0)
PYEOF
echo "::endgroup::"

echo "::group::git-trust-court: report json sanity"
python3 -m json.tool "$TMP/git-trust.json" > /dev/null || exit 1
echo "::endgroup::"

exit "$ADJ_RC"
