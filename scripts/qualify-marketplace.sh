#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
config_json="${1:-${GGEN_MARKETPLACE_ADMITTED_CONFIG:-}}"
report="${2:-${RUNNER_TEMP:-${TMPDIR:-/tmp}}/ggen-marketplace-qualification.json}"

if [[ -z "${config_json}" ]]; then
  config_json="$(bash "${root}/scripts/admit-config.sh")"
fi

mapfile -t values < <(python3 - "${config_json}" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if payload.get("q_config") != 1 or payload.get("standing") != "ADMITTED":
    raise SystemExit("REFUSED:MARKETPLACE_CONFIG_NOT_ADMITTED")
config = payload["config"]
print(config["qualification"]["workers"])
print(config["qualification"]["timeout_seconds"])
print(config["ggen"]["version"])
PY
)

if [[ "${#values[@]}" -ne 3 ]]; then
  echo "REFUSED:MARKETPLACE_CONFIG_QUALIFIER_PROJECTION" >&2
  exit 2
fi

workers="${values[0]}"
timeout_seconds="${values[1]}"
expected_version="${values[2]}"
ggen="${GGEN_BIN:-}"
if [[ -z "${ggen}" ]]; then
  ggen="$(bash "${root}/scripts/install-ggen.sh" "${config_json}")"
fi

observed_version="$("${ggen}" --version 2>&1)"
if [[ "${observed_version}" != "ggen ${expected_version#v}"* ]]; then
  printf 'REFUSED:GGEN_VERSION_DRIFT:observed=%s expected=%s\n' "${observed_version}" "${expected_version}" >&2
  exit 2
fi

python3 "${root}/scripts/qualify_packs.py" \
  --ggen "${ggen}" \
  --workers "${workers}" \
  --timeout-seconds "${timeout_seconds}" \
  --report "${report}"
