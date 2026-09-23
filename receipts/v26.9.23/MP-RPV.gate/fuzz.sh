#!/usr/bin/env bash
# Adversarial inputs (fuzz/*.json) through the validator; no output may contain a traceback.
# Run from a scratch copy of fuzz/: bash fuzz.sh <validator> > fuzz.<sha>.log
# deep.json (not committed) is regenerated here: 100000 nested arrays.
V=$1
[ -f deep.json ] || python3 -c "open('deep.json','w').write('['*100000 + ']'*100000)"
for f in *.json; do for args in "" "--require-durable --repo-map seanchatmangpt/xaas=/Users/sac/wt/v26922/fri/xaas-int"; do
  out=$(python3 $V $f --contract=dfcm_fleet_v1 $args 2>&1); e=$?; tb=clean; echo "$out" | grep -q Traceback && tb=TRACEBACK
  echo "exit=$e $tb $f ${args:+durable}"
done; done
