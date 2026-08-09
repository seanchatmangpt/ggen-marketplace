#!/usr/bin/env bash
set -euo pipefail

readonly GGEN_VERSION="v26.8.8"

case "$(uname -s)/$(uname -m)" in
  Linux/x86_64)
    asset="ggen-x86_64-unknown-linux-gnu.tar.gz"
    expected_sha256="c651d873c2aeb6bd71c3d5356634f0b3f4adafd2454ee354c817a7079c2ea802"
    ;;
  Linux/aarch64|Linux/arm64)
    asset="ggen-aarch64-unknown-linux-gnu.tar.gz"
    expected_sha256="c39d883b43aa6c635f5a490b7c203a1aaa6499e0df14b5d82d9dc4a26b8d22f6"
    ;;
  Darwin/arm64|Darwin/aarch64)
    asset="ggen-aarch64-apple-darwin.tar.gz"
    expected_sha256="673c1b5e1aecc13fd848141e62ef6b2bb5b54f0eb653866826caa01e80aea3df"
    ;;
  Darwin/x86_64)
    asset="ggen-x86_64-apple-darwin.tar.gz"
    expected_sha256="a4304371ce787e7bfe479fdba050960cdb8761fc9ca3d272da6bd7e64af08570"
    ;;
  *)
    printf 'REFUSED:UNSUPPORTED_GGEN_PLATFORM:%s/%s\n' "$(uname -s)" "$(uname -m)" >&2
    exit 2
    ;;
esac

readonly asset expected_sha256
readonly url="https://github.com/seanchatmangpt/ggen/releases/download/${GGEN_VERSION}/${asset}"
readonly cache_root="${GGEN_MARKETPLACE_CACHE_DIR:-${RUNNER_TEMP:-${TMPDIR:-/tmp}}/ggen-marketplace-${GGEN_VERSION}}"
readonly archive="${cache_root}/${asset}"
readonly marker="${cache_root}/asset.sha256"
readonly bin="${cache_root}/ggen"

mkdir -p "${cache_root}"

if [[ -x "${bin}" && -f "${marker}" ]] && [[ "$(cat "${marker}")" == "${expected_sha256}" ]]; then
  printf '%s\n' "${bin}"
  exit 0
fi

rm -f "${archive}" "${bin}" "${marker}"
curl --fail --location --retry 1 --silent --show-error \
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
