#!/bin/bash
# SessionStart hook for Claude Code on the web: make the marketplace's
# local-first checks runnable out of the box in a fresh cloud container.
#
#   python3 scripts/marketplace.py validate|catalog|fingerprint   (stdlib only)
#   python3 -m pytest tests/ scripts/                              (needs the deps below)
#
# pyoxigraph + rdflib give the pack gate courts (e.g.
# tests/test_kubernetes_privilege_gate.py) two independent SPARQL engines, so
# they run instead of skipping. The pinned ggen binary is attempted best-effort
# through the admitted installer: environments whose network policy blocks
# GitHub release assets still get every check that does not shell out to ggen.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"

python3 -m pip install --quiet --disable-pip-version-check --root-user-action=ignore \
  'pytest>=8' 'rdflib>=7,<8' 'pyoxigraph>=0.4'

admitted="${TMPDIR:-/tmp}/ggen-marketplace-admitted.json"
if bash scripts/admit-config.sh marketplace.toml "${admitted}" >/dev/null 2>&1; then
  if ggen_bin="$(bash scripts/install-ggen.sh "${admitted}" 2>/dev/null)" && [ -x "${ggen_bin}" ]; then
    echo "export PATH=\"$(dirname "${ggen_bin}"):\$PATH\"" >> "${CLAUDE_ENV_FILE:-/dev/null}"
    echo "session-start: ggen installed at ${ggen_bin}"
  else
    echo "session-start: pinned ggen release not reachable (network policy?); ggen-dependent tests will fail until it is"
  fi
  echo "export GGEN_MARKETPLACE_ADMITTED_CONFIG=\"${admitted}\"" >> "${CLAUDE_ENV_FILE:-/dev/null}"
fi
