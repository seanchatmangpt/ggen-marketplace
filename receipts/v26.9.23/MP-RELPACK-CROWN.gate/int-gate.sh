#!/usr/bin/env bash
# MP-RELPACK-CROWN lane gate rebound from the lane worktree to the int worktree pack.
# Usage: int-gate.sh <marketplace checkout root>
cd "${1:-.}/packs/chatman-ecosystem-release-pack" && P=$PWD && python3 bin/run-gates.py qualification/imported-crown.positive.ttl gates && for f in stale-r0 llm1 unreceipted-null drop-gate foreign-subject gi-mismatch; do ! python3 bin/run-gates.py qualification/imported-crown.$f.ttl gates || { echo VACUOUS $f; exit 1; }; done && F=qualification/fixtures/positive-receipts && python3 bin/import-crown-lift.py $F $(cat $F/XAAS_SHA) $(cat $F/GI_SHA) | cmp - qualification/imported-crown.positive.ttl && python3 bin/run-gates.py qualification/consumer.ttl gates
