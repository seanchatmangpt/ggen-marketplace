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
print(config["clap_noun_verb"]["version"])
PY
)

if [[ "${#values[@]}" -ne 4 ]]; then
  echo "REFUSED:MARKETPLACE_CONFIG_QUALIFIER_PROJECTION" >&2
  exit 2
fi

workers="${values[0]}"
timeout_seconds="${values[1]}"
expected_version="${values[2]}"
expected_clap_noun_verb_version="${values[3]}"
ggen="${GGEN_BIN:-}"
if [[ -z "${ggen}" ]]; then
  ggen="$(bash "${root}/scripts/install-ggen.sh" "${config_json}")"
fi

observed_version="$("${ggen}" --version 2>&1)"
if [[ "${observed_version}" != "ggen ${expected_version#v}"* ]]; then
  printf 'REFUSED:GGEN_VERSION_DRIFT:observed=%s expected=%s\n' "${observed_version}" "${expected_version}" >&2
  exit 2
fi

# The clap-noun-verb-crate-pack's generated Cargo.toml exact-pins
# `clap-noun-verb` and `clap-noun-verb-macros` to the same version (they
# must move in lockstep -- the macros crate is published first). Refuse if
# either pin drifts from marketplace.toml's [clap_noun_verb].version
# source of truth, or if the two pins disagree with each other.
cargo_toml_tmpl="${root}/packs/clap-noun-verb-crate-pack/templates/Cargo.toml.tmpl"
mapfile -t observed_pins < <(grep -oE '^clap-noun-verb(-macros)? = "=[0-9][0-9.]*"' "${cargo_toml_tmpl}" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
if [[ "${#observed_pins[@]}" -ne 2 ]]; then
  printf 'REFUSED:CLAP_NOUN_VERB_PIN_UNPARSEABLE:file=%s\n' "${cargo_toml_tmpl}" >&2
  exit 2
fi
if [[ "${observed_pins[0]}" != "${observed_pins[1]}" ]]; then
  printf 'REFUSED:CLAP_NOUN_VERB_PIN_LOCKSTEP_MISMATCH:crate=%s macros=%s\n' \
    "${observed_pins[0]}" "${observed_pins[1]}" >&2
  exit 2
fi
if [[ "${observed_pins[0]}" != "${expected_clap_noun_verb_version}" ]]; then
  printf 'REFUSED:CLAP_NOUN_VERB_VERSION_DRIFT:observed=%s expected=%s\n' \
    "${observed_pins[0]}" "${expected_clap_noun_verb_version}" >&2
  exit 2
fi

python3 "${root}/scripts/qualify_packs.py" \
  --ggen "${ggen}" \
  --workers "${workers}" \
  --timeout-seconds "${timeout_seconds}" \
  --report "${report}"
