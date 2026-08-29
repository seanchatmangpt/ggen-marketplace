
# MFW PCP Level-5 candidate pack

This is a complete **Level-5 candidate**, not an unverified Level-5 claim. It carries the twelve capabilities required by the current ggen promotion contract and refuses final admission until live evidence closes every capability.

## Run

```bash
cd packs/mfw-pcp-level5-pack
ggen sync run
cd consumer/mfw-pcp-generated
cargo build && cargo test
ggen receipt verify
```

## Produced consumer

The pack generates the complete bounded verifier crate: build manifest, certificate registry, obligation and distinction ledgers, receipt contracts, replay/standing verifier, positive tests, negative witnesses, documentation, provenance, CI, release standing, and verifier script.

## Standing (real, 2026-08-29 audit -- not this pack's own optimistic self-assessment)

`L5_CAPABILITY_LEDGER.json` and `evidence/*.json` are authoritative for this pack, and reflect a
live per-capability audit, not a script that marks every row `ALIVE` on completion. Result:
**11/12 ALIVE** (cap01-cap05, cap07-cap12), **1/12 PARTIAL_ALIVE** (cap06). `standing` is
`PARTIAL_ALIVE` and `level5_admitted` is `false`. (`.specify/pack-l5-promotion.ttl` and
`docs/l5-promotion/L5_PROMOTION_PROGRAM.md`, referenced by an earlier pass as this repo's L5
pack-closure promotion program citation, do not currently exist in this repository -- a
pre-existing dangling reference this pass did not fabricate a replacement for.)

The 2026-07-21/22 passes' two real falsifier hits are now closed: the FRONTMATTER_LEAK that broke
every generated output, and cap11's hardcoded-`10` test, were both already fixed in the source
templates by the time this pass started (their committed `consumer/mfw-pcp-generated/` snapshot
had simply drifted out of sync with the fix -- re-rendered to match, re-verified live). This pass
additionally found and fixed a third, previously-undocumented defect: `cargo fmt --all -- --check`
failed against the regenerated consumer because rustfmt's line-wrap decisions are content-length
dependent and a static template can't guarantee `--check`-clean output for arbitrary ontology
text; `templates/ci.yml.tmpl`/`templates/scripts/verify.sh.tmpl` now run `cargo fmt --all`
(canonicalize) instead. See `evidence/consumer-replacement.json` and `evidence/semantic-diff.json`
for full reproduction detail (no `ggen` binary was available in this pass's environment -- both
files document the real rdflib-SPARQL + Jinja2 re-render method used in its place, cross-checked
against a real `cargo build`/`test`/`fmt`/`clippy`).

**cap06 (Generated negative witnesses) stays open, on a real, disclosed, unfabricated gap.**
`ontology.ttl` declares 6 `pcp:Invariant` individuals; 4 have real passing positive+negative
tests, 1 more (`certificate_inventory_is_complete`) is enforced at the admission-gate layer
instead of at runtime. The 6th, `bounded_is_not_exhausted`, has no implementation anywhere in
this pack -- no Rust type, no test, no gate references "bounded" or "exhausted" at all beyond
this one invariant's own prose. This pass did not invent Bounded/Exhausted semantics to paper
over that gap: nothing else in the ontology defines what they mean, and fabricating the business
rule would be a worse defect than an honest `PARTIAL_ALIVE`. Closing it needs a maintainer who
knows the intended semantics, or a decision to retire the invariant.

## Decisive verifier -- not carried forward from the source pack

An earlier `verify-level5.sh` script existed upstream that unconditionally set all twelve
capability rows to `ALIVE` and `standing`/`level5_admitted` to `ALIVE`/`true` the moment its own
(narrower) check sequence completed without error -- it never re-verifies each capability's own
named falsifier (e.g. its "semantic mutation" check only compares output digests, not whether the
regenerated consumer still builds and passes `cargo test`, which is exactly the check that caught
the real cap11 falsifier above). Trusting that script's output would have overclaimed Level 5
admission for a pack that demonstrably does not have it. It is deliberately not included in this
pack's landed copy; `L5_CAPABILITY_LEDGER.json` plus `evidence/*.json` (real command transcripts
and digests, not narration) are the authoritative standing record instead.
