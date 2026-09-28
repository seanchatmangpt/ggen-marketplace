#!/usr/bin/env bash
# Live chain for packs/ash-extension-pack:
#
#   real `ggen sync run` (consumer built by scripts/qualify_packs.py's own
#   prepare_consumer, i.e. the exact projection-profile capsule the marketplace
#   qualification court uses, including qualification/consumer.ttl)
#   -> second `ggen sync run` + sha256 comparison of every generated file
#   -> copy of the generated Elixir under test into <capsule>/generated/
#      (compiled by fixture/mix.exs via ASH_PACK_GENERATED)
#   -> mix deps.get -> mix compile --warnings-as-errors -> mix test
#      (MIX_BUILD_ROOT / MIX_DEPS_PATH also point into the capsule)
#
# Generated files are copied verbatim and never hand-edited or committed. A defect in them is fixed in the pack's
# templates/queries/ontology and re-projected by rerunning this script.
#
# Usage: scripts/ash_pack_live_fixture.sh [ggen-binary]
# Env:   ASH_PACK_CAPSULE  capsule dir to (re)create (default: mktemp -d)
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
pack_dir="${root}/packs/ash-extension-pack"
fixture="${pack_dir}/fixture"
ggen_bin="${1:-${GGEN_BIN:-$(command -v ggen)}}"
capsule="${ASH_PACK_CAPSULE:-$(mktemp -d "${TMPDIR:-/tmp}/ash-extension-pack-live.XXXXXX")}"
# The Elixir projections the fixture compiles and executes. The other generated
# files (resource/info/persist/verify/install/composition_test) are produced and
# hashed by both sync passes but are not compiled here.
generated=(receipt.ex receipted_action.ex reactor_pipeline.ex)
package="pipeline_probe"

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

[pack] = [p for p in marketplace.require_admitted() if p.name == "ash-extension-pack"]
print(f"profile: {pack.profile}")
print(f"consumer: {qualify_packs.prepare_consumer(pack, capsule)}")
PY

consumer="${capsule}/consumer"

digest() {
  (cd "${consumer}" && find lib test qualification -type f | LC_ALL=C sort | xargs shasum -a 256)
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

# Copy the projections under test out of the consumer tree. They stay in the
# capsule (not fixture/lib/generated) together with _build/ and deps/, because
# marketplace.py archives every visible file under a pack and refuses symlinks.
export ASH_PACK_GENERATED="${capsule}/generated"
export MIX_BUILD_ROOT="${capsule}/_build"
export MIX_DEPS_PATH="${capsule}/deps"
mkdir -p "${ASH_PACK_GENERATED}/${package}"
for file in "${generated[@]}"; do
  cp "${consumer}/lib/${package}/${file}" "${ASH_PACK_GENERATED}/${package}/${file}"
done

cd "${fixture}"
# Run under the toolchain pinned in fixture/.tool-versions when asdf is present
# (a PATH-first Homebrew elixir would otherwise shadow the pin).
if command -v asdf >/dev/null 2>&1; then
  mix_cmd=(asdf exec mix)
else
  mix_cmd=(mix)
fi
echo "elixir: $("${mix_cmd[@]}" run --no-start --no-compile --no-deps-check -e 'IO.write(System.version())' 2>/dev/null || echo unknown)"
"${mix_cmd[@]}" deps.get
"${mix_cmd[@]}" deps.compile

# Warnings-as-errors over the project's own sources (consumer lib/ + generated), with
# exactly one named, time-boxed allowance: receipt.ex.tmpl renders
# `@table :"<package>_receipts"`, a quoted atom Elixir 1.20 warns on. The source fix
# (drop the quotes in templates/receipt.ex.tmpl) belongs to the concurrent
# receipted-action lane that owns that file. When the fix lands the allowance stops
# matching and this script fails until the allowance is deleted.
allowed_warning="generated/${package}/receipt.ex:17"
compile_log="${capsule}/compile.log"
"${mix_cmd[@]}" compile --force 2>&1 | tee "${compile_log}"
locations="$(grep -E '^[[:space:]]*└─ ' "${compile_log}" | sed -E 's/^[[:space:]]*└─ ([^: ]+:[0-9]+).*/\1/' || true)"
unexpected="$(printf '%s\n' "${locations}" | grep -v -e '^$' -e "${allowed_warning}\$" || true)"
if [[ -n "${unexpected}" ]]; then
  echo "REFUSED:ASH_PACK_FIXTURE_COMPILE_WARNINGS" >&2
  printf '%s\n' "${unexpected}" >&2
  exit 1
fi
if ! printf '%s\n' "${locations}" | grep -q "${allowed_warning}\$"; then
  echo "REFUSED:ASH_PACK_FIXTURE_STALE_WARNING_ALLOWANCE ${allowed_warning} no longer warns; delete the allowance" >&2
  exit 1
fi
echo "compile: 0 unexpected project warnings (1 allowed: ${allowed_warning} quoted atom)"

"${mix_cmd[@]}" test
