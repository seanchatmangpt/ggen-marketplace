# cgap-pack

Canonical RDF graph for the CGAP columnar substrate: the Apache Arrow physical
format surface (layout families, format strings, buffer slots, C Data Interface
ABI structs, schema flags) that the `cgap` repo manufactures from. Every modeled
type cites the Arrow Columnar Format spec
(https://arrow.apache.org/docs/format/Columnar.html); generated consequences are
projections of THIS graph — change the graph, re-run `ggen sync`, never hand-edit
generated output.

## Layout

| path | content |
|---|---|
| `ontology.ttl` | the canonical graph — `https://cgap.chatmangpt.com/` vocabulary + pack namespace |
| `gates/010…050_*.rq` | 5 violation-row SELECTs, `ORDER BY`-deterministic |
| `witnesses/{pass,fail}/` | exact-stem witness pairs per gate — pass silent, fail fires |
| `gate-court.toml` | court config (`ggen.semantic-gate-witness-court/1`, exact-stem keys) |
| `templates/` | 4 Tera templates with disjoint output targets |

Pack namespace IRI: `https://seanchatmangpt.github.io/packs/cgap-pack#`.

## What the graph models

- **PhysicalLayout taxonomy** — `av:PhysicalLayout` plus 8 subclasses:
  `NullLayout`, `PrimitiveLayout` (with `TemporalLayout` and `DecimalLayout`
  beneath it), `VariableBinaryLayout`, `BinaryViewLayout`, `NestedLayout`,
  `RunEndEncodedLayout`, `DictionaryLayout` — 50 type individuals across the
  families (Null 1, primitive-side 32, variable-binary 4, binary-view 2,
  nested 9, run-end-encoded 1, dictionary 1).
- **Format coverage** — every layout except `av:Dictionary` carries an exact
  `av:formatCode` (39 individuals: `n`, `b`, `c`…`L`, `e`/`f`/`g`, `td*`, `tt*`,
  `tD*`, `ti*`, `u`/`U`/`z`/`Z`, `vu`/`vz`, `+s`/`+l`/`+L`/`+vl`/`+vL`/`+m`/`+r`)
  or a parameterized `av:formatPrefix` (10 individuals: `d:`, `tss:`/`tsm:`/
  `tsu:`/`tsn:`, `w:`, `+fl:`, `+ud:`, `+us:`). Dictionary carries neither by
  design — its format string is its index type's native code.
- **Densely indexed 64-byte-aligned BufferSlots** — 99 slot descriptors, every
  one carrying `av:alignmentBytes` exactly 64 (AVX-512 / NEON invariant) and a
  dense 0-based `av:slotIndex` (max+1 == count). Six `av:BufferRole` values:
  `ValidityBitmap` ×45, `DataBuffer` ×38, `OffsetBuffer` ×10, `SizeBuffer` ×2,
  `TypeBuffer` ×2, `VariadicDataBuffer` ×2.
- **ArrowSchema/ArrowArray C-ABI sourceText** — `av:ArrowSchema` and
  `av:ArrowArray` as `av:CAbiStruct` individuals carrying the exact spec
  struct definitions as `av:sourceText`, plus three `av:SchemaFlag` individuals
  with `av:cFlagValue` 1/2/4 (`ARROW_FLAG_DICTIONARY_ORDERED`, `NULLABLE`,
  `MAP_KEYS_SORTED`).
- **Promises** — three `av:Promise` individuals (64-byte alignment, C-ABI
  parity, format coverage), each `p:backedBy` modeled individuals, so the
  promise-vs-content gate has content to check.

## Gates

Refusal gates 010–050; each has a pass witness (zero rows) and a fail witness
(≥1 row) at the exact stem.

| gate | refuses when |
|---|---|
| `010_subject_identity` | a `p:Subject` lacks `p:subjectId` |
| `020_promise_vs_content` | an `av:Promise` has no `p:backedBy` edge |
| `030_alignment_invariant` | a buffer slot's `alignmentBytes` is missing or ≠ 64 |
| `040_format_completeness` | a layout other than Dictionary lacks formatCode and formatPrefix |
| `050_slot_continuity` | slot indices are not dense from 0 (COUNT ≠ MAX+1) |

## Projections

| template | generated target |
|---|---|
| `templates/cgap_h.tmpl` | `include/cgap_c_data.h` — C-ABI structs + schema flag macros |
| `templates/cgap_format_codes_h.tmpl` | `include/cgap_format_codes.h` — one macro per code |
| `templates/layout_gen_rs.tmpl` | `crates/cgap-arrow/src/generated_layout.rs` — `LAYOUT_SPECS` |
| `templates/subject-count.txt.tmpl` | `generated/subject-count.txt` |

## Standing

`ALIVE` within the marketplace + witness-court boundary (2026-10-29):

```text
$ python3 scripts/marketplace.py check cgap-pack
check ok packs=1 turtle=ok qualify=ok        (exit 0)

$ python3 scripts/check_gate_witness_courts.py   # cgap-pack row
```

Court-row fields (JSON output): `standing: ALIVE`, `case_count: 5`,
`require_pass: true`, `require_fail: true`, schema
`ggen.semantic-gate-witness-court/1`.

Standing is scoped to that qualification boundary — not a claim about any
consumer runtime.

## Consumers

`/Users/sac/cgap/ggen.toml` binds the pack by path:

```toml
[packs]
cgap-pack = { path = "../ggen-marketplace/packs/cgap-pack" }
```

Byte-stable replay (ggen 26.10.11, 2026-10-29, in `/Users/sac/cgap`):
`ggen sync run` twice, both exit 0; sha256 over the generated tree
(`include/`, `crates/cgap-arrow/src`, `generated/`) diff-identical across runs
and identical to the pre-sync tree; the second run reported `"written": []`.

## Evidence boundary

Marketplace admission + the exact-stem witness court + consumer replay only.
No execution authority; BRCE remains the sole actuation boundary.

## See Also

- [Pack contract](../../docs/reference/pack-contract.md)
- [Pack classes](../../docs/reference/pack-classes.md)
