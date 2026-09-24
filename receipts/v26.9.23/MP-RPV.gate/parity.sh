#!/usr/bin/env bash
# Per-file exit of the unified default profile, validate_receipt.py and the durable profile.
# Run from the pack dir: bash parity.sh > parity.<sha>.tsv
V=$PWD/generated/unified_receipt_validator.py
for f in /Users/sac/wt/v26922/fri/xaas-int/docs/sjira/v26.9.23/receipts/*.json /Users/sac/wt/v26922/fri/xaas-int/receipts/v26.9.23/*.json /Users/sac/wt/v26922/fri/ggen_igniter-int/receipts/v26.9.23/*.json qualification/fixtures/dfcm_fleet_v1/*.json; do
  a=0; python3 $V $f --contract=dfcm_fleet_v1 >/dev/null 2>&1 || a=$?
  b=0; python3 /Users/sac/.claude/dfcm/validate_receipt.py $f >/dev/null 2>&1 || b=$?
  d=0; python3 $V $f --contract=dfcm_fleet_v1 --require-durable --repo-map seanchatmangpt/xaas=/Users/sac/wt/v26922/fri/xaas-int --repo-map seanchatmangpt/ggen_igniter=/Users/sac/wt/v26922/fri/ggen_igniter-int >/dev/null 2>&1 || d=$?
  echo "unified=$a fleet=$b durable=$d $f"
done
