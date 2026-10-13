# errc-tracker.md — strata-pn64-pack hardening wave (L6)

ERRC pass over the strata-hardening-wave hardening pass. Every claim below
was verified against the working tree at edit time (2026-10-12); line
numbers are from the on-disk files.

## Eliminate

- **Dead legacy twin `templates/pn64_masks.rs.tmpl`** — still present
  (verified on disk), old pre-ggen header format (`to: src/pn64_masks.rs`
  / `sparql:`); the `ggen.toml` generation rule names only
  `templates/pn64_masks.rs.tera`, so the `.tmpl` is dead weight. Recorded
  for deletion in a later transition; not deleted in this pass.

## Reduce

- **DaoVerb domain misuse reduced**: 5 of 6 `st:DaoVerb` individuals used
  `st:transitionOpcode` (domain `st:RonrTransition`; `ontology.ttl:134`'s
  own comment says "do not reuse st:transitionOpcode, domain
  RonrTransition") instead of `st:verbOpcode` — which would have made gate
  030's verb leg read only 1 verb (5 would be `verb_without_transition`
  rows... actually 5 verb rows + 5 `transition_without_verb` rows). Fixed
  in this pass: `ontology.ttl:149-154` — all six verbs now
  `st:verbOpcode` "0x01".."0x06".

## Raise

- **Fire-law equivalence court landed**: `templates/pn64_masks.rs.tera` —
  doc-comment on `fire()` (precondition `enabled(marking, pre)` first;
  ungated XOR toggles pre-bits absent from the marking; equals the
  clear-then-set law `(m & !pre) | post` used by `reachable_bitset` on the
  enabled domain, diverges off it) plus test
  `fire_law_equivalence_on_enabled_domain` (256 markings x 8 pre x 6 post
  asserted on the gated domain, plus two pinned divergence witnesses
  `fire(0b0000, 0b0010, 0b0000) == 0b0010` vs clear-then-set `0b0000`).
  Receipt: 6/6 tests pass via `rustc --test generated/pn64_masks.rs -o
  /tmp/l6-pn64-tests && /tmp/l6-pn64-tests` (0.00s).
- **Three gates wired and witnessed** — `gates/010_place_offset_bounds.rq`,
  `gates/020_transition_pre_nonzero.rq`,
  `gates/030_verb_opcode_bijection.rq`, all registered in
  `ggen.toml` `[validation] gates`, all returning zero rows (clean) on the
  real graph, and gate 010 witnessed refusing a corrupted copy
  (`[FM-LAW-018] SPARQL gate gates/010_place_offset_bounds.rq refused the
  sync: ... SELECT returned 2 row(s); first row: { ?conflict =
  duplicate_offset, ?offset = 3, ?place = ...#p_debatable }`).

## Create

- **Dual-template dedup decision pending**: the pack carries two mask
  templates (`.tmpl` twin + `.tera`). Decision: delete `.tmpl` at wave
  integration (see Eliminate); nothing else consumes it.
- **`generated/pn64_masks.rs` minted for the first time**:
  sha256 `aebb4149a711b2b988aae50af6a2a003ff5c45a22d8716fe530d56f7b57c1f1c`;
  two consecutive `ggen sync run`s byte-identical (`cmp` clean);
  `graph_hash_hex 5507214b8e5353b4c7fdee35a50c76a31e59224162c32599f887cf6b1ad4c366`;
  not git-added per lane rules.
