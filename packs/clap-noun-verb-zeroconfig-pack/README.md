# clap-noun-verb-zeroconfig-pack

Zero-config starter for the clap-noun-verb zero-code CLI compiler.

The real compiler is six separately-composable packs — `clap-noun-verb-schema-pack`,
`-crate-pack`, `-routing-pack`, `-behavior-pack`, `-boundary-pack`, `-verification-pack` — each
with one narrow responsibility (see their own `pack.toml` descriptions). Wiring all six into a
project's `[packs]` table and hand-authoring a valid `ontology.ttl` is real, but not zero-effort.
This pack does that wiring once and ships a small, complete, working `ontology.ttl` alongside it,
so getting a compiling CLI out of the compiler takes one command -- **as long as you run it in
place, from inside a full `ggen-marketplace` checkout**: `ggen.toml`'s `[packs]` table wires the
six sibling packs by relative path (`path = "../clap-noun-verb-schema-pack"`, etc.), which only
resolves when those six directories are actually its siblings on disk. `ggen` has no
registry/name-based pack reference today -- `path =` is the only composition mechanism -- so
moving or copying just this one directory elsewhere breaks the command below immediately with
`[FM-PACK-001]` (pack not found). If you cloned the whole `ggen-marketplace` repo, this just works:

```bash
git clone https://github.com/seanchatmangpt/ggen-marketplace
cd ggen-marketplace/packs/clap-noun-verb-zeroconfig-pack
ggen sync run
cargo build && cargo test
./target/debug/zc greet hello World
./target/debug/zc greet add 2 3
./target/debug/zc system ping
```

## What's in the starter graph

Two nouns, four commands, four distinct behavior kinds — enough to see the real shape of the
compiler without wading through every feature:

- `greet hello <name> [--uppercase]` — `EchoBehavior` (returns typed inputs as JSON)
- `greet add <left> <right>` — `ExpressionBehavior` (typed `i64` arithmetic)
- `system ping` — `StaticJsonBehavior` (ontology-owned constant response)
- `system refuse` — `RefusalBehavior` (typed, deliberate command-level refusal)

Grow your own CLI by editing `ontology.ttl` — rename `cnv:crateName`/`cnv:binaryName`, then add
`cnv:Noun`/`cnv:Command`/`cnv:Argument` individuals. `ggen sync run` regenerates everything
downstream from that one file; nothing else in this directory needs to change.

## Not a composable ingredient

Unlike the six packs it wires together, this pack's `ontology.ttl` declares a concrete `cnv:Cli`
individual (same reasoning as `clap-noun-verb-specimen-pack`) — composing it into another
project's `[packs]` table would violate `clap-noun-verb-schema-pack`'s exactly-one-CLI gate
(`gates/060_exactly_one_cli.rq`). To build your own CLI, copy this directory's `ontology.ttl` into
a new project as a starting point, then hand-author that new project's own `ggen.toml` with a
`[packs]` table pointing (by relative or absolute path) at wherever your `ggen-marketplace`
checkout of the six real compiler packs lives -- copying `ontology.ttl` alone is enough; do **not**
copy this directory's own `ggen.toml`, since its `../clap-noun-verb-*-pack` paths are only valid
next to this pack's siblings inside `ggen-marketplace/packs/`.

Verified 2026-08-10 with the real `ggen 26.8.6` binary: `ggen sync run` writes a complete
`Cargo.toml`/`src/*.rs`/`tests/*.rs` crate; `cargo build` succeeds; `cargo test` passes all 17
generated tests (route registration, argument validation and refusal, behavior correctness,
filesystem-boundary safety) with zero mocks — every test exercises the real compiled binary.
