#!/bin/sh
# Gate 000 -- the wave-1 failure mode, mechanically refused.
#
# Templates must not bake target module names: every collaborator module is a
# chi:SuiteConfig binding resolved by queries/courts.rq and rendered by the
# template. Any literal "AshA2A.*" module reference in templates/ fails this
# gate, because a hardcoded module name makes the pack's courts un-admissible
# against any target other than the one the template author happened to have.
#
# ASK-equivalent: true (violation found) = refuse; exit 0 = pass.
set -eu

cd "$(dirname "$0")/.."

if [ ! -d templates ]; then
  echo "gates/000: no templates/ directory" >&2
  exit 1
fi

hits=$(grep -rn 'AshA2A\.' templates/ || true)

if [ -n "$hits" ]; then
  echo "gates/000 FAIL: hardcoded AshA2A.* module names in templates/:" >&2
  echo "$hits" >&2
  echo "Fix: move every module reference into chi:SuiteConfig bindings in ontology.ttl and render {{ bindings }}." >&2
  exit 1
fi

echo "gates/000 ok: no hardcoded AshA2A.* module names in templates/"
