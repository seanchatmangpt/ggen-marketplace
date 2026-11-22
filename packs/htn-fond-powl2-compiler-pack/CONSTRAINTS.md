# CONSTRAINTS — htn-fond-powl2-compiler-pack

Standing: **UNVERIFIED / scaffold** (not a live compiler pack; no codegen)

Treat any C4 / inventory claim that this pack “compiles ferroplan →
`%Smalt.Powl2{}`” as **FAKE-ALIVE** until templates exist and qualify twice.
This tree is constraints + SELECT gate stubs + a vocabulary scaffold only.

Empty manufacture dirs (intentionally vacant — do **not** fake `.tera` /
sync output):

| Dir | On-disk state |
|---|---|
| `templates/` | empty |
| `queries/` | empty |
| `ontology/` | empty (root `ontology.ttl` is the only TTL) |
| `qualification/witnesses/` | empty |

These six go-locks plus the L39 bridge survey are **hard** for any authoring
or qualify pass. Full pack codegen waits until cindy sjira docs + these locks
are reconciled. Never touch `fibo/packs.toml` / `verify_pins.py` until
`python3.11 scripts/marketplace.py check htn-fond-powl2-compiler-pack`
qualifies twice.

## Go locks (ordered)

### 1. bcinr first — do not reinvent the ferroplan→POWL tape

Inspect and **call/adapt** before writing a new UniversalPlan→`%Smalt.Powl2{}` pass:

| Artifact | Path |
|---|---|
| Tape bridge | `/Users/sac/ggen/crates/bcinr-pddl/src/powl_bridge.rs` |
| WF-net→POWL tree | `/Users/sac/ggen/crates/powl2-decompose/` (workspace-excluded; on disk) |
| NAT-FAC sim/judge | `/Users/sac/natfac/docs/sim/NAT-FAC-SIM.md` |
| L39 receipt | `/Users/sac/cindy/docs/sjira/v26.11.19/receipts/L39-ferroplan-powl2-bridge.md` |

`powl_bridge` law (`temporal_plan_to_powl_tape`):

- `MAX_POWL_TAPE_STEPS = 64`
- `n > 64` → `Err(Pddl8Error::BoundExceeded)` (refuse; **never** silent truncate)
- per step `i`: `succ_mask = 1u64 << i`
- `pred_mask` = OR of `1u64 << j` for finished predecessors (`prev.end <= step.start`, ε=1e-9), then transitive reduction
- concurrent (overlapping intervals) → no pred edge

Ferroplan owns HTN/FOND **policy solve**. The temporal-plan → POWL **tape**
lowerer already lives in `bcinr-pddl::powl_bridge`. **Do not invent a parallel
ferroplan→Powl2 encoder.**

### 2. Three 64-bit surfaces — keep separate (L39)

| Surface | Path | Bit `i` means | Cap |
|---|---|---|---|
| **A. Plan tape** | `TemporalPlan` → `powl_bridge` → `PowlOpSpec` / `bcinr_powl::Powl64Op` | tape **slot** | 64 ops |
| **B. Hierarchical Powl** | WF-net → `powl2-decompose::convert` → `Powl` tree | N/A (tree, not tape) | separability refusal |
| **C. OCEL place marking** | place IRI → `powl:slotIndex` / bitIndex 0..63 → u64 | OCEL **place** token | 64 places |

A and C both use `u64` / `1 << i` but index **different domains**. Conflating
them is the reinvent hazard. B is Kourani Stage-1 (`Leaf` / `PartialOrder` /
`Choice`), not a flat tape — do not reimplement `convert`.

### 3. cgap hosts marking — not `fnox-mark`

Host the `no_std` u64 OCEL2 marking & branchless transition kernel in
`/Users/sac/cgap`:

- `cgap-bosym`
- `cgap-ocel2`
- `cgap-branchless/src/swar.rs`

`cgap` is the rename of `avec`. With `frozen-duckdb`, that stack is the ~97%
OCEL2 compression source (`~480 B` verbose JSON event → `8 B` u64 atom).
Also see `wasm4pm/src/hot_kernels.rs` (`Marking4`). **Do not create a separate
`fnox-mark` crate.**

### 4. 736-byte PCCf hot envelope (exact)

```
736 = 64-byte AOQ1/PCCf header + 672-byte Bulletproof
```

Header (bytes `0..63`):

| Offset | Size | Field |
|---|---:|---|
| `0..7` | 8 | u64 compressed OCEL 2.0 terminal marking `m^(t)` |
| `8..23` | 16 | Epoch-permuted AID / StreamType intent slot |
| `24..55` | 32 | BLAKE3 MMR/SMT epoch lease & detached ML-DSA-65 anchor digest |
| `56..63` | 8 | Monotonic epoch + alignment witness (`gamma = 0`) |

Body: bytes `64..735` = single-range homomorphic Bulletproof (672 B).

ML-DSA-65 signatures (3309 B) live on the **Epoch Lease / Batch Checkpoint**
root out-of-band — **not** inline per packet. Curve unify:
`curve25519-dalek-ng` → `curve25519-dalek` v4 before wiring `admit_pccf`.

A14's alternate field table in `06-specs/A14-marketplace-pack.md` §8 is
**superseded** by this lock until reconciled.

### 5. SRL pccf in graphlaw leaf

Write PCCf admission in PurRDF **SRL** with checked stratification
(`stratify_rules`), **never** unstratified N3 `log:notIncludes`.

- Leaf: `/Users/sac/graphlaw/src/pccf.rs` (`admit_pccf`)
- Do **not** modify the Step enum
- Do **not** add a duckdb cargo feature
- Keep `priv/graphlaw.wasm` (~63 MB, frozen-duckdb linked by law) as
  server/enclave admission; browser/edge verifier is a tiny standalone
  wasm-bindgen crate (`pccf-verifier-wasm` or inside `cgap-ocel2`), target
  `< 250 KB`, checking the 736-byte envelope only

### 6. SELECT gates only (marketplace.py ignores ASK)

Every file under `gates/*.rq` **must** be:

```sparql
SELECT ?violation ?subject
```

- 0 rows = PASS
- ≥ 1 row = REFUSED

`scripts/marketplace.py` **silently ignores ASK**. Cindy Wave G / sjira gates
for this pack must not emit ASK. `[pack]` in `pack.toml` holds **only**
`name`, `version`, `description`. Qualify twice via:

```sh
python3.11 scripts/marketplace.py check htn-fond-powl2-compiler-pack
```

### 7. cindy prefix alignment

Ontology prefixes must align 1:1 across cindy, ggen-marketplace, smalt, cgap,
graphlaw, and fnox (cindy A13):

| Prefix | IRI |
|---|---|
| `pp:` | `https://ggen.dev/ontology/planning-policy#` |
| `powl:` | `https://ggen.dev/ontology/powl2#` |
| `pccf:` | `https://ggen.dev/ontology/pccf#` |
| `vin:` | `https://ggen.dev/ontology/vin-repair#` |

Reconcile any A14 `hf:` / `urn:hfpowl2:` draft onto these IRIs before codegen.
Source census: `/Users/sac/cindy/docs/jira/v26.11.19/` (and sjira mirror).
Note: `/Users/sac/cindy` has **no `.git`** — cindy receipts are files only;
commits for this pack land in ggen-marketplace.

## Scaffold policy

- This drop: `CONSTRAINTS.md`, `STATUS.md`, minimal root `ontology.ttl`,
  SELECT gate stubs, pack receipt. **No** full template/codegen until docs
  ready. Do not invent `.tera` under `templates/`, SPARQL under `queries/`,
  or witnesses under `qualification/witnesses/` to look ALIVE.
- Pinning: **forbidden** until qualify. Leave `fibo/packs.toml` and
  `verify_pins.py` untouched.
- Flip Standing past UNVERIFIED only from a receipt that cites real
  `templates/*.tera` renders + twice-green
  `python3.11 scripts/marketplace.py check htn-fond-powl2-compiler-pack`.
