# STRATA Receipt Templates

Fill-in templates for strata campaign closure receipts, matching the
`PACK_FEEDBACK-425-CLOSE.md` section shape (Title, Item, Status, Fixing
commit, Fix shape, Witnesses, Consumer consequence). Copy the relevant
template into a new file, replace every `<...>` placeholder, and cite only
witness artifacts you have actually read on disk.

## STRATA-BATCH-<n>-CLOSE.md (batch closure)

```markdown
# STRATA-HARDENING-1 Batch <n> — CLOSED

- **Item**: `docs/sjira/v26.10.8/STRATA-HARDENING-1.md` items <P-x, P-y, ...>
  — <one-sentence defect summary for the batch's pack set>.
- **Status**: CLOSED <YYYY-MM-DD> (batch <n>).
- **Fixing commits** (on `ggen-marketplace` branch `<branch>`):
  1. `<sha>` — `<commit subject>`. <What changed, at contract level:
     ggen.toml / ontology / template / gate.>
  2. `<sha>` — `<commit subject>`. <Change; note output-neutral sync proof
     if generated output is unchanged.>
- **Fix shape**: <where the remediation lives — pack contract source, not
  generated consumers; generated files remain projections.>
- **Witnesses** (real qualification artifacts on this machine):
  1. `<path>/wave-baseline-qual.json` (ggen <version>, <N> packs) — pre-fix
     baseline. Affected packs: <pack>: <status/code> per pack, with whole
     corpus counts (<alive> ALIVE / <refused> REFUSED / <warn> WARN /
     <skipped> SKIPPED).
  2. `<path>/wave-post<n>-qual.json` (ggen <version>, <N> packs) — post-fix
     court. Affected packs: <n>/<m> ALIVE. Whole corpus: <counts>; the delta
     vs baseline is the remediated set.
- **Consumer consequence**: <what consumers of the affected packs can now do;
  which remaining refusals are explicitly out of batch scope>.
```

## STRATA-<n>-CLOSE.md (single-item closure)

```markdown
# STRATA-HARDENING-1 Item <P-x> — CLOSED

- **Item**: `docs/sjira/v26.10.8/STRATA-HARDENING-1.md` item <P-x>
  (<pack(s)>: <defect class, e.g. FM-PACK-014 unresolvable dependency,
  dead vocabulary, template drift>).
- **Status**: CLOSED <YYYY-MM-DD> (lane <L-n>).
- **Fixing commit**: `<sha>` on `ggen-marketplace` branch `<branch>` —
  `<commit subject>`.
- **Fix shape**: <minimal description of the source-level change: which
  ggen.toml key, ontology term, template block, or gate; why generated
  consumer output does or does not change.>
- **Witnesses** (all executed on the fix commit's subject):
  1. Court `<test-or-script path>` — <n>/<m> passed (<what it really
     exercises: real pack source, real ggen sync, real render>).
  2. Real ggen <version> qualification `<artifact path>`: `<pack>` verdict
     <ALIVE/REFUSED:...> before vs <after>.
  3. <Optional: grep/byte-compare proof that generated output is unchanged,
     e.g. template count 1852 → 1851 with zero consumer diff.>
- **Consumer consequence**: <what the consumer of this pack can now admit or
  no longer sees; any behavior change in generated output, stated exactly.>
```

## Invariants

- Cite SHAs and file paths exactly; re-read witness artifacts from disk at
  write time — never quote counts from memory.
- Status vocabulary: `UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE`, `BLOCKED`,
  `BUILD_BROKEN`, `UNSUPPORTED`, typed `REFUSED:*`.
- A batch closure covers only the items it names; out-of-scope refusals are
  disclosed, not claimed.
