# qualification/positive — RFC-GPACK-001 valid corpus (Appendix D `valid/*`)

The four positive fixtures of the first permanent conformance corpus
(RFC-GPACK-001 v26.9.17, Appendix D). Each fixture pack is exactly the
§90 recommended shape for its role, is strict §7.1 in its manifest, and
self-describes with `gp:profile gp:Portable1` + `gp:authorityCeiling
gp:Construct` (§10 shape). Ticket T02 owns this directory;
`qualification/negative/` is T03, `vectors/` is T04, and the spec pack's
own root manifest, vocabulary, and gates are T01.

Falsifiers for every normative claim below live in
`tests/test_gpack_valid_corpus.py` (repo root). Each guard there has a
sabotage twin (§79) proving it can fire.

## How to run

```bash
# 1. Structural admission of the enclosing spec pack (whole marketplace):
python3.11 scripts/marketplace.py validate

# 2. Real Turtle parse + real SPARQL execution + §91 byte-diff + guards:
python3.11 -m pytest tests/test_gpack_valid_corpus.py -v
```

RDF stack: `rdflib==7.1.4` (same pin as the repository's RDF-consuming CI
workflows). TOML: stdlib `tomllib` (Python 3.11+).

Running the Rust `ggen` / `ggen_igniter` engines against these fixtures is
the wave-2 Appendix E crown and is deliberately out of scope here; these
fixtures pin the declarative state those engines must consume equivalently.

## Fixtures

### minimal-portable-pack — Appendix D `valid/minimal-portable-pack`

The §91 Minimal Portable Example, byte-for-byte: `pack.toml`,
`ontology.ttl`, `queries/message.rq`, `gates/010_required.rq`,
`templates/hello.txt.tera`, and the §91 expected consequence
(`expected/hello.txt`: `Hello from admitted RDF.`). The test suite diffs
every file against the RFC's fenced-block bytes and executes the query
(observed binding: `message = "Hello from admitted RDF."`) and the gate
(observed row count: 0 = pass, §14).

Appendix E crown rows fed: **all six** — `PackDigest_R = PackDigest_I`,
`GraphDigest_R = GraphDigest_I`, `GateVerdicts_R = GateVerdicts_I`,
`CanonicalBindings_R = CanonicalBindings_I`, `TargetBytes_R =
TargetBytes_I`, `Replay_R = Replay_I = PASS`. This fixture is the minimal
complete cross-engine crown subject.

### two-semantic-dependencies — Appendix D `valid/two-semantic-dependencies`

A consumer pack with TWO `gp:requiresPack` dependencies, each a
`gp:PackRequirement` whose `gp:dependencyScope` is EXACTLY `{SEMANTICS}`
(§26 scope algebra; token form witnessed by the §55 receipt envelope's
`"scope": ["SEMANTICS"]`). The dependee packs ship inline under `deps/`
and are semantic-only — no `templates/` — which is lawful per §73 ("A
Core ... pack MAY contain no projections"). Engines without §73 support
MUST report semantic-only execution as `UNSUPPORTED` (§83) rather than
redefine the abstract `Pack` to require projection. A wave-2 court
resolves the `gp:requiresPack` IRIs by registering the `deps/` pack dirs.

Appendix E crown rows fed: `PackDigest` (the digest must cover the
dependency declarations) plus the §96 falsifier row "Dependency scope —
SEMANTICS-only dependency contains projection; projection must not run",
witnessed positively here and negatively by T03's corpus.

### portable-tera-fanout — Appendix D `valid/portable-tera-fanout`

One projection query (`queries/modules.rq`) selecting `?name ?rank` with
`ORDER BY ?rank` — §25 order law: row order is meaningful only when the
query establishes it, and unique ranks make the order total, hence
deterministic. The §22-normalized template
(`templates/module.txt.tera`: `renderer: tera1`, `query: modules`,
`for_each: modules`, `write: managed`) fans out one target per binding
row.

Expected target set, in ORDER BY-derived order (also pinned in
`expected/targets.txt`):

```text
generated/1-alpha.txt
generated/2-beta.txt
generated/3-gamma.txt
```

This is the order-invariance witness for the wave-2 courts: any conforming
engine must derive this exact ordered target set regardless of internal
row storage or file-discovery order (§51, §96 "Order invariance").

Appendix E crown rows fed: `TargetBytes_R = TargetBytes_I` and
`CanonicalBindings_R = CanonicalBindings_I` (the ordered bindings are the
comparison oracle, §24).

### consumer-alias — Appendix D `valid/consumer-alias`

§9 alias law: `consumer.toml` assigns the local alias `payments` to the
canonical `acme-payments-pack` (verbatim §9 example shape). `expected/
receipt.json` pins the receipt fields §9 requires an engine to preserve:

```text
consumer_alias = payments
canonical_name = acme-payments-pack
```

The alias MUST NOT overwrite canonical identity in receipts or dependency
resolution. The fixture directory name (`consumer-alias`) deliberately
differs from the canonical pack name: §9 makes
`directory_name == canonical_name` a MAY for strict marketplace
publication only; local composition need not. No engine may infer
canonical identity from a directory name.

Appendix E crown rows fed: receipt identity inside the "canonical evidence
comparison" — `PackDigest`/subject identity must bind the canonical name,
with `consumer_alias` carried alongside, in both engines' receipts.

## Recorded edges (no silent pruning)

- The spec-pack root `pack.toml`/`ontology.ttl` shipped by T02 are a
  minimum-admission scaffold; T01's vocabulary/gates supersede them at
  merge as a semantic superset. The fixture subtree needs no change then.
- Scope tokens are string literals (`"SEMANTICS"`), per the RFC's own §55
  receipt form. IRI-form scope individuals are T01 vocabulary territory
  and were not invented here.
- Dependees declare `gp:profile gp:Core1` (the profile §73 explicitly
  frees from projections) rather than `gp:Portable1`, which the consumer
  fixture packs carry.
