#!/usr/bin/env bash
# G14 gate runner: exit-checked SPARQL gates over ontology.ttl.
set -euo pipefail
cd "$(dirname "$0")/.."
for g in gates/*.rq; do
  ggen gate run --query "$g" --ontology ontology.ttl || { echo "GATE FAIL: $g"; exit 1; }
done
echo ALL_GATES_PASS
