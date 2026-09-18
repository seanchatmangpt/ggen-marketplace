# qualification/ — corpus layout contract

This directory holds the qualification corpus for `ggen-pack-spec-pack`
(RFC-GPACK-001 §77 conformance philosophy, §78 required portable courts,
§79 gate sabotage court, Appendix D first conformance corpus).

## Layout contract (owned by separate tickets)

```text
qualification/
├── README.md        # this contract (T01)
├── positive/        # graphs that MUST pass every gate in gates/        (T02)
├── negative/        # graphs that MUST make at least one gate FIRE     (T03)
└── vectors/         # cross-engine binding/ordering test vectors       (T04)
```

Rules:

1. **positive/** — one Turtle graph per file; each must produce zero rows
   on every `gates/*.rq` (SELECT gate: `Violation = RowCount > 0`, §14).
2. **negative/** — one Turtle graph per file, each named for the refusal it
   provokes (e.g. `missing-name.ttl` → `GPACK-ONTOLOGY-MISSING-NAME`); each
   must produce ≥ 1 violation row naming the expected stable refusal id.
   A negative test is valid only when the attack reached the gate (§15).
3. **vectors/** — canonical binding representation cases (§23–§25): IRI,
   simple literal, datatype literal, language literal, unbound, ORDER BY.
4. Every corpus file must carry the stable refusal id or court id it
   witnesses in a header comment (§16: ids, not prose, are the keys).
5. Corpus graphs are admission subjects, not sources: they never ship in
   `templates/` and never mutate pack source during manufacture (§52).

## Gate sabotage recipe (§79) — reproducible falsifier for THIS scaffold

For every normative gate there must exist a negative witness capable of
causing it to fire; a guard whose removal would not be noticed by its
falsifier is vacuous. The scaffold-level witnesses (executed at T01, and
re-runnable on any graph):

```bash
PACK=packs/ggen-pack-spec-pack

# Runner: exit 0 = zero violation rows (gate pass), exit 1 = gate FIRED.
run_gate() {  # $1 = gate file, $2 = turtle graph
  python3 - "$1" "$2" <<'PY'
import sys, pathlib
from rdflib import Graph
gate, graph = sys.argv[1], sys.argv[2]
g = Graph(); g.parse(graph, format="turtle")
rows = list(g.query(pathlib.Path(gate).read_text()))
print(f"{pathlib.Path(gate).name} vs {pathlib.Path(graph).name}: rows={len(rows)}")
for r in rows: print("  ", tuple(str(x) for x in r))
sys.exit(1 if rows else 0)
PY
}

# Positive witness: the pack's own graph passes both gates (exit 0).
run_gate $PACK/gates/010_identity.rq                      $PACK/ontology.ttl
run_gate $PACK/gates/020_manifest_graph_correspondence.rq $PACK/ontology.ttl

# Sabotage A — drop gp:name from the self-pack: gate 010 must FIRE (exit 1).
python3 -c "
from rdflib import Graph, URIRef
g = Graph(); g.parse('$PACK/ontology.ttl', format='turtle')
p = URIRef('https://ggen.dev/ns/pack#name')
for s, o in list(g.subject_objects(p)):
    if str(s) == 'urn:ggen:pack:ggen-pack-spec-pack':
        g.remove((s, p, o))
g.serialize(destination='/tmp/sabotage-a.ttl', format='turtle')"
run_gate $PACK/gates/010_identity.rq /tmp/sabotage-a.ttl   # expect rows + exit 1

# Sabotage B — add a second distinct gp:name: gate 010 AMBIGUOUS branch fires.
python3 -c "
from rdflib import Graph, URIRef, Literal
g = Graph(); g.parse('$PACK/ontology.ttl', format='turtle')
g.add((URIRef('urn:ggen:pack:ggen-pack-spec-pack'),
       URIRef('https://ggen.dev/ns/pack#name'),
       Literal('ggen-pack-spec-pack-evil')))
g.serialize(destination='/tmp/sabotage-b.ttl', format='turtle')"
run_gate $PACK/gates/010_identity.rq /tmp/sabotage-b.ttl   # expect rows + exit 1

# Sabotage C — mismatch the graph name vs the pinned manifest name: gate 020 fires.
python3 -c "
from rdflib import Graph, URIRef, Literal
g = Graph(); g.parse('$PACK/ontology.ttl', format='turtle')
s = URIRef('urn:ggen:pack:ggen-pack-spec-pack')
p = URIRef('https://ggen.dev/ns/pack#name')
for o in list(g.objects(s, p)):
    g.remove((s, p, o))
g.add((s, p, Literal('some-other-name')))
g.serialize(destination='/tmp/sabotage-c.ttl', format='turtle')"
run_gate $PACK/gates/020_manifest_graph_correspondence.rq /tmp/sabotage-c.ttl  # expect rows + exit 1
```

If any sabotage run returns exit 0, the corresponding gate is vacuous and
the pack is `BUILD_BROKEN`, not qualified.
