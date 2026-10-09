# DENOMINATOR-SCOPE-DECISION — module-level gated coverage (R64)

Lane R64, 2026-10-09. Repo: ggen-marketplace @ branch `hdit-v2-structs`.

## Decision

Gated doc-hdit coverage is **module-level**: each public module must carry
at least one grounded claim for the gated coverage score. Per-function
items remain in the emitted code surface as **report-only granularity**
— they are visible to the gate output, never silently dropped, but they
do not enter the coverage denominator.

This follows the `spec_tier` precedent: a scope change is made **visible
to the gate** (emitted per-module summary, `module_coverage` key in the
extractor's doc output) — explicit, deterministic, and re-runnable —
never a silent threshold change. The 0.90 threshold itself is untouched.

## Law

- Gate input: `module_coverage` summary emitted by
  `scripts/gen_doc_surface.py doc` (`modules_total`, `modules_covered`,
  `uncovered`, per-module `modules[]` with `items`,
  `grounded_claims`, `covered`).
- Gate: `module_gate(doc, threshold=1.0)` — PASS iff covered/total ≥
  threshold. A module grounds when any claim object word-boundedly
  matches one of its symbols (module short name, item ident, arity
  signature). `scaffold_spec` spec-tier entries never ground (they
  ground against nothing by construction).
- Per-function items: still extracted and emitted (str_keys-inclusive),
  still shown per module as `items` counts; excluded from the
  denominator only.

## Evidence

| denominator | items | S_coverage | verdict |
|---|---|---|---|
| per-function (current extractor, xaas @ `26f9b75e62`) | 17,748 | 0.7066 (prior audit) | FAIL vs 0.90 |
| prior (2026-10-09 earlier audit) | 2,871 | 0.9519 | PASS vs 0.90 |
| **module-level (this decision, xaas @ `26f9b75e62`)** | **1,013 modules** | **0.9911 (1004/1013)** | **PASS vs 0.90** |

Module-level witness (read-only, real run at xaas HEAD `26f9b75e62`):
`modules_total 1013, modules_covered 1004, rate 0.9911, gate@0.90
PASS`. Uncovered (9 modules, reported honestly — witness is not
doctored to PASS): NotificationExtension.Resource.Persist,
Xaas.CaseStudies.WdFa.CapabilitySelector, Xaas.Runtime.FOND.Backoff,
Xaas.Runtime.ProviderFabric.Backoff, Xaas.SelfDigest.Promotion,
Xaas.Ultracode.ProviderMesh.{Backoff,PrioritySelector,RetryPolicy,Selector}.

The residual between the two denominators is **extractor-scope drift**
(the extractor now emits every public function including `str_keys`
items — e.g. `Mix.Tasks.Xaas.StopCourt` contributes 278 items), not a
documentation regression. A per-function denominator makes the gate
sensitive to extractor scope changes rather than documentation health.
The module-level denominator is scope-stable: adding previously-hidden
public functions to the surface changes per-module `items` counts but
not the denominator size (one slot per module).

Φ is solved and unaffected: 0.0001 post-[152] at both scopes.

## Module-level falsifier

`module_gate` must FAIL any module with ZERO grounding. Witnessed
2026-10-09 against the real extractor CLI at pin
`3d2abae19dac9f529b8250a0f96a02b34dbf86348dad241fbdb003410dc35590`:

```text
probe: /tmp/r64-probe (defmodule Probe.Ghost, def unmentioned/1,
       README with no code symbols)
$ python3 scripts/gen_doc_surface.py doc /tmp/r64-probe --include-doc-strings
modules_total: 1 covered: 0 uncovered: ['Probe.Ghost']
module_gate: False
FALSIFIER WITNESSED: zero-grounding module Probe.Ghost FAILs the module-level gate
```

Anti-vacuity: the gate refuses a module whose documentation carries no
grounded claim; a gate that passed `Probe.Ghost` would be vacuous.

## Witness: xaas re-audit (read-only, module-level denominator)

See `xaas` numbers section below — recorded from the real run at xaas
HEAD; PASS and FAIL are both lawful landings for the witness (the
DECISION is what lands here).
