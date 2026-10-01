#!/bin/sh
# Gate: wasm_zero_imports.sh — WASM import-policy + required-export gate.
#
# Consolidates: wasm4pm/crates/wasm4pm-ex4pm-bindings/scripts/wasm_imports.py
#               (--require-zero-imports + required-export verification)
#               and graphlaw/tests/wasm_abi.rs (the "only wasi_snapshot_preview1
#               imports" assertion, enforced here without a wasm runtime).
#
# LAW GUARDED (wasi-json-abi-pack, gates/060_imports_policy_wasi_only.rq,
#              gates/080_wasi_import_closure.rq):
#   a wja:WasmModule's import surface is exactly the wasi_snapshot_preview1
#   module (or empty); every named host function must be an enumerated
#   wja:WasiImport. Default posture is ZERO imports (the ex4pm-bindings
#   posture); --allow-wasi opts in to the WASI-only policy (the graphlaw /
#   affidavit posture). Every export the ABI contract names must exist in the
#   module's export section.
#
# Usage:
#   wasm_zero_imports.sh [--allow-wasi] [--allow-import mod.name]...
#                        [--require export]... FILE.wasm
#     --allow-wasi            permit imports from wasi_snapshot_preview1 only
#     --allow-import mod.name permit exactly this import (repeatable; also
#                             accepts comma-separated lists)
#     --require export        this export name must be present (repeatable;
#                             also accepts comma-separated lists)
#
# Exit codes: 0 = pass; 1 = policy violation (disallowed import or missing
# required export); 2 = usage error or malformed wasm.
# Self-contained: POSIX shell + python3 stdlib. Slow-rail verification script.
set -u

ALLOW_WASI=0
REQUIRE=""
ALLOWED=""
FILE=""
WASI_MODULE="wasi_snapshot_preview1"

usage() { sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --allow-wasi)    ALLOW_WASI=1 ;;
    --allow-import)  [ $# -ge 2 ] || usage; ALLOWED="$ALLOWED $2"; shift ;;
    --require)       [ $# -ge 2 ] || usage; REQUIRE="$REQUIRE $2"; shift ;;
    -h|--help)       usage ;;
    -*)              echo "wasm_zero_imports: unknown flag: $1" >&2; exit 2 ;;
    *)               [ -z "$FILE" ] || { echo "wasm_zero_imports: exactly one FILE.wasm" >&2; exit 2; }
                     FILE="$1" ;;
  esac
  shift
done
[ -n "$FILE" ] || usage
[ -f "$FILE" ] || { echo "wasm_zero_imports: no such file: $FILE" >&2; exit 2; }

FILE="$FILE" ALLOW_WASI="$ALLOW_WASI" WASI_MODULE="$WASI_MODULE" \
REQUIRE="$REQUIRE" ALLOWED="$ALLOWED" python3 - <<'PYEOF'
import os, sys

# --- vendored section parser (wasm4pm wasm_imports.py, stdlib-only) ---------
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

def parse(b):
    if b[:4] != b"\0asm":
        raise ValueError("not a wasm module")
    i, imports, exports = 8, [], []
    while i < len(b):
        sid = b[i]
        size, i = leb(b, i + 1)
        end = i + size
        if sid == 2:
            n, j = leb(b, i)
            for _ in range(n):
                mod, j = name(b, j)
                nm, j = name(b, j)
                kind = b[j]
                j += 1
                if kind == 0:
                    _, j = leb(b, j)
                elif kind == 1:
                    j += 1
                    j = limits(b, j)
                elif kind == 2:
                    j = limits(b, j)
                elif kind == 3:
                    j += 2
                elif kind == 4:
                    j += 1
                    _, j = leb(b, j)
                else:
                    raise ValueError("unknown import kind %d" % kind)
                imports.append((mod, nm))
        elif sid == 7:
            n, j = leb(b, i)
            for _ in range(n):
                nm, j = name(b, j)
                j += 1
                _, j = leb(b, j)
                exports.append(nm)
        i = end
    return imports, exports

# --- gate policy ------------------------------------------------------------
def split_list(items):
    out = []
    for it in items:
        out.extend(x for x in it.split(",") if x)
    return out

allow_wasi = os.environ["ALLOW_WASI"] == "1"
wasi_module = os.environ["WASI_MODULE"]
required = split_list(os.environ["REQUIRE"].split())
allowed = set(split_list(os.environ["ALLOWED"].split()))

try:
    with open(os.environ["FILE"], "rb") as f:
        imports, exports = parse(f.read())
except (ValueError, IndexError, KeyError) as e:
    print("GATE wasm_zero_imports: REFUSED(malformed_wasm): %s" % e, file=sys.stderr)
    sys.exit(2)

print("GATE wasm_zero_imports: module=%s imports=%d exports=%d"
      % (os.environ["FILE"], len(imports), len(exports)))

violations = []
for mod, nm in imports:
    key = "%s.%s" % (mod, nm)
    if mod == wasi_module and allow_wasi:
        print("  allowed import (wasi): %s" % key)
    elif key in allowed:
        print("  allowed import (explicit): %s" % key)
    else:
        violations.append("disallowed_import %s" % key)

export_set = set(exports)
for req in required:
    if req not in export_set:
        violations.append("missing_required_export %s" % req)

for v in sorted(violations):
    print("  VIOLATION %s" % v)

if violations:
    print("GATE wasm_zero_imports: REFUSED(%d violation(s))" % len(violations))
    sys.exit(1)
print("GATE wasm_zero_imports: PASS")
sys.exit(0)
PYEOF
exit $?
