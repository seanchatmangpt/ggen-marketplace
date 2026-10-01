#!/usr/bin/env bash
# Court compose-r86-forced-top25-qualification-capsule -- migrated from .github/workflows/compose-r86-forced-top25-qualification-capsule.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Parse public ontology
echo "::group::compose-r86-forced-top25-qualification-capsule: Parse public ontology"
(
set -e
python -c "from rdflib import Graph; Graph().parse('packs/forced-top25-qualification-capsule-pack/ontology.ttl', format='turtle')"
)
echo "::endgroup::"
# --- Execute R86 court
echo "::group::compose-r86-forced-top25-qualification-capsule: Execute R86 court"
(
set -e
pytest -q packs/forced-top25-qualification-capsule-pack/tests/test_r86_qualification_capsule.py
)
echo "::endgroup::"
