# Second Consumer: xaas Ultracode Loop

Second real pi:/st:/es: consumer for process-intelligence-pack, v26.9.21. Source graph:
`qualification/consumer/xaas-ultracode.ttl` (namespace `xu:`). Vocabulary read from
`xaas/lib/xaas/ultracode/ocel_egress.ex` (16 event types; objects Run, Epoch, Worker, Receipt,
Worktree). qualify_packs.py unions it with `qualification/consumer.ttl` automatically.

## Reproduce

```bash
ggen sync run   # ggen.toml with the pi, st and es packs over xaas-ultracode.ttl
python3 - <<'PY'   # compare-loops over zcode-loop.ttl (graph A/B) and this graph
import rdflib
g = rdflib.Dataset()
g.graph(rdflib.URIRef("urn:loop:zcode")).parse("zcode-loop.ttl")
g.graph(rdflib.URIRef("urn:loop:xaas")).parse("xaas-ultracode.ttl")
print(len(list(g.query(open("queries/compare-loops.rq").read()))))
PY
```

## Recorded result

- ggen sync: 12 files (ts, py, rs, ex for tap, fsm, chain), gates 010-090 green.
- compare-loops.rq: 134 rows; shared terms are only hash algorithm `sha256` and source kind
  `stream-json`; event, object and qualifier vocabularies are disjoint.
- Python reuse: the generated `tap.py` body from `hash_hex` onward is identical to the zcode
  consumer's generated `py/ocel.py`; only the data preamble differs.
- Status of compare-loops.rq moves from toy-only to run over two real consumers.

## See Also

- `queries/compare-loops.rq`
- `qualification/consumer.ttl`
