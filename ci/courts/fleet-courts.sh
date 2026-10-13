#!/usr/bin/env bash
# Court fleet-courts -- CI-degraded wiring for the machine-local fleet courts.
#
# Primary execution home is the launchd job (label com.sac.fleet-courts, every
# 6h) running scripts/run_fleet_courts.sh; see
# docs/sjira/v26.10.8/FLEET-COURTS-CRON.md. CI is supplemental READ-ONLY
# evidence: sibling fleet repos may be absent on a CI runner, so this wrapper
# (1) censuses the fleet workgraph files under $HOME and fails only if ZERO are
# present, (2) runs scripts/run_fleet_courts.py (which already treats missing
# workgraphs as non-failing MISSING rows), and (3) adjudicates which failures
# are absence-attributable (skipped in CI) vs real (still fail the court):
#
#   git-trust   UNRESOLVED with detail "no local checkout for owning repo"
#               -> absence-class, degraded skip. Any other UNRESOLVED
#               (cat-file failure on a repo that IS present) is a real failure.
#   agent-cards repo status ABSENT -> absence-class. Status FAIL (real card
#               violations in a present repo) still fails the court.
#   workgraphs  MISSING rows are already non-failing in the runner; a missing
#               ~/ggen_igniter shapes pack makes the court vacuous, reported as
#               DEGRADED (not evidence), never a silent pass.
#   f5ea-graph  fully in-repo; runner verdict propagated as-is.
#
# scripts/run_fleet_courts.py has no skip flag, so none is passed -- the
# degraded handling lives entirely in this wrapper. No mocks: real subprocesses
# over real fleet state.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"

TMP="${RUNNER_TEMP:-/tmp}/fleet-courts-ci.$$"
mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT

# Fleet workgraph targets, mirroring FLEET_WORKGRAPHS in
# scripts/run_fleet_courts.py. Keep in sync.
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

echo "::group::fleet-courts: sibling workgraph census"
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
  echo "FLEET_COURTS_NO_SIBLINGS: zero fleet workgraphs present under \$HOME;"
  echo "the fleet courts have no subject to observe. Failing."
  exit 1
fi
echo "::endgroup::"

echo "::group::fleet-courts: absence detail for git-trust adjudication"
# The runner's git-trust aggregate does not carry per-SHA details, so run
# git_trust_court.py once more over the present workgraphs to classify each
# UNRESOLVED as absence-class vs real.
GT_FILES=()
for rel in "${FLEET_WORKGRAPHS[@]}"; do
  [ -f "$HOME/$rel" ] && GT_FILES+=(--file "$HOME/$rel")
done
python3 scripts/git_trust_court.py "${GT_FILES[@]}" \
  --json "$TMP/git-trust-detail.json" \
  >"$TMP/git-trust-stdout.txt" 2>"$TMP/git-trust-stderr.txt"
GT_RC=$?
echo "git_trust_court.py exit: $GT_RC (adjudicated below)"
echo "::endgroup::"

echo "::group::fleet-courts: run_fleet_courts.py"
RUNNER_RC=0
python3 scripts/run_fleet_courts.py --json-out "$TMP/report.json" \
  >"$TMP/table.txt" 2>"$TMP/runner-stderr.txt" || RUNNER_RC=$?
cat "$TMP/table.txt"
if [ "$RUNNER_RC" -ne 0 ]; then
  echo "runner exit: $RUNNER_RC (see $TMP/runner-stderr.txt above)"
  cat "$TMP/runner-stderr.txt" || true
fi
echo "::endgroup::"

echo "::group::fleet-courts: degraded adjudication"
ADJ_RC=0
python3 - "$TMP/report.json" "$TMP/git-trust-detail.json" <<'PYEOF' || ADJ_RC=$?
import json, sys

report = json.load(open(sys.argv[1]))
gt = json.load(open(sys.argv[2]))
failures = []
degraded = []

# --- git-trust: absence-class UNRESOLVED skipped, real ones fail
real_unresolved = 0
absent_unresolved = 0
for wg in gt.get("workgraphs", []):
    for r in wg.get("results", []):
        if r["verdict"] == "UNRESOLVED":
            if r.get("detail") == "no local checkout for owning repo":
                absent_unresolved += 1
            else:
                real_unresolved += 1
                failures.append(
                    f"git-trust: real UNRESOLVED {r['sha']} "
                    f"({r['owning_repo']}): {r.get('detail')}"
                )
if real_unresolved:
    pass  # already recorded above
if absent_unresolved:
    degraded.append(f"git-trust: {absent_unresolved} absence-class UNRESOLVED (skipped)")

# --- per-court adjudication of the runner report
for c in report.get("courts", []):
    name = c["court"]
    verdict = c.get("verdict")
    if name == "workgraphs":
        non_missing = [r for r in c.get("repos", []) if r.get("status") != "MISSING"]
        if not non_missing:
            degraded.append("workgraphs: zero present workgraphs observed (vacuous)")
        elif verdict in ("PASS", "STYLE-ONLY"):
            pass
        else:
            failures.append(f"workgraphs: verdict {verdict}")
    elif name == "agent-cards":
        observed = [r for r in c.get("repos", []) if r.get("status") != "ABSENT"]
        if not observed:
            degraded.append("agent-cards: all repos ABSENT (vacuous)")
        for r in c.get("repos", []):
            if r.get("status") == "FAIL":
                failures.append(f"agent-cards: {r['repo']}: real card violations")
    elif name == "f5ea-graph":
        if verdict != "PASS":
            failures.append(f"f5ea-graph: verdict {verdict}")
    elif name == "git-trust":
        # runner verdict for git-trust is delegated to the direct
        # git_trust_court.py adjudication above (absence-aware)
        pass

for d in degraded:
    print(f"DEGRADED: {d}")
for f in failures:
    print(f"FAIL: {f}")
print(f"fleet-courts degraded overall: "
      f"{'FAIL' if failures else 'PASS'} "
      f"({len(degraded)} degraded skips, {len(failures)} real failures)")
sys.exit(1 if failures else 0)
PYEOF
echo "::endgroup::"

echo "::group::fleet-courts: report json sanity"
python3 -m json.tool "$TMP/report.json" > /dev/null || exit 1
echo "::endgroup::"

exit "$ADJ_RC"
