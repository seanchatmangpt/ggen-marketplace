#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Non-Ash Chicago fixture for qri-consumer-binding-pack (profile node-wasi). Real ggen, real pyshacl,
# real wasm, real node:wasi, zero mocks. Generated host only: no hand-written ABI glue.
# Env overrides: AFFIDAVIT_DIR ASH_AFFIDAVIT_DIR PYTHON GGEN NODE WORK MKT_TIP MIX_BUILD_ROOT
set -uo pipefail
PACK="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO="$(cd "$PACK/../.." && pwd)"
AFF="${AFFIDAVIT_DIR:-/Users/sac/affidavit}"
ASH="${ASH_AFFIDAVIT_DIR:-/Users/sac/ash_affidavit}"
PY="${PYTHON:-python3.11}"; NODE="${NODE:-node}"; GGEN="${GGEN:-$(command -v ggen)}"
WORK="${WORK:-$(mktemp -d "${TMPDIR:-/tmp}/qcb-chicago.XXXXXX")}"
FX="$PACK/fixtures/node-wasi"
step() { printf '\n== step %s: %s\n' "$1" "$2"; }
fail() { printf 'FIXTURE FAILED at step %s: %s\n' "$1" "$2" >&2; exit 1; }
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
mkdir -p "$WORK"; echo "work dir: $WORK"

step 0 "probe node:wasi against the 4 preview1 imports"
WASM_SRC="$AFF/affidavit-wasm/target/wasm32-wasip1/wasm/affidavit_wasm.wasm"
[ -f "$WASM_SRC" ] || WASM_SRC="$ASH/priv/affidavit/affidavit.wasm"
echo "node $($NODE --version); wasm source $WASM_SRC"
$NODE --input-type=module -e '
import {readFileSync} from "node:fs"; import {WASI} from "node:wasi";
const m = await WebAssembly.compile(readFileSync(process.argv[1]));
const imps = WebAssembly.Module.imports(m).map(i => i.module+"::"+i.name).sort();
const w = new WASI({version:"preview1"});
const inst = await WebAssembly.instantiate(m, w.getImportObject()); w.initialize(inst);
console.log(JSON.stringify({imports: imps, abi: inst.exports.af_abi_version()}));
' "$WASM_SRC" || fail 0 "node:wasi cannot instantiate the module (fallback: Rust wasmtime host)"

step 1 "record subject identities (scratch export of origin/main tip + pack)"
MKT_TIP="${MKT_TIP:-80d429f13cc887f66855ba4029f6d83aa3a8098f}"
echo "marketplace origin/main tip (export source): $MKT_TIP"
echo "pack: $(basename "$PACK") version $(grep -m1 '^version' "$PACK/pack.toml")"
(cd "$REPO" && $PY scripts/marketplace.py fingerprint | tail -1)
echo "affidavit HEAD: $(git -C "$AFF" rev-parse HEAD 2>/dev/null || echo UNKNOWN)"
echo "ggen: $($GGEN --version)"

step 2 "take artifact-pin.json, op-examples.json and the wasm from the affidavit checkout"
cp "$AFF/affidavit-wasm/registry/artifact-pin.json" "$WORK/artifact-pin.json"
cp "$AFF/affidavit-wasm/registry/op-examples.json" "$WORK/op-examples.json"
cp "$WASM_SRC" "$WORK/affidavit.wasm"
WASM_SHA="$(sha "$WORK/affidavit.wasm")"; WASM_BYTES="$(wc -c < "$WORK/affidavit.wasm" | tr -d ' ')"
REG_SHA="$(sha "$AFF/affidavit-wasm/registry/capability-registry.json")"
$PY - "$WORK/artifact-pin.json" "$WASM_SHA" "$WASM_BYTES" "$REG_SHA" <<'PYEOF' || fail 2 "wasm does not equal the affidavit pin record"
import json, sys
pin = json.load(open(sys.argv[1]))
assert pin["sha256"] == sys.argv[2], (pin["sha256"], sys.argv[2])
assert pin["bytes"] == int(sys.argv[3]), (pin["bytes"], sys.argv[3])
assert pin["registry_sha256"] == sys.argv[4], (pin["registry_sha256"], sys.argv[4])
print("pin == wasm:", pin["sha256"], pin["bytes"], "registry", pin["registry_sha256"], "ops", len(pin["ops"]))
PYEOF

step 3 "fixture binding.ttl: contract, profile node-wasi, pin, authorityCeiling NONE (pin facts == pin record)"
cp "$FX/binding.ttl" "$WORK/binding.ttl"
grep -q "$WASM_SHA" "$WORK/binding.ttl" && grep -q "\"$WASM_BYTES\"" "$WORK/binding.ttl" && grep -q "$REG_SHA" "$WORK/binding.ttl" \
  || fail 3 "binding pin facts differ from the affidavit pin record"
grep -q 'qcb:authorityCeiling "NONE"' "$WORK/binding.ttl" && grep -q 'qcb:profileId "node-wasi"' "$WORK/binding.ttl" \
  || fail 3 "binding is not node-wasi / ceiling NONE"
echo "binding pin facts match: sha256 $WASM_SHA bytes $WASM_BYTES registry $REG_SHA"

step 4 "admission: gate court, SHACL, gates give zero rows"
(cd "$REPO" && $PY scripts/check_gate_witness_courts.py) > "$WORK/court.json" || fail 4 "gate court"
$PY -c 'import json,sys; d=json.load(open(sys.argv[1])); c=[x for x in d["courts"] if x["pack"]=="qri-consumer-binding-pack"][0]; print("court:", d["standing"], "| qcb cases", c["case_count"], c["standing"]); assert d["standing"]==c["standing"]=="ALIVE"' "$WORK/court.json" || fail 4 "court not ALIVE"
$PY - "$PACK" "$WORK/binding.ttl" <<'PYEOF' || fail 4 "admission produced rows or SHACL violations"
import sys, pathlib
sys.path.insert(0, sys.argv[1] + "/runners")
from rdflib import Graph
import semantic_runner, pyshacl
pack = pathlib.Path(sys.argv[1]); g = Graph().parse(sys.argv[2])
rows = [(p.stem, str(r[1])) for p in sorted((pack/"gates").glob("*.rq")) for r in semantic_runner.gate_rows(p, g)]
print("gate rows:", rows); assert rows == []
ok, _, text = pyshacl.validate(g, shacl_graph=Graph().parse(pack/"shapes"/"qcb.shacl.ttl"), inference="none")
print("SHACL conforms:", ok); assert ok
PYEOF

step 5 "ggen sync in a scratch capsule twice (consume.py); cmp the outputs"
$PY "$PACK/runners/consume.py" --binding "$WORK/binding.ttl" --out "$WORK/out1" > "$WORK/consume1.json" || fail 5 "consume run 1"
$PY "$PACK/runners/consume.py" --binding "$WORK/binding.ttl" --out "$WORK/out2" > "$WORK/consume2.json" || fail 5 "consume run 2"
cmp "$WORK/consume1.json" "$WORK/consume2.json" && diff -r "$WORK/out1" "$WORK/out2" || fail 5 "replay mismatch"
$PY -c 'import json,sys; d=json.load(open(sys.argv[1])); print("profile",d["profile"],"ggen",d["generator_version"]); print("output_digest",d["output_digest"]); print("final_listing_digest",d["final_listing_digest"]); print("files",sorted(d["files"]))' "$WORK/consume1.json"
OUT="$WORK/out1"
[ -f "$OUT/node-wasi/host.mjs" ] || fail 5 "generated host missing"

step 6 "validate projection-receipt.json against the outputs"
$PY - "$OUT" <<'PYEOF' || fail 6 "projection receipt invalid"
import json, sys, hashlib, pathlib
out = pathlib.Path(sys.argv[1]); r = json.load(open(out/"projection-receipt.json"))
assert r["schema"] == "qcb.projection-receipt/1" and r["authority_ceiling"] == "NONE"
for f in r["outputs"]:
    assert hashlib.sha256((out/f["path"]).read_bytes()).hexdigest() == f["sha256"], f["path"]
listed = {f["path"] for f in r["outputs"]}
actual = {str(p.relative_to(out)) for p in out.rglob("*") if p.is_file() and p.name != "projection-receipt.json"}
assert listed == actual, (listed ^ actual)
assert "standing" not in r, "standing must be derived, never stored"
print("receipt ok:", len(listed), "outputs hash-match; ceiling NONE; no stored standing; pack", r["pack_version"], r["pack_content_digest"][:16])
PYEOF

HOST="$OUT/node-wasi/host.mjs"
step 7 "generated host --check: sha256 == pin and af_abi_version == 1"
CHK="$($NODE "$HOST" --check "$WORK/affidavit.wasm")" || fail 7 "host --check refused the real module"
echo "$CHK"
$PY -c 'import json,sys; c=json.loads(sys.argv[1]); assert c["ok"] and c["abi_version"]==1 and c["sha256"]==sys.argv[2] and c["authority"]=="NONE"' "$CHK" "$WASM_SHA" || fail 7 "check payload"

step 8 "tamper copy: typed wasm_digest_mismatch, expected non-zero exit"
cp "$WORK/affidavit.wasm" "$WORK/tampered.wasm"
printf '\xff' | dd of="$WORK/tampered.wasm" bs=1 seek=100 count=1 conv=notrunc 2>/dev/null
TOUT="$($NODE "$HOST" --check "$WORK/tampered.wasm")"; TRC=$?
echo "exit $TRC: $TOUT"
[ "$TRC" -eq 3 ] || fail 8 "tamper exit was $TRC, expected 3"
$PY -c 'import json,sys; d=json.loads(sys.argv[1]); assert d["code"]=="wasm_digest_mismatch" and d["ok"] is False and d["authority"]=="NONE"' "$TOUT" || fail 8 "tamper not typed wasm_digest_mismatch"
echo "typed refusal observed; nothing cached (host holds no state across processes)"

step 9 "drive op-examples through af_alloc/af_call/af_free via the generated host"
$NODE "$FX/drive.mjs" "$HOST" "$WORK/affidavit.wasm" "$WORK/op-examples.json" > "$WORK/node-responses.json" || fail 9 "node drive assertions"
echo "node responses recorded: $($PY -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "$WORK/node-responses.json") ops"
AUTHORITY_WASM="$WORK/affidavit.wasm" AUTHORITY_EXAMPLES="$WORK/op-examples.json" $NODE --test "$OUT/node-wasi/authority-boundary.test.mjs" > "$WORK/authority-test.out" 2>&1 \
  || { tail -30 "$WORK/authority-test.out"; fail 9 "authority-boundary test"; }
grep -E "^. (tests|pass|fail|skipped) " "$WORK/authority-test.out"

step 10 "negative: ambiguous realization and ceiling OBSERVE give typed refusals with zero files"
$PY - "$WORK" <<'PYEOF'
import sys, re, pathlib
w = pathlib.Path(sys.argv[1]); t = (w/"binding.ttl").read_text()
amb = t.replace("qcb:chosenRealization ab:realization ;", "qcb:candidateRealization ab:realization, ab:realizationB ;")
assert amb != t; (w/"ambiguous.ttl").write_text(amb + "\nab:realizationB a qri:Realization .\n")
obs = t.replace('qcb:authorityCeiling "NONE"', 'qcb:authorityCeiling "OBSERVE"', 1)
assert obs != t; (w/"ceiling-observe.ttl").write_text(obs)
PYEOF
for pair in "ambiguous:AMBIGUOUS_REALIZATION" "ceiling-observe:CEILING_NOT_NONE"; do
  name="${pair%%:*}"; code="${pair##*:}"
  ROUT="$($PY "$PACK/runners/consume.py" --binding "$WORK/$name.ttl" --out "$WORK/out-$name")"; RRC=$?
  echo "$name -> exit $RRC $ROUT"
  [ "$RRC" -eq 2 ] || fail 10 "$name exit $RRC, expected 2"
  [ ! -e "$WORK/out-$name" ] || fail 10 "$name wrote files"
  $PY -c 'import json,sys; d=json.loads(sys.argv[1])["refused"]; assert d["code"]==sys.argv[2], d; print("  typed:", d["code"], d["class"], d["broken_term"], d["standing_literal"])' "$ROUT" "$code" || fail 10 "$name not typed $code"
done

step 11 "parity vs the Elixir host (C9), then replay (C7)"
(cd "$ASH" && MIX_BUILD_ROOT="${MIX_BUILD_ROOT:-_build-laneF1}" mix run --no-start "$FX/elixir_replay.exs" "$WORK/op-examples.json") > "$WORK/elixir-responses.raw" 2> "$WORK/elixir.err" \
  || { tail -20 "$WORK/elixir.err"; fail 11 "elixir host replay"; }
tail -1 "$WORK/elixir-responses.raw" > "$WORK/elixir-responses.json"
$PY - "$WORK/node-responses.json" "$WORK/elixir-responses.json" <<'PYEOF' || fail 11 "node != elixir responses"
import json, sys
n = json.load(open(sys.argv[1])); e = json.load(open(sys.argv[2]))
assert sorted(n) == sorted(e), (sorted(n), sorted(e))
# JS parses 1.0 as 1 while Elixir keeps the float: normalize integral floats (decoder artifact, not engine output)
norm = lambda v: ({k: norm(x) for k, x in v.items()} if isinstance(v, dict) else [norm(x) for x in v] if isinstance(v, list)
                  else int(v) if isinstance(v, float) and v.is_integer() else v)
c = lambda v: json.dumps(norm(v), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
bad = [k for k in sorted(n) if c(n[k]) != c(e[k])]
for k in sorted(n): print(f"  {k}: {'EQUAL' if k not in bad else 'DIFFERS'} ({len(c(n[k]))} bytes canonical)")
assert not bad, bad
print("parity: node-wasi == Elixir host for", len(n), "ops")
PYEOF
$PY "$PACK/runners/consume.py" --binding "$WORK/binding.ttl" --out "$WORK/out3" > "$WORK/consume3.json" || fail 11 "replay run"
cmp "$WORK/consume1.json" "$WORK/consume3.json" && diff -r "$OUT" "$WORK/out3" && echo "replay: identical stdout and output tree"
echo "receipt recorded: $OUT/projection-receipt.json"
cp "$OUT/projection-receipt.json" "$WORK/fixture-receipt.json"
echo "authority ceiling NONE throughout; standing is derived elsewhere, not claimed here"
echo; echo "ALL 11 STEPS PASSED (work dir $WORK)"
