#!/bin/sh
# Gate: wasm_abi_doc_drift.sh — ABI-document vs module export drift court.
#
# Consolidates:
#   wasm4pm/crates/wasm4pm-ex4pm-bindings/scripts/gen_abi.py
#     (regenerates docs/abi/ex4pm-bindings.abi.json; CI fails on drift)
#   wasm4pm/crates/wasm4pm-ex4pm-bindings/tests/abi_roundtrip.rs
#     (exact exported-symbol-name resolution: a renamed #[export_name] breaks
#      the host the same way at call_function time)
#   graphlaw/tests/wasm_abi.rs (drives every op through the JSON ABI).
#
# LAW GUARDED: the ABI document is a projection of the module's export
# section, not an independent hand-edited artifact. This gate re-derives the
# module's export list with the same stdlib section parser the zero-imports
# gate vendors (gate 1), reads the ABI document's declared exports, and fails
# on drift in EITHER direction:
#   doc-declared export absent from the module  -> stale doc (renamed/removed
#     export_name) — the Wasmex host would fail at call time;
#   module export absent from the doc (and not explicitly ignored) ->
#     undeclared surface (new export never admitted into the contract).
# Ignored prefixes must be declared explicitly on the command line; the gate
# never silently prunes.
#
# Usage:
#   wasm_abi_doc_drift.sh --abi ABI.json --module FILE.wasm
#                         [--ignore-prefix name]...
#     --abi            generated ABI JSON document. Accepted shapes:
#                        {"exports": [ "name", ... ]}
#                        {"exports": [ {"export": "name", ...}, ... ]}
#                        {"exports": [ {"name": "name", ...}, ... ]}
#     --module         the .wasm whose export section is the ground truth
#     --ignore-prefix  module exports starting with this prefix are exempt
#                      from the module->doc direction (repeatable, e.g.
#                      memory, __). Doc->module direction is never exempted.
#
# Exit codes: 0 = no drift; 1 = drift (stale or undeclared surface);
#             2 = usage error / malformed abi json / malformed wasm.
set -u

ABI=""
MODULE=""
IGNORE_PREFIXES=""

usage() { sed -n '2,44p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --abi)           [ $# -ge 2 ] || usage; ABI="$2";  shift ;;
    --module)        [ $# -ge 2 ] || usage; MODULE="$2"; shift ;;
    --ignore-prefix) [ $# -ge 2 ] || usage; IGNORE_PREFIXES="$IGNORE_PREFIXES $2"; shift ;;
    -h|--help)       usage ;;
    *) echo "wasm_abi_doc_drift: unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done
[ -n "$ABI" ] && [ -n "$MODULE" ] || usage
[ -f "$ABI" ]    || { echo "wasm_abi_doc_drift: no such abi doc: $ABI" >&2; exit 2; }
[ -f "$MODULE" ] || { echo "wasm_abi_doc_drift: no such module: $MODULE" >&2; exit 2; }

ABI="$ABI" MODULE="$MODULE" IGNORE_PREFIXES="$IGNORE_PREFIXES" python3 - <<'PYEOF'
import json, os, sys

# --- vendored section parser (same lineage as gate 1; wasm_imports.py) ------
def leb(b, i):
    r = s = 0
    while True:
        x = b[i]
        i += 1
        r |= (x & 0x7F) << s
        s += 7
        if not x & 0x80:
            return r, i

def name(b, i):
    n, i = leb(b, i)
    return b[i:i + n].decode("utf-8", "replace"), i + n

def limits(b, i):
    flag, i = leb(b, i)
    _, i = leb(b, i)
    if flag & 1:
        _, i = leb(b, i)
    return i

def parse_exports(b):
    if b[:4] != b"\0asm":
        raise ValueError("not a wasm module")
    i, exports = 8, []
    while i < len(b):
        sid = b[i]
        size, i = leb(b, i + 1)
        end = i + size
        if sid == 7:
            n, j = leb(b, i)
            for _ in range(n):
                nm, j = name(b, j)
                j += 1
                _, j = leb(b, j)
                exports.append(nm)
        i = end
    return exports

def doc_export_names(doc):
    ex = doc.get("exports")
    if ex is None:
        raise ValueError("abi doc has no 'exports' array")
    names = []
    for e in ex:
        if isinstance(e, str):
            names.append(e)
        elif isinstance(e, dict):
            for key in ("export", "name"):
                if key in e:
                    names.append(str(e[key]))
                    break
            else:
                raise ValueError("export entry lacks 'export'/'name': %r" % (e,))
        else:
            raise ValueError("unsupported export entry: %r" % (e,))
    return names

try:
    with open(os.environ["MODULE"], "rb") as f:
        module_exports = parse_exports(f.read())
except (ValueError, IndexError) as e:
    print("GATE wasm_abi_doc_drift: REFUSED(malformed_wasm): %s" % e, file=sys.stderr)
    sys.exit(2)
try:
    with open(os.environ["ABI"]) as f:
        doc_exports = doc_export_names(json.load(f))
except (ValueError, KeyError) as e:
    print("GATE wasm_abi_doc_drift: REFUSED(malformed_abi_doc): %s" % e, file=sys.stderr)
    sys.exit(2)

ignore = tuple(os.environ["IGNORE_PREFIXES"].split())
module_set = set(module_exports)
doc_set = set(doc_exports)

print("GATE wasm_abi_doc_drift: abi=%s module=%s" % (os.environ["ABI"], os.environ["MODULE"]))
print("  doc declares %d exports; module carries %d exports" % (len(doc_exports), len(module_exports)))

# export_count sanity when the doc carries it (gen_abi.py always does)
try:
    with open(os.environ["ABI"]) as f:
        declared = json.load(f).get("export_count")
    if declared is not None and declared != len(doc_exports):
        print("  VIOLATION export_count_mismatch doc.export_count=%d but exports[]=%d"
              % (declared, len(doc_exports)))
        print("GATE wasm_abi_doc_drift: REFUSED(drift)")
        sys.exit(1)
except (ValueError, KeyError):
    pass

drift = []
for n in sorted(doc_set - module_set):
    drift.append("stale_doc_export %s (declared in doc, absent from module)" % n)
for n in sorted(module_set - doc_set):
    if n.startswith(ignore):
        print("  ignored module export (explicit prefix): %s" % n)
    else:
        drift.append("undeclared_module_export %s (carried by module, absent from doc)" % n)

for d in drift:
    print("  VIOLATION %s" % d)

if drift:
    print("GATE wasm_abi_doc_drift: REFUSED(drift: %d item(s))" % len(drift))
    sys.exit(1)
print("GATE wasm_abi_doc_drift: PASS (abi doc matches module export section)")
sys.exit(0)
PYEOF
exit $?
