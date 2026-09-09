# chicago-pytest-dataclass-pack — Provenance

Manufactured 2026-09-06 by a test-manufacture lens sweep over
`/Users/sac/gym-ecosystem`. Sibling to `chicago-tdd-tools-pack` (Rust CLI
boundary axis); this pack covers the Python dataclass-projection axis.

## Where the ontology facts came from

Every `cpd:className`, `cpd:fieldName` and field shape in `ontology.ttl` was
read off a real, already-generated file:
`/Users/sac/gym-ecosystem/vendor/autofde-lab/src/autofde_lab/constitution/evidence.py`
(itself `ggen sync run` output from `ontology/evidence.ttl`). Nothing was
inferred from a class name or a repo name.

The repeated structure this pack captures is the ten hand-written
`tests/test_constitution_*_chicago.py` files in autofde-lab, which all repeat
the same four moves per class: real import, `__all__` assertion, real
construction with real values, real `FrozenInstanceError`.

## Verification actually run

```
$ ggen sync run          # in a scratch copy of this pack
"written": ["tests/chicago_dataclass_runtime.py", "tests/test_chicago_dataclass_proof.py"]
graph_hash_hex: 656d68e5cfcd09ea5d931018315689f9fa313c8a68962ad7cfea3031285bab3e

$ .venv/bin/python -m pytest <scratch>/tests/test_chicago_dataclass_proof.py -q
..........                                                               [100%]
10 passed in 0.25s
```

Falsifier (a sabotaged copy: one `cpd:fieldName "reads_manifest"` renamed to
`reads_manifest_TYPO`, regenerated, re-run):

```
E  AssertionError: VerifierRun has no field(s) ['reads_manifest_TYPO']; real fields are ['reads_manifest']
1 failed, 9 passed in 0.20s
```

So the generated proof really binds to the module on disk; it cannot pass on a
wrong fact.

Gate queries were run for real with rdflib over `ontology.ttl` (184 triples):
all four returned 0 violations.

## Authority boundary

This pack carries NO runtime actuation authority, the same boundary
`chicago-tdd-tools-pack` establishes. Generated output only imports modules and
constructs frozen data objects. `gates/040_no_actuation_authority.rq` fails any
`cpd:sampleExpr` that smells like actuation (`subprocess`, `Popen`, `open(`,
`requests.`, `eval(`, `__import__`). Consequential DO stays behind GymAct/BRCE
admission.

## Vocabulary reuse

`rdfs:`, `owl:`, `xsd:`, `dcterms:` (title/description/created), `prov:Entity`
on the proof class. `cpd:` terms are minted only for the test-shape concepts no
public vocabulary covers (field sample expressions, frozen-ness, exhaustive
export lists).
