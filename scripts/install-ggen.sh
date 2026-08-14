#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
config_json="${1:-${GGEN_MARKETPLACE_ADMITTED_CONFIG:-}}"
if [[ -z "${config_json}" ]]; then
  config_json="$(bash "${root}/scripts/admit-config.sh")"
fi

platform="$(uname -s)/$(uname -m)"
mapfile -t values < <(python3 - "${config_json}" "${platform}" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if payload.get("q_config") != 1 or payload.get("standing") != "ADMITTED":
    raise SystemExit("REFUSED:MARKETPLACE_CONFIG_NOT_ADMITTED")
platforms = {
    "Linux/x86_64": "linux_x86_64",
    "Linux/aarch64": "linux_aarch64",
    "Linux/arm64": "linux_aarch64",
    "Darwin/arm64": "darwin_aarch64",
    "Darwin/aarch64": "darwin_aarch64",
    "Darwin/x86_64": "darwin_x86_64",
}
key = platforms.get(sys.argv[2])
if key is None:
    raise SystemExit(f"REFUSED:UNSUPPORTED_GGEN_PLATFORM:{sys.argv[2]}")
ggen = payload["config"]["ggen"]
asset = ggen["assets"][key]
print(ggen["repository"])
print(ggen["version"])
print(asset["archive"])
print(asset["sha256"])
PY
)

if [[ "${#values[@]}" -ne 4 ]]; then
  echo "REFUSED:MARKETPLACE_CONFIG_INSTALLER_PROJECTION" >&2
  exit 2
fi

readonly repository="${values[0]}"
readonly version="${values[1]}"
readonly asset="${values[2]}"
readonly expected_sha256="${values[3]}"
if [[ ! "${expected_sha256}" =~ ^[0-9a-f]{64}$ ]]; then
  echo "REFUSED:GGEN_ASSET_DIGEST_INVALID:${expected_sha256}" >&2
  exit 2
fi

readonly url="https://github.com/${repository}/releases/download/${version}/${asset}"
readonly cache_root="${GGEN_MARKETPLACE_CACHE_DIR:-${RUNNER_TEMP:-${TMPDIR:-/tmp}}/ggen-marketplace-${version}}"
readonly archive="${cache_root}/${asset}"
readonly marker="${cache_root}/asset.sha256"
readonly bin="${cache_root}/ggen"

mkdir -p "${cache_root}"

if [[ -x "${bin}" && -f "${marker}" ]] && [[ "$(cat "${marker}")" == "${expected_sha256}" ]]; then
  printf '%s\n' "${bin}"
  exit 0
fi

rm -f "${archive}" "${bin}" "${marker}"
# GitHub release/CDN fetches are transport, not evidence. Retry a bounded set of
# transient HTTP/network failures, then still fail closed unless the downloaded
# bytes match the admitted SHA-256 below.
curl --fail --location --silent --show-error \
  --retry 5 --retry-all-errors --retry-delay 1 --retry-max-time 20 \
  --connect-timeout 10 --max-time 30 \
  "${url}" --output "${archive}"

actual_sha256="$(python3 - "${archive}" <<'PY'
from pathlib import Path
import hashlib
import sys

path = Path(sys.argv[1])
h = hashlib.sha256()
with path.open('rb') as stream:
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(chunk)
print(h.hexdigest())
PY
)"

if [[ "${actual_sha256}" != "${expected_sha256}" ]]; then
  printf 'REFUSED:GGEN_ASSET_DIGEST_DRIFT:actual=%s expected=%s\n' "${actual_sha256}" "${expected_sha256}" >&2
  exit 3
fi

extract_dir="$(mktemp -d "${cache_root}/extract.XXXXXX")"
trap 'rm -rf "${extract_dir}"' EXIT
tar -xzf "${archive}" -C "${extract_dir}"
found="$(find "${extract_dir}" -type f -name ggen -print -quit)"
if [[ -z "${found}" ]]; then
  printf 'REFUSED:GGEN_BINARY_NOT_FOUND:%s\n' "${asset}" >&2
  exit 4
fi

cp "${found}" "${bin}"
chmod 0755 "${bin}"
printf '%s\n' "${expected_sha256}" > "${marker}"
printf '%s\n' "${bin}"
