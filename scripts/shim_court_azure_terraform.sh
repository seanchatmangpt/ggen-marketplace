#!/usr/bin/env bash
# Shim court: azure-terraform-pack main.tf.tmpl.
# BASELINE(sha256) -> BEFORE(check passes) -> SHIM(mutate) -> AFTER(check must fail) -> RESTORE(sha256 byte-exact).
# Check = render template HCL body with fixture row values, then `terraform test` under mock_provider (plan-only).
# A court that cannot flip is FAIL (VACUOUS GATE); missing terraform/provider is a loud [SKIP], exit 3.
# Self-check (--self-check): corrupts a restore on a temp copy; must exit 1.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMPL="${TMPL:-$ROOT/packs/azure-terraform-pack/templates/main.tf.tmpl}"
sha() { shasum -a 256 "$1" | awk '{print $1}'; }

check() { # $1 = template file ; rc 0 = assertions pass
  local d; d="$(mktemp -d)"
  python3 - "$1" "$d" <<'PY'
import sys,re
t=open(sys.argv[1]).read().split('\n---\n',1)[1]
t=re.sub(r'\{%-?\s*set[^%]*%\}','',t)
fixt={'group.osType':'Linux','group.restartPolicy':'Never','group.ipAddressType':'None',
      'row.label':'fixture','c.name':'c1','c.cpu':'1','c.memory':'1.5','c.command':'true'}
t=re.sub(r'\{%-?\s*for[^%]*%\}','',t); t=re.sub(r'\{%-?\s*endfor\s*-?%\}','',t)
t=re.sub(r'\{\{\s*([\w.]+)\s*\}\}',lambda m:fixt.get(m.group(1),'x'),t)
open(sys.argv[2]+'/main.tf','w').write(t)
PY
  cat > "$d/vars.tf" <<'H'
terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "3.117.1" }
  }
}
provider "azurerm" {
  features {}
}
variable "resource_group_name" { default = "rg" }
variable "location" { default = "eastus" }
variable "name" { default = "n" }
variable "container_image" { default = "img" }
locals { tags = {} }
H
  mkdir -p "$d/tests"
  cat > "$d/tests/c.tftest.hcl" <<'H'
mock_provider "azurerm" {}
run "attrs" {
  command = plan
  assert {
    condition     = azurerm_container_group.this.restart_policy == "Never"
    error_message = "restart_policy drifted"
  }
  assert {
    condition     = azurerm_container_group.this.os_type == "Linux"
    error_message = "os_type drifted"
  }
}
H
  ( cd "$d" && terraform init -backend=false -input=false >/dev/null 2>&1 && terraform test >"$d/out.txt" 2>&1 ); local rc=$?
  tail -3 "$d/out.txt" 2>/dev/null; cp "$d/out.txt" "${CHECK_OUT:-/dev/null}" 2>/dev/null; rm -rf "$d"; return $rc
}

court() { # $1 = template path
  local f="$1" base shim_rc
  base="$(sha "$f")"; echo "BASELINE sha256=$base"
  check "$f"; local b=$?; echo "BEFORE rc=$b"
  [ "$b" -eq 0 ] || { echo "[SKIP] baseline check not green (terraform/provider unavailable or template broken)"; return 3; }
  cp "$f" "$f.court-orig"
  trap '[ -f "$f.court-orig" ] && cp "$f.court-orig" "$f" && rm -f "$f.court-orig"' EXIT INT TERM
  sed 's/restart_policy      = "{{ group.restartPolicy }}"/restart_policy      = "Always" # SHIM-COURT/' "$f.court-orig" > "$f"
  echo "SHIM applied sha256=$(sha "$f")"
  local ao; ao="$(mktemp)"; CHECK_OUT="$ao" check "$f"; local a=$?; echo "AFTER rc=$a"
  grep -q "restart_policy drifted" "$ao" || a=0; rm -f "$ao"
  cp "$f.court-orig" "$f"
  [ "${CORRUPT_RESTORE:-0}" = 1 ] && echo "# corrupt" >> "$f"
  rm -f "$f.court-orig"
  local after; after="$(sha "$f")"
  if [ "$after" = "$base" ]; then echo "RESTORE sha256=$after MATCH"; else echo "RESTORE sha256=$after MISMATCH"; return 1; fi
  [ "$a" -ne 0 ] || { echo "VACUOUS GATE: shim did not flip the restart_policy assertion"; return 1; }
  echo "COURT PASS"
}

if [ "${1:-}" = "--self-check" ]; then
  t="$(mktemp -d)"; cp "$TMPL" "$t/main.tf.tmpl"
  CORRUPT_RESTORE=1 court "$t/main.tf.tmpl"; rc=$?; rm -rf "$t"
  [ "$rc" -eq 1 ] && { echo "SELF-CHECK PASS (corrupt restore detected)"; exit 0; }
  [ "$rc" -eq 3 ] && { echo "[SKIP] self-check: baseline not green"; exit 3; }
  echo "SELF-CHECK FAIL rc=$rc"; exit 1
fi
court "$TMPL"; exit $?
