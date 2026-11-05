# dspy-pack

Universal DSPy generation vocabulary for [ggen](https://github.com/seanchatman/ggen) — law
only, zero individuals. Generates `src/dspy_program.py`, `src/dspy_optimize.py`, and
`src/dspy_shacl_signatures.py` from a consumer's own ontology individuals over this pack's
`dspy:` vocabulary.

Verified against the real installed dspy 3.1.3 source tree (not docs prose) via
`inspect.signature()` on every admitted constructor and `compile()` method, and by real
object construction/execution against actual dspy classes. Covers dspy.ai's own tutorials:
general Predict/ChainOfThought modeling, MCP tool use, GEPA and GRPO optimization, GEPA
worked examples, the retrieve-then-reason (RAG) pattern, the 2-hop multi-hop pattern, and
KNN/Parallel/Ensemble/KNNFewShot.

# Consumer Contract

Deps below are pulled by the pack's **projected code** (not by the pack itself); they are
derived mechanically from the template imports:

- `dspy` (`>=3.0`, verified against 3.1.3) — every template imports `dspy`.
- `pydantic` (`>=2.0`) — `dspy_program.py.tmpl` imports `pydantic` for generated
  `BaseModel` field types.
- `mcp` (latest) — `dspy_program.py.tmpl` imports
  `from mcp import ClientSession, StdioServerParameters`.

Install (in the consumer project):

```bash
pip install "dspy>=3.0" "pydantic>=2.0" mcp
```

Failure modes if a dep is missing at runtime:

- `import dspy` → `ModuleNotFoundError: No module named 'dspy'`
- `import pydantic` → `ModuleNotFoundError: No module named 'pydantic'`
- `from mcp import ...` → `ModuleNotFoundError: No module named 'mcp'`

Peer context — what the consumer must supply:

- Its own `dspy:Signature` / `dspy:InputField` / `dspy:OutputField` / `dspy:Module` /
  `dspy:Optimizer` individuals in the consumer's own `.ttl` (the pack ships zero
  individuals; composing it cannot inject a signature, module, or optimizer).
- Metric/reward/reduce function bodies, tool bodies, and
  trainset/valset/devset/eval_kwargs contents are consumer-owned; ggen scaffolds
  `NotImplementedError` stubs and named placeholders.
- MCP consumers additionally supply `dspy:MCPServerConnection` individuals with real
  server commands.

# Verification Court

Pack-level: `gates/010_admission.rq` + `gates/020_shacl_signature_admission.rq` run inside
every consumer `ggen sync run`; `scripts/coverage_check.py` cross-references the ontology
against `evidence/dspy-source-coverage.ttl`.

Consumer-level court (this pack version, run 2026-11-05, lane G12 of the pack-refactor
wave 2): a scratch consumer in `/tmp/g12-consumer` bound the pack by path, ran the real
`ggen sync run --skip-ea-admission` (exit 0, projected `src/dspy_program.py`,
`src/dspy_optimize.py`, `src/dspy_shacl_signatures.py`), then `py_compile` on all three
projected files (exit 0) and a real `import` + construction tier against the installed
dspy 3.1.3 — with an anti-vacuity flip (import of a nonexistent module injected into the
projected output → compile fails, restore → passes). Full commands, exits, and
disclosures: `docs/jira/v26.11.5/receipts/G12.md`.

# See Also

- `ontology.ttl` — the law-only `dspy:` vocabulary (documented caveats on upstream dspy
  3.1.3 defects: unexported SignatureOptimizer, removed TypedPredictor in AvatarOptimizer,
  BetterTogether runtime whitelist)
- `docs/jira/v26.11.5/receipts/G12.md` — this version's court receipt
- ggen monorepo `examples/dspy-*` fixtures + `crates/ggen-engine/tests/dspy_pack_e2e.rs`
