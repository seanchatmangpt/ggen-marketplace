#!/usr/bin/env bash
# Live chain for packs/cs2-semantic-work (mirrors scripts/ash_pack_live_fixture.sh):
#
#   real `ggen sync run` (consumer built by scripts/qualify_packs.py's own
#   prepare_consumer, i.e. the exact projection-profile capsule the marketplace
#   qualification court uses, including qualification/consumer/*.ttl)
#   -> second `ggen sync run` + sha256 comparison of every generated file
#   -> verbatim copy of generated/cs2-semantic-work (elixir/*.ex + every JSON
#      projection) into <capsule>/generated, read by fixture/mix.exs and the fixture
#      tests via CS2_PACK_GENERATED
#   -> mix deps.get -> mix compile --warnings-as-errors -> mix test
#      (MIX_BUILD_ROOT / MIX_DEPS_PATH also point into the capsule)
#
# Generated files are never hand-edited or committed. A defect in them is fixed in the
# pack's templates/ontology and re-projected by rerunning this script.
#
# Usage: scripts/cs2_pack_live_fixture.sh [ggen-binary]
# Env:   CS2_PACK_CAPSULE  capsule dir to (re)create (default: mktemp -d)
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
pack_dir="${root}/packs/cs2-semantic-work"
fixture="${pack_dir}/fixture"
ggen_bin="${1:-${GGEN_BIN:-$(command -v ggen)}}"
capsule="${CS2_PACK_CAPSULE:-$(mktemp -d "${TMPDIR:-/tmp}/cs2-semantic-work-live.XXXXXX")}"

echo "ggen: ${ggen_bin} ($("${ggen_bin}" --version 2>/dev/null | head -1))"
echo "capsule: ${capsule}"
rm -rf "${capsule}"
mkdir -p "${capsule}"

python3 - "${root}" "${capsule}" <<'PY'
import sys
from pathlib import Path

root, capsule = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(root / "scripts"))
import marketplace  # noqa: E402
import qualify_packs  # noqa: E402

[pack] = [p for p in marketplace.require_admitted() if p.name == "cs2-semantic-work"]
print(f"profile: {pack.profile}")
print(f"consumer: {qualify_packs.prepare_consumer(pack, capsule)}")
PY

consumer="${capsule}/consumer"
generated_rel="generated/cs2-semantic-work"

digest() {
  (cd "${consumer}" && find generated qualification -type f | LC_ALL=C sort | xargs shasum -a 256)
}

sync_pass() {
  local n="$1"
  if ! (cd "${consumer}" && "${ggen_bin}" sync run --format json >"${capsule}/sync-${n}.json" 2>"${capsule}/sync-${n}.log"); then
    echo "REFUSED:GGEN_PACK_SYNC_FAILED pass=${n}" >&2
    tail -5 "${capsule}/sync-${n}.log" >&2
    exit 1
  fi
  echo "ggen sync run pass=${n} exit=0"
}

sync_pass 1
digest >"${capsule}/sha256-pass1.txt"
sync_pass 2
digest >"${capsule}/sha256-pass2.txt"
if ! cmp -s "${capsule}/sha256-pass1.txt" "${capsule}/sha256-pass2.txt"; then
  echo "REFUSED:GGEN_PACK_NONDETERMINISTIC_REPLAY" >&2
  diff "${capsule}/sha256-pass1.txt" "${capsule}/sha256-pass2.txt" >&2 || true
  exit 1
fi
echo "determinism: $(wc -l <"${capsule}/sha256-pass1.txt" | tr -d ' ') files byte-identical across passes"
echo "sha256 manifest: $(shasum -a 256 "${capsule}/sha256-pass1.txt" | cut -d' ' -f1)"
cat "${capsule}/sha256-pass1.txt"

if [[ ! -d "${consumer}/${generated_rel}/elixir" || ! -f "${consumer}/${generated_rel}/work-projection-batch.json" ]]; then
  echo "REFUSED:CS2_PACK_GENERATED_MISSING (${generated_rel})" >&2
  exit 1
fi

# The generated tree stays in the capsule (never under fixture/) together with
# _build/ and deps/, because marketplace.py archives every visible file under a pack
# and refuses symlinks.
export CS2_PACK_GENERATED="${capsule}/generated"
export MIX_BUILD_ROOT="${capsule}/_build"
export MIX_DEPS_PATH="${capsule}/deps"
cp -R "${consumer}/${generated_rel}" "${CS2_PACK_GENERATED}"
echo "generated: $(find "${CS2_PACK_GENERATED}/elixir" -name '*.ex' | wc -l | tr -d ' ') .ex and $(find "${CS2_PACK_GENERATED}" -name '*.json' | wc -l | tr -d ' ') .json files copied into the capsule"

# mix.lock is written back into the pack only when dependency resolution changes it;
# the committed lock pins jason.
cd "${fixture}"
export PATH="${HOME}/.asdf/shims:${PATH}"
echo "elixir: $(elixir -e 'IO.write(System.version())' 2>/dev/null || echo unknown)"
mix deps.get
mix compile --force --warnings-as-errors
mix test
