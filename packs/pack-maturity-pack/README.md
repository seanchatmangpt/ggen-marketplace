# pack-maturity-pack

Generates the cross-cutting proof artifacts that any ggen pack's consumer can compose in to help
close two real, machine-checkable dimensions of the L5 promotion program's 12-capability bar
(`http://ggen.org/l5-promotion#`, defined in the `ggen` repository's own
`.specify/pack-l5-promotion.ttl`):

- **`l5p:cap03` (Deterministic regeneration) + `l5p:cap04` (Fixed-point convergence)** — a
  generated test (`tests/pack_maturity_regeneration.rs`) that runs `ggen sync run` twice against
  the real consumer and snapshots every output file's raw bytes before and after the second run,
  asserting they're identical. This observes real filesystem state rather than trusting `ggen
  sync run`'s own "written"/"skipped" self-report — some frontmatter write modes report
  `"written"` on every run even when content didn't change, confirmed empirically, so the only
  trustworthy signal is the actual bytes on disk.
- **`l5p:cap09` (Generated receipts)** — a generated test (`tests/pack_maturity_receipt.rs`) that
  runs a real sync, then `ggen receipt verify`, and asserts the chain is `valid`, `signed`, and
  `signature_valid`.

## What this does *not* do

Composing this pack does not, by itself, get a consumer to L5 or even L4 across the board — it
closes 2 of 12 named capabilities, and only the mechanical ones. `l5p:cap01` (authoritative
semantic source), `cap02` (complete generation surface), `cap05` (generated verification of
domain behavior), `cap06` (generated negative witnesses), `cap07`/`cap08` (generated
documentation/provenance), and `cap10`–`cap12` all require domain-specific ontology facts —
what the subsystem actually *does* — that only the composing pack's own author can supply. A
generic pack cannot manufacture domain semantics it doesn't have. Composing this pack is a
floor, not a ceiling.

## Usage

Add to a consumer's `ggen.toml`:

```toml
[packs]
pack-maturity-pack = { path = "../../packs/pack-maturity-pack" }
```

No ontology facts of your own are required — both generated tests are static-content templates
(no `sparql:` extraction), so they compose unchanged into any consumer regardless of domain.
Requires `ggen` on `PATH` at test time (same requirement `chicago-tdd-tools-pack`'s `CliHarness`
already has for the binary under test).

Verified 2026-08-10 against a real composed consumer (real `ggen 26.8.6`, no mocks): both
generated tests pass on a clean sync.

A real negative-control experiment was also run: hand-editing a generated `force: true` file
between two real syncs. The mutation was **silently overwritten** by the second sync — correct,
intended `force: true` behavior, not a bug — so the regeneration test does *not* flag external
hand-edits to `force: true` output, and shouldn't. Its actual, verified purpose is catching
non-determinism in the generation pipeline itself (a stray timestamp, random ID, or unstable
iteration order leaking into rendered output across two runs with unchanged inputs) — that's
what "fixed-point convergence" (`l5p:cap04`) means, and it's what this test actually checks.
