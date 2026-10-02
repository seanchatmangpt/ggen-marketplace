# Semantic Gate Witness Court Pack

Reusable GGen manufacturing capital for turning a directory of semantic gates into an explicit, replayable qualification court.

## Consumer contract

A consumer owns its semantic gates and witnesses. The court owns the reusable correspondence law:

- `gates/<case>.rq` or `.sparql` is an admitted semantic gate.
- `witnesses/pass/<case>.<ext>` is a positive witness that must be accepted by that gate.
- `witnesses/fail/<case>.<ext>` is a negative witness that must be refused when `require_fail = true`.
- `gate-court.toml` declares directories, extensions, and whether pass/fail coverage is required.
- case identity is exact filename stem; missing and orphan witnesses fail closed.
- the court emits deterministic JSON with SHA-256 identities for gates and executed witnesses.
- an optional runner delegates gate semantics without coupling the pack to a SPARQL engine; it is invoked without a shell and must return zero only when the requested expectation is observed.

Minimal consumer configuration:

```toml
[court]
schema = "ggen.semantic-gate-witness-court/1"
case_key = "exact-stem"
gate_dir = "gates"
pass_dir = "witnesses/pass"
fail_dir = "witnesses/fail"
require_pass = true
require_fail = false
```

The generated court can be run structurally with `python3 generated/semantic_gate_witness_court.py <pack-root>` or semantically with `--runner '... {gate} {witness} {expectation} ...'` once a consumer supplies its engine-specific adapter.

## Canonical runner (v26.9.30)

This pack also owns the canonical semantic runner: `templates/semantic-runner.py.tera`,
the rdflib-based adapter that judges `gates/*.rq` against pass/fail witnesses with the
exactly-one-gate-fires law. Consumer packs carry `runners/semantic_runner.py` as a
byte-identical projection of that template; byte-identity is enforced by
`tests/test_contract.py::test_consumer_runners_are_byte_identical_projections`.
Edit the template, then re-project every consumer copy — never edit a copy.

Mechanism record (v26.9.30 consolidation wave, lane 7):

- A `gate-court.toml` `runner` field pointing at a shared cross-pack runner was
  examined and REFUSED as a mechanism: nothing in `scripts/check_gate_witness_courts.py`
  reads `runner` (only `gate_dir`/`pass_dir`/`fail_dir` are `safe_dir`-guarded), and the
  runner itself resolves its gates relative to its own file location
  (`PACK_ROOT = Path(__file__).resolve().parents[1]`), so a runner file outside the
  consumer pack would judge the wrong `gates/` directory and refuse every gate
  (exit 3). Fixing that means changing the root-resolution law — a behavior change.
- Dedup is therefore template + byte-identical projections (mechanism B). The quad
  affidavit-consumer, affidavit-trust-plane, capability-closure and wasi-json-abi
  shipped one byte-identical runner (ancestor sha256
  `b82b63220cc004032700a111b682d5f72c30387addffd15eaaa8de0f26a7badd`); it is now
  projected from this template (canonical sha256
  `81d1b9e1af2f362b0879e3c5d7fd4371eeb6dabe75bc3f3e673e5d551f6c4f08`). A template
  cannot carry its own digest (fixed point); the ancestor digest is recorded instead.
- Per-pack `gate-court.toml` files cannot be shared either: the checker hardcodes
  `pack / "gate-court.toml"` and `safe_dir` refuses `..`, so per-pack configs are the
  design, not drift. The shared byte-strings across the 18 configured courts are the
  `[court]` table above plus the standard runner invocation line.
- Deliberately divergent runners (premature-actuation, interchangeable-parts,
  strategic-doctrine, greene-licensing families) are out of scope: consolidating them
  changes behavior and requires witness reruns.
