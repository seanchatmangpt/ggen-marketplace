# semantic-cad-bim consumer example

A consumer project manufacturing from the `industry-semantic-cad-bim` pack
(the IND-6 pillar-gate lane's consumer face).

```text
examples/industry/semantic-cad-bim/
└── consumer/
    ├── ggen.toml     # references ../../../../packs/industry-semantic-cad-bim by path
    └── ontology.ttl  # a minimal, pillar-lawful design snapshot
```

Run it:

```bash
cd examples/industry/semantic-cad-bim/consumer
ggen sync run
cat output/pillar-gates.md
```

The consumer ontology is silent under all seven pack gates (G1 storey
containment, G2 revision predecessor, G3 orphan geometry, G4/P1 design
isolation, G5/P2 attestation, G6/P3 proposer-judge, G7/P5 Merkle seal) and
SHACL-conforms against `packs/industry-semantic-cad-bim/ontology/shapes.ttl` — the graph IS the pass witness
for the pillar laws. Sync is byte-identical across runs
(sha256 `992ec6d1f5509fca…`).

## See Also

- [Pillar→gate mapping](../../../packs/industry-semantic-cad-bim/PILLARS.md)
- [hello-pack example](../../hello-pack/README.md)
