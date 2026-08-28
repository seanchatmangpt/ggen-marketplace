#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
admitted="${1:?usage: materialize_factory_ggen.sh ADMITTED_JSON OUTPUT_DIR}"
out="${2:?usage: materialize_factory_ggen.sh ADMITTED_JSON OUTPUT_DIR}"
mkdir -p "${out}/bin/amd64" "${out}/bin/arm64" "${out}/downloads"

mapfile -t values < <(python3 - "${admitted}" <<'PY'
import json, sys
from pathlib import Path
p=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
if p.get('q_config') != 1 or p.get('standing') != 'ADMITTED':
    raise SystemExit('REFUSED:MARKETPLACE_CONFIG_NOT_ADMITTED')
g=p['config']['ggen']
print(g['repository'])
print(g['version'])
print(g['release_commit'])
for key in ('linux_x86_64','linux_aarch64'):
    a=g['assets'][key]
    print(a['archive'])
    print(a['sha256'])
PY
)

[[ "${#values[@]}" -eq 7 ]] || { echo "REFUSED:GGEN_FACTORY_PROJECTION" >&2; exit 2; }
repo="${values[0]}"
version="${values[1]}"
release_commit="${values[2]}"
amd_asset="${values[3]}"
amd_sha="${values[4]}"
arm_asset="${values[5]}"
arm_sha="${values[6]}"

headers=(-H 'Accept: application/vnd.github+json')
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  headers+=( -H "Authorization: Bearer ${GITHUB_TOKEN}" -H 'X-GitHub-Api-Version: 2022-11-28' )
fi
ref_json="$(curl --fail --location --retry 3 --retry-all-errors --silent --show-error \
  "${headers[@]}" "https://api.github.com/repos/${repo}/git/ref/tags/${version}")"
python3 - "${ref_json}" "${release_commit}" <<'PY'
import json, sys
p=json.loads(sys.argv[1]); expected=sys.argv[2]; obj=p.get('object') or {}
if obj.get('type') != 'commit' or obj.get('sha') != expected:
    raise SystemExit(f"REFUSED:GGEN_RELEASE_TAG_DRIFT:{obj.get('type')}:{obj.get('sha')}:{expected}")
PY

fetch_asset() {
  local asset="$1" expected="$2" arch="$3"
  local archive="${out}/downloads/${asset}"
  curl --fail --location --retry 5 --retry-all-errors --retry-delay 1 --silent --show-error \
    "https://github.com/${repo}/releases/download/${version}/${asset}" -o "${archive}"
  local actual
  actual="$(sha256sum "${archive}" | awk '{print $1}')"
  [[ "${actual}" == "${expected}" ]] || {
    echo "REFUSED:GGEN_ASSET_DIGEST_DRIFT:${asset}:actual=${actual}:expected=${expected}" >&2
    exit 3
  }
  local tmp
  tmp="$(mktemp -d)"
  tar -xzf "${archive}" -C "${tmp}"
  local found
  found="$(find "${tmp}" -type f -name ggen -print -quit)"
  [[ -n "${found}" ]] || { rm -rf "${tmp}"; echo "REFUSED:GGEN_BINARY_NOT_FOUND:${asset}" >&2; exit 4; }
  cp "${found}" "${out}/bin/${arch}/ggen"
  chmod 0755 "${out}/bin/${arch}/ggen"
  rm -rf "${tmp}"
}

fetch_asset "${amd_asset}" "${amd_sha}" amd64
fetch_asset "${arm_asset}" "${arm_sha}" arm64

python3 - "${out}" "${repo}" "${version}" "${release_commit}" "${amd_asset}" "${amd_sha}" "${arm_asset}" "${arm_sha}" <<'PY'
import json, sys
from pathlib import Path
out=Path(sys.argv[1])
p={
  'schema':'ggen.factory-binaries/1',
  'repository':sys.argv[2],
  'version':sys.argv[3],
  'release_commit':sys.argv[4],
  'assets':{
    'amd64':{'archive':sys.argv[5],'sha256':sys.argv[6]},
    'arm64':{'archive':sys.argv[7],'sha256':sys.argv[8]},
  },
}
(out/'ggen-binaries.json').write_text(json.dumps(p,indent=2,sort_keys=True)+'\n',encoding='utf-8')
PY
