#!/usr/bin/env bash
# Chicago-style pack qualification (real ggen, real rdflib, real files; no mocks).
# Everything runs in a scratch copy; the committed tree is never written.
#   1. qualification/consumer.ttl passes the explicit runner.
#   2. consumer-v26.9.23 passes native `ggen sync run` twice with byte-identical
#      outputs, passes the runner, and renders 16 disposed legacy roles.
#   3. control = consumer-v26.9.23 minus the CE orders import (the mutant base)
#      passes both executors; M6's committed file differs from the control render
#      in exactly the forged standing line.
#   4. a valid explicit decision (positive witness) is admitted and rendered.
#   5. every mutant in mutants/EXPECTED.tsv is refused by the declared executor
#      with the declared code, gate and reason.
# Usage: qualification/qualify.sh   (GGEN=<ggen binary> to override)
set -u
P=$(cd "$(dirname "$0")/.." && pwd)
GGEN=${GGEN:-ggen}
W=$(mktemp -d "${TMPDIR:-/tmp}/relpack-qual.XXXXXX")
fail=0
ok() { printf 'PASS %s\n' "$*"; }
no() { printf 'FAIL %s\n' "$*"; fail=1; }

# Copy a consumer dir into scratch and point its path pack at this pack (absolute).
# A third argument "keep-out" preserves a committed out/ fixture (M6); otherwise
# any previous sync consequence is dropped so every render is fresh.
stage() {
  cp -R "$1" "$2"
  rm -rf "$2/.ggen-v2" "$2/.ggen" "$2/ggen.lock"
  if [ "${3:-}" != keep-out ]; then rm -rf "$2/out"; fi
  python3 - "$2/ggen.toml" "$P" <<'PY'
import re, sys
path, pack = sys.argv[1], sys.argv[2]
text = open(path).read()
text, n = re.subn(r'path = "[^"]+"', f'path = "{pack}"', text)
assert n == 1, n
open(path, "w").write(text)
PY
}

runner() { python3 "$P/bin/run-gates.py" "$1/release.ttl" "$P/gates" > "$2" 2>&1; }

# 1
if python3 "$P/bin/run-gates.py" "$P/qualification/consumer.ttl" "$P/gates" > "$W/consumer.log" 2>&1; then
  ok "consumer.ttl runner"; else no "consumer.ttl runner (see $W/consumer.log)"; fi

# 2
stage "$P/qualification/consumer-v26.9.23" "$W/c23"
if (cd "$W/c23" && "$GGEN" sync run > "$W/c23-1.json" 2> "$W/c23-1.err"); then ok "c23 sync 1"; else no "c23 sync 1"; fi
cp -R "$W/c23/out" "$W/c23-out1"
if (cd "$W/c23" && "$GGEN" sync run > "$W/c23-2.json" 2> "$W/c23-2.err"); then ok "c23 sync 2"; else no "c23 sync 2"; fi
if diff -r "$W/c23/out" "$W/c23-out1" > /dev/null; then ok "c23 renders byte-identical"; else no "c23 renders differ"; fi
if runner "$W/c23" "$W/c23-runner.log"; then ok "c23 runner"; else no "c23 runner"; fi
if python3 - "$W/c23/out" <<'PY'
import sys, tomllib
from pathlib import Path
from rdflib import Graph, URIRef
out = Path(sys.argv[1])
docs = {p.name: tomllib.loads(p.read_text()) for p in out.glob("*.toml")}
xw = docs["legacy-role-crosswalk.toml"]
roles = xw["role"]
assert xw["crosswalk"]["role_count"] == 16 == len(roles) == len({r["legacy_role"] for r in roles}), len(roles)
assert all(r["boundary"] in {"REQUIRED", "SUCCESSOR", "BLOCKED", "UNSUPPORTED", "REFUSED"} for r in roles)
assert all(r["reason"] and (r["derived_by"] or r["decided_by"]) for r in roles)
manifest = docs["manifest.toml"]
fields = {"id", "repository", "ref", "ref_check", "sha", "role", "disposition", "standing", "required", "depends_on"}
assert all(fields <= set(c) for c in manifest["components"]), manifest["components"]
mapped = {c["release_role"] for c in docs["constitutional-role-crosswalk.toml"]["crosswalk"]}
assert {c["role"] for c in manifest["components"] if c["required"]} <= mapped
assert docs["requirements.toml"]["requirements"]["row_count"] == len(docs["requirements.toml"]["requirement"]) > 0
g = Graph().parse(out / "crosswalk.ttl")
er = "http://seanchatmangpt.github.io/packs/chatman-ecosystem-release#"
assert len(set(g.subjects(URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), URIRef(er + "RoleDisposition")))) == 16
print("rendered: 16 roles disposed, manifest fields complete, roles mapped, requirements", docs["requirements.toml"]["requirements"]["row_count"])
PY
then ok "c23 rendered contents"; else no "c23 rendered contents"; fi

# 3
stage "$P/qualification/consumer-v26.9.23" "$W/control"
sed -i.bak 's#, "imports/ce23-orders.ttl"##' "$W/control/ggen.toml" && rm "$W/control/ggen.toml.bak" "$W/control/imports/ce23-orders.ttl"
if (cd "$W/control" && "$GGEN" sync run > "$W/control.json" 2> "$W/control.err"); then ok "control sync"; else no "control sync"; fi
if runner "$W/control" "$W/control-runner.log"; then ok "control runner"; else no "control runner"; fi
changed=$(diff "$W/control/out/manifest.toml" "$P/qualification/mutants/M6-hand-edited-rendered-file/out/manifest.toml" | grep -c '^[<>]')
if [ "$changed" = 2 ] && diff "$W/control/out/manifest.toml" "$P/qualification/mutants/M6-hand-edited-rendered-file/out/manifest.toml" | grep -q '^> standing = "ALIVE"'; then
  ok "M6 differs from the control render only in the forged standing"; else no "M6 fixture drifted from the control render ($changed changed lines)"; fi

# 4
stage "$W/control" "$W/decision"
cat >> "$W/decision/release.ttl" <<'TTL'

<https://ggen.dev/marketplace/qualification/chatman-ecosystem-release/v26.9.23/release/decision/formal-proof> a er:RoleDisposition ;
    er:legacyRole "formal-proof" ;
    er:sourceRelease <https://github.com/seanchatmangpt/chatman-ecosystem/release/v26.9.1> ;
    er:targetRelease <https://ggen.dev/marketplace/qualification/chatman-ecosystem-release/v26.9.23/release> ;
    er:boundary er:ROLE_BLOCKED ;
    er:reason "qualification witness: an explicit decision for a repository absent from the fleet classification" ;
    er:decidedBy "qualification:positive-witness" .
TTL
if (cd "$W/decision" && "$GGEN" sync run > "$W/decision.json" 2> "$W/decision.err") && runner "$W/decision" "$W/decision-runner.log" \
  && python3 - "$W/decision/out" <<'PY'
import sys, tomllib
from pathlib import Path
out = Path(sys.argv[1])
rows = {r["legacy_role"]: r for r in tomllib.loads((out / "legacy-role-crosswalk.toml").read_text())["role"]}
assert len(rows) == 16
fp = rows["formal-proof"]
assert (fp["boundary"], fp["decided_by"], fp["derived_by"]) == ("BLOCKED", "qualification:positive-witness", ""), fp
assert tomllib.loads((out / "role-derivations.toml").read_text())["derivations"]["decided_count"] == 1
PY
then ok "explicit decision admitted and rendered"; else no "explicit decision witness"; fi

# 5
while IFS=$'\t' read -r name code gate want reason; do
  case "$name" in ''|'#'*) continue ;; esac
  stage "$P/qualification/mutants/$name" "$W/m-$name" keep-out
  (cd "$W/m-$name" && "$GGEN" sync run > "$W/m-$name.json" 2> "$W/m-$name.err"); r=$?
  runner "$W/m-$name" "$W/m-$name.runner.log"; g=$?
  verdict=ok
  [ "$r" -ne 0 ] && grep -q "\[$code\]" "$W/m-$name.err" || verdict=no
  if [ "$gate" != "-" ]; then grep -q "gate \`$gate\`" "$W/m-$name.err" || verdict=no; fi
  if [ "$want" = REFUSED ]; then
    [ "$g" -ne 0 ] && grep -q -- "$reason" "$W/m-$name.runner.log" || verdict=no
  else
    [ "$g" -eq 0 ] || verdict=no
  fi
  if [ "$verdict" = ok ]; then ok "$name native=$r[$code] runner=$g"; else no "$name native=$r runner=$g (see $W/m-$name.*)"; fi
done < "$P/qualification/mutants/EXPECTED.tsv"

printf 'QUALIFICATION %s scratch=%s\n' "$([ $fail = 0 ] && echo ALIVE || echo REFUSED)" "$W"
exit $fail
