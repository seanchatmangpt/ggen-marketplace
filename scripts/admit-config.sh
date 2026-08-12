#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
config="${1:-${root}/marketplace.toml}"
output="${2:-${RUNNER_TEMP:-${TMPDIR:-/tmp}}/ggen-marketplace-admitted.json}"

if [[ "${config}" != /* ]]; then
  config="${root}/${config}"
fi
if [[ "${output}" != /* ]]; then
  output="${root}/${output}"
fi

manifest="${root}/tools/marketplace-config/Cargo.toml"
lock="${root}/tools/marketplace-config/Cargo.lock"
lock_tracked=false
if command -v git >/dev/null 2>&1 && git -C "${root}" ls-files --error-unmatch tools/marketplace-config/Cargo.lock >/dev/null 2>&1; then
  lock_tracked=true
fi

export CARGO_TARGET_DIR="${GGEN_MARKETPLACE_CONFIG_TARGET_DIR:-${RUNNER_TEMP:-${TMPDIR:-/tmp}}/ggen-marketplace-config-target}"
cargo run --quiet --manifest-path "${manifest}" -- "${config}" "${output}"

if [[ "${lock_tracked}" != true ]]; then
  rm -f "${lock}"
fi

python3 - "${output}" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
if payload.get("q_config") != 1 or payload.get("standing") != "ADMITTED":
    raise SystemExit("REFUSED:MARKETPLACE_CONFIG_Q_CONFIG_ZERO")
witness = payload.get("witness_blake3")
if not isinstance(witness, str) or len(witness) != 64:
    raise SystemExit("REFUSED:MARKETPLACE_CONFIG_WITNESS_INVALID")
PY

# The star-toml receipt admits operational configuration. This second court
# admits pack-source authority and binds the current pack corpus without
# allowing an import origin or mirror repository to become semantic authority.
authority_receipt="${output%.json}.source-authority.json"
python3 "${root}/scripts/verify_source_authority.py" \
  "${output}" \
  --receipt "${authority_receipt}"

printf '%s\n' "${output}"
