#!/usr/bin/env bash
# Live chain for packs/ash-extension-pack:
#
#   real `ggen sync run` (consumer built by scripts/qualify_packs.py's own
#   prepare_consumer, i.e. the exact projection-profile capsule the marketplace
#   qualification court uses, including qualification/consumer.ttl)
#   -> second `ggen sync run` + sha256 comparison of every generated file
#   -> copy of EVERY generated file into the capsule: lib/**/*.ex into
#      <capsule>/generated/ (compiled by fixture/mix.exs via ASH_PACK_GENERATED) and
#      every generated test (the composition tests plus every spark/parity/verifier/
#      transformer/igniter/dead-surface court) into <capsule>/generated_test/ (run by
#      mix test via ASH_PACK_GENERATED_TEST)
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
# A previous chain run's igniter-court scratch installs can leave a _build tree
# (with deps symlinks) inside the fixture dir; the pack archiver refuses symlinks.
rm -rf "${fixture}/_build"
ggen_bin="${1:-${GGEN_BIN:-$(command -v ggen)}}"
capsule="${ASH_PACK_CAPSULE:-$(mktemp -d "${TMPDIR:-/tmp}/ash-extension-pack-live.XXXXXX")}"

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

# The live chain is pack-scoped: admit ash-extension-pack on its OWN issues. A
# concurrent wave can hold OTHER packs mid-edit (MANIFEST_MISSING on a pack another
# lane is writing); those are foreign flux, not this chain's subject, and are
# reported as a typed note instead of blocking the chain. This pack's issues still
# refuse.
packs, issues = marketplace.inspect_marketplace()
target = "ash-extension-pack"
own = [i for i in issues if target in i]
foreign = [i for i in issues if target not in i]
if own:
    for issue in own:
        print(issue, file=sys.stderr)
    raise SystemExit(2)
if foreign:
    print(f"NOTE:FOREIGN_PACK_FLUX n={len(foreign)} (chain scoped to {target}; first: {foreign[0]})", file=sys.stderr)
[pack] = [p for p in packs if p.name == target]
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

# Copy every projection out of the consumer tree: all generated lib/**/*.ex (every
# spec in the union graph: the pack ontology's worked specs plus
# qualification/consumer.ttl's) and every generated composition test. They stay in the
# capsule (not fixture/lib/generated) together with _build/ and deps/, because
# marketplace.py archives every visible file under a pack and refuses symlinks.
export ASH_PACK_GENERATED="${capsule}/generated"
export ASH_PACK_GENERATED_TEST="${capsule}/generated_test"
# Repo fixture dir, for courts that need pack fixture support files (specimens,
# mutants) regardless of the cwd mix test runs from.
export ASH_PACK_FIXTURE_DIR="${fixture}"
export MIX_BUILD_ROOT="${capsule}/_build"
export MIX_DEPS_PATH="${capsule}/deps"
mkdir -p "${ASH_PACK_GENERATED}" "${ASH_PACK_GENERATED_TEST}"
(cd "${consumer}/lib" && find . -type f -name '*.ex' | LC_ALL=C sort | while read -r f; do
  mkdir -p "${ASH_PACK_GENERATED}/$(dirname "${f}")"
  cp "${f}" "${ASH_PACK_GENERATED}/${f}"
done)
# Copy the composition tests (the original selection) plus every generated court.
# Court templates emit two shapes: runnable ExUnit files already named
# *_court_test.exs, and ExUnit files named *_court.exs -- mix test only executes
# *_test.exs paths, so the latter are copied under a _test.exs name. That is a
# transport rename only: file contents are copied verbatim, never hand-edited.
cp "${consumer}"/test/*_composition_test.exs "${ASH_PACK_GENERATED_TEST}/"
for court in "${consumer}"/test/*_court_test.exs; do
  [[ -e "${court}" ]] || continue
  cp "${court}" "${ASH_PACK_GENERATED_TEST}/"
done
for court in "${consumer}"/test/*_court.exs; do
  [[ -e "${court}" ]] || continue
  cp "${court}" "${ASH_PACK_GENERATED_TEST}/$(basename "${court%.exs}")_test.exs"
done
# The court chain is load-bearing: copying zero courts is a refusal, not a pass.
if [[ "$(find "${ASH_PACK_GENERATED_TEST}" -name '*_court*_test.exs' | wc -l | tr -d ' ')" -eq 0 ]]; then
  echo "REFUSED:ASH_PACK_NO_COURTS_COPIED" >&2
  exit 1
fi
# mix test requires a helper in every test path; the fixture's own helper is reused.
cp "${fixture}/test/test_helper.exs" "${ASH_PACK_GENERATED_TEST}/test_helper.exs"
generated_ex="$(cd "${consumer}" && find lib -type f -name '*.ex' | wc -l | tr -d ' ')"
generated_other="$(cd "${consumer}" && find lib -type f ! -name '*.ex' | wc -l | tr -d ' ')"
if [[ "${generated_other}" != "0" ]]; then
  echo "REFUSED:ASH_PACK_UNCOMPILED_GENERATED_LIB (${generated_other} non-.ex files under lib/)" >&2
  exit 1
fi
echo "generated: ${generated_ex} lib .ex files and $(find "${ASH_PACK_GENERATED_TEST}" -name '*_test.exs' ! -name 'test_helper.exs' | wc -l | tr -d ' ') generated tests ($(find "${ASH_PACK_GENERATED_TEST}" -name '*_court*_test.exs' | wc -l | tr -d ' ') courts) copied into the compile capsule"

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

# Warnings-as-errors over the project's own sources (consumer lib/ + generated). The
# former receipt.ex quoted-atom allowance was retired when templates/receipt.ex.tmpl
# dropped the quotes (v26.9.27); zero project warnings are admitted.
compile_log="${capsule}/compile.log"
"${mix_cmd[@]}" compile --force 2>&1 | tee "${compile_log}"
locations="$(grep -E '^[[:space:]]*└─ ' "${compile_log}" | sed -E 's/^[[:space:]]*└─ ([^: ]+:[0-9]+).*/\1/' || true)"
unexpected="$(printf '%s\n' "${locations}" | grep -v -e '^$' || true)"
if [[ -n "${unexpected}" ]]; then
  echo "REFUSED:ASH_PACK_FIXTURE_COMPILE_WARNINGS" >&2
  printf '%s\n' "${unexpected}" >&2
  exit 1
fi
echo "compile: 0 project warnings"

"${mix_cmd[@]}" test
