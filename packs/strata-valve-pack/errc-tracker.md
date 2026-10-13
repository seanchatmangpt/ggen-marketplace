# errc-tracker.md — strata-valve-pack hardening wave

ERRC (Eliminate/Reduce/Raise/Create) pass over the strata-valve-pack
hardening wave. Every entry below cites a real source, re-verified on disk
at write time (2026-10-12) — no paraphrase substituted for a citation, per
this ecosystem's source-of-truth-check discipline.

## Eliminate

**Dead query `queries/receipt_len.rq` — recorded, NOT deleted this wave**
(per lane instruction: record only). Verified on disk at write time:
`grep -rn "receipt_len.rq" ggen.toml templates/ queries/refusals.rq`
returns zero references anywhere in the pack — the file is unreferenced by
`ggen.toml` (`ggen.toml:29-34` wires only `queries/refusals.rq`), by any
template, or by any gate. No template reads a receipt-len query result other
than `queries/refusals.rq` (`queries/refusals.rq:10-12` binds `?receiptLen`
via the `valve:WireFact` join). The file is safe to retire in a later
cleanup wave.

## Reduce

**Namespace split, pending wave.** `ggen.toml:10` pins
`base_iri = "urn:strata:valve:"` while `ggen.toml:17` declares
`valve = "urn:strata:valve#"` and `ggen.toml:18` declares
`wire = "urn:strata:protocol:wire#"` — two different IRIs for the valve
vocabulary (`.../valve:` document base vs `.../valve#` term namespace),
and the wire vocabulary (`wire:` terms, e.g. `wire:RefusalReceipt`) is
referenced in the ontology's prose (`ontology.ttl:12`, `ontology.ttl:56`)
without being declared in-pack. Splitting document-IRI from term-namespace
and re-homing `wire:` to the protocol pack is recorded as a pending wave.

## Raise

**Gates landed this wave.** `gates/010_refusal_atom_closure.rq:8-18`
(fail-closed violation-row SELECT: refuses off-enum `valve:atom` values and
any `valve:RefusalClass` missing `valve:atom`; the enum is exactly
`{malformed_frame, fuel_exhausted, parent_discontinuity, arena_failure}`,
grounded in `ontology.ttl:31`, `ontology.ttl:37`, `ontology.ttl:43`,
`ontology.ttl:50`) and `gates/020_wire_class_present.rq:9-25` (refuses a
missing or non-32 `valve:length` on
`valve:refusalReceiptLen`; see `ontology.ttl:53-56`). Both verified clean
(0 rows) via `rdflib` against the real `ontology.ttl` and verified
non-vacuous by mutation (injected `valve:atom "bogus_atom"` and removed
`valve:length` each yield exactly 1 violation row). Wired into
`ggen.toml:21-24` `[validation] gates`.

**Runtime fix.** `templates/refusals.ex.tera:26` now emits
`@receipt_len {{ receipt_len }}` in each child module (before `@moduledoc`,
so the doc-string interpolation at `templates/refusals.ex.tera:33` and the
`List.duplicate(0, @receipt_len)` at `templates/refusals.ex.tera:41` both
resolve). Pre-fix, child modules only saw the parent module's copy
(`templates/refusals.ex.tera:10`) — `elixirc` raised 8
`undefined module attribute @receipt_len` warnings per compile (2 per child
module: the moduledoc interpolation and the `refuse/1` body). Post-fix,
`elixirc` is zero-warning and every child `refuse/1` returns a 32-byte
binary (witnessed by the runtime command in this wave's verification
ladder).

## Create

**Cross-graph 32-byte court (planned).** A court that loads both this
pack's `ontology.ttl` and the protocol pack's wire graph and asserts
`valve:refusalReceiptLen valve:length 32` agrees with
`wire:RefusalReceipt wire:fixedLen 32` — the check `gates/020_wire_class_present.rq:6-11`
documents but cannot execute in-pack (the `wire:` class is not declared
in-pack; see the gate's own header note). Planned as a cross-graph court
in a later wave.
