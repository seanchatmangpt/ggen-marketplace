# ggen-pack-spec-pack

The executable specification pack for **RFC-GPACK-001 v26.9.17 — the GGEN
Semantic Pack Protocol** (RFC §94). The pack is self-governed by the law it
defines (§93 self-hosting): its own graph describes this pack, and its own
gates run against that graph.

## What ships here

| Path | Role |
|---|---|
| `pack.toml` | Bootstrap manifest, strict §7.1 schema: `[pack]` with `name` / `version` / `description` ONLY. Unknown keys are refused (§7.1, `deny-unknown-fields`). |
| `ontology.ttl` | The canonical `gp:` vocabulary (`https://ggen.dev/ns/pack#`, Appendix B): classes, profiles (§12/§88/§89), renderers (§17), authority ceilings (§46 ladder + §47 default), lifecycle states (§61), pack classes (§11), properties (App. B), typed refusal codes (App. C), and the pack's own self-description (§8, §94). |
| `gates/010_identity.rq` | Court: every `gp:Pack` has exactly one `gp:name` and one `gp:version`. |
| `gates/020_manifest_graph_correspondence.rq` | Court: graph `gp:name` equals the `[pack].name` the pack ships under (`Project(I_S) = I_B`, §8). |
| `qualification/` | Corpus layout contract for the conformance corpus (positive/ and negative/ and vectors/ are owned by separate tickets — see `qualification/README.md`). |

This pack carries no templates and no queries: it is semantic + gate law
only (§73 semantic-only packs, plus admission gates).

## Gate semantics (how courts consume these)

Each gate is a SPARQL SELECT interpreted as a falsifier (§14):

```text
Violation = RowCount > 0        (SELECT gates)
GatePass  = AttemptObserved AND ViolationAbsent
```

- Zero rows on the admitted graph = gate pass.
- Any row = `REFUSED:GATE_VIOLATION` with the row's `?violation` value as
  the stable refusal identity (§16: the id, not the prose, is the
  automation key).
- A gate that never actually executed MUST NOT be reported as passed (§14).
- Gate results bind gate identity, subject graph identity, attempt-observed,
  violation rows, decision (§15).

Every gate declares its stable refusal ids in a header comment and runs its
UNION branches self-contained, so results are declaration-order independent
(§3.8, §51).

## Running the gates

Any conforming SPARQL-over-RDF implementation works. With Python `rdflib`:

```bash
python3 - <<'PY'
import sys, pathlib
from rdflib import Graph
g = Graph()
g.parse("packs/ggen-pack-spec-pack/ontology.ttl", format="turtle")
for gate in sorted(pathlib.Path("packs/ggen-pack-spec-pack/gates").glob("*.rq")):
    rows = list(g.query(pathlib.Path(gate).read_text()))
    print(f"{gate.name}: rows={len(rows)}")
    for r in rows:
        print("  ", tuple(str(x) for x in r))
    if rows:
        sys.exit(1)
PY
```

Exit `0` = both gates passed; exit `1` = a gate fired.

Turtle well-formedness can be cross-checked with an independent parser,
e.g. Raptor (`rapper -i turtle -o ntriples packs/ggen-pack-spec-pack/ontology.ttl`).

## Sabotage court (§79)

For every normative gate, qualification must include a negative witness
capable of causing the gate to fire; a falsifier that passes regardless of
whether the guard exists is presumed vacuous. The reproduction commands are
recorded in `qualification/README.md`.

## Identity

- Canonical name: `ggen-pack-spec-pack` (equal in `pack.toml`, graph
  `gp:name`, and this directory name).
- IRI: `<urn:ggen:pack:ggen-pack-spec-pack>`
- Profile: `gp:Portable1` — Authority ceiling: `gp:Construct` (§47 default,
  never elevated) — Lifecycle: `gp:Candidate`.
