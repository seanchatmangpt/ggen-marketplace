# Receipt: ga-2-aoq-gates (PG-A6 step 2, lane GA-2)

Standing: **ALIVE** — every claim below is a command run this session with its real exit.

## Deliverables (all under /Users/sac/ggen-marketplace/packs/aoq-pack/)

- `gates/010_header_field_closure.rq` .. `090_grounding_regex.rq` — 9 gates, locked PG-A6 table, each with `# MESSAGE:` line 1, `# Anti-vacuity:` naming its fail-witness mutation, deterministic `ORDER BY` (E0013).
- `witnesses/pass/*.ttl` (9) — one clean 64-byte AOQ1 seed graph (header chain 0→4→6→58-end-64, in-band constant FM-AOQ-001, BLOCKED KemParam, labeled Epoch/StreamType, frame).
- `witnesses/fail/*.ttl` (9) — the seed with exactly the named PG-A6 mutation applied:
  010 drop goName · 020 out-of-band 0x4347A009 · 030 offset 4→5 (chain break) · 040 wireKind "u96" · 050 unlabeled Epoch member · 060 strip `aoq:seam "hand-law"` · 070 frozen literal 0x43470004 · 080 all Epoch individuals removed · 090 sizeBytes 64→24 (R-1 flip).
- `gate-court.toml` — mirrors cgap-pack schema `ggen.semantic-gate-witness-court/1` verbatim (exact-stem, require_pass ∧ require_fail).

## Verification ladder (real commands, real exits)

1. **Structural court**: `python3 scripts/check_gate_witness_courts.py --packs /tmp/ga2-courts --report /tmp/ga2-court.json` (aoq-pack isolated via symlink dir; full-packs run REFUSES on cgap-pack's pre-existing `arrow_layout` witness gap — not this lane's surface) → `{"case_count":9,...,"standing":"ALIVE"}`, exit 0.
2. **Syntax**: real `sparql_gate_check` binary built this session (`cargo build -p ggen-graph --bin sparql_gate_check`, 33s) run over a scratch gates dir (its 6 known gates + my 9; the binary hardcodes its own repo's gate list, so it cannot be pointed at a foreign gates dir directly — limitation disclosed) → `SYNTAX_OK` ×9, zero syntax_error lines. The 6 ggen repo gates semantically FAIL against AOQ's ontology (foreign gates, foreign ontology — expected, not a gate defect).
3. **Semantic witness court** (rdflib 7.6.0, real SPARQL engine; harness `/tmp/ga2_sparql_gate_check.py`):
   - parse pass 9/9; ORDER BY present 9/9; `# MESSAGE:`/`# Anti-vacuity:` headers 9/9;
   - ontology.ttl → 0 rows on all 9 (the canonical graph passes its own law);
   - pass witnesses → 0 rows on all 9;
   - fail witnesses → ≥1 row on all 9 (030 gives 2 rows, both direct consequences of the single offset move).
4. **Mutation spot-check**: fail rows verified to land on the named mutation, not side defects (030: "f0 end=4 next=5 at f1"; 090: "header sizeBytes must be 64 (R-1), got 24"; 070: subject `urn:aoq:witness:fail/legacy`, value 0x43470004).

## Disclosures

- **GA-1 reconciliation**: GA-1's `ontology.ttl` landed mid-lane and was READ and used as the sole vocabulary authority (aoq: = `urn:aoq:`, wireKind closed set {u16,u32,u64,reserved-zero,fnv1a32}, frozen band literals as no-underscore strings "0x4347A001..A008"). No field-table divergence to reconcile: PG-A6's `alignmentBytes==8` item has no corresponding property in the landed ontology, so gate 090 grounds on the landed law (`aoq:sizeBytes 64` on the Header) — no property was invented.
- **Validator note**: the ggen `sparql_gate_check` binary's semantic pass covers only its hardcoded gate list, so witness execution used rdflib as the real engine; the binary contributed the oxigraph syntax pass. A scratch-gates-dir workaround was used to route the 9 gates through the real parser.

## Standing

ALIVE — 9 gates, 9+9 witnesses, court structurally qualified, syntax + semantics witnessed green this session. Consumer-side shim-court (ggen sync run against cgap, per PG-A6 §3) and pack.toml/templates are other lanes' surfaces; not run here.
