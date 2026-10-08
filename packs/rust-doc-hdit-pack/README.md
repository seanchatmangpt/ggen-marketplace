# rust-doc-hdit-pack

ggen-first documentation manufacturing for Rust crates. The code surface is
extracted into RDF once; every document is a projection of that graph, and
verification diffs the doc surface against the code surface — never against
an agent's memory of the code.

## Architecture

**Code surface -> RDF.** tree-sitter parses the crate; extraction emits
code-surface facts using the `dhs:` vocabulary in `ontology.ttl`:
`dhs:Module`, `dhs:Function`, `dhs:Struct`, `dhs:Enum`, `dhs:Resource`,
`dhs:Action`, `dhs:Verb`, each with `dhs:signature`, `dhs:params`,
`dhs:defaults`, `dhs:errors`, `dhs:invariants`. Facts load into oxigraph.

**Hypervectors.** For each item `i` with fact set `F(i)`:

```
H_code(i) = sum_{f in F(i)} randvec(hash(f))       # code-surface bundle
H_doc(i)  = sum_{c in Claims(i)} randvec(hash(c))  # doc-surface bundle
```

`randvec` is a fixed-seed bipolar random vector per hash; binding is
elementwise multiply, bundling is majority sum. Similarity is cosine, so a
doc claim that matches a code fact scores ~1 and an invented one scores ~0.

**Three gates** (`courts/doc_quality.court`):

| Gate | Threshold | Measures |
|------|-----------|----------|
| `S_coverage` | >= 0.90 | share of code-surface Verbs covered by >= 1 doc claim |
| `Phi_halluc` | <= 0.001 | share of doc claims with no matching code fact |
| `Q_density` | >= 0.65 | verified facts per 100 words of rendered prose |

Pass on all three -> `doc-hdit:certify` mints a BLAKE3 receipt (via
affidavit) over the rendered docs plus the code-surface store fingerprint.
Any gate failure -> REFUSED, no receipt.

## Execution verbs

| Verb | Effect |
|------|--------|
| `doc-hdit:scaffold` | render Diataxis skeletons from code-surface facts (`queries/ast_extract.rq` -> `templates/*.md.tera`) |
| `doc-hdit:vectorize` | compute `H_code` / `H_doc` hypervectors per item |
| `doc-hdit:audit` | evaluate `S_coverage`, `Phi_halluc`, `Q_density` against the court thresholds |
| `doc-hdit:certify` | on gate pass, mint the BLAKE3 receipt via affidavit |

## Agent-role constraint

`templates/reference.md.tera` is RIGID: `AGENT-FORBIDDEN` markers fence the
tables and agents must not add, edit, reorder, or remove any row. In
`how_to` and `explanation` templates, agents write ONLY inside the bounded
`AGENT-COMMENTARY` `{% comment %}` fences (<= 12 lines, no new code facts).
Anything outside those fences must come from the query output or the
verified-snippet slot.

## Layout

- `ontology.ttl` — code-surface + doc-surface vocabulary
- `queries/ast_extract.rq` — modules -> items -> signatures (+ errors, invariants)
- `templates/` — Diataxis skeletons (`reference`, `how_to`, `explanation`)
- `courts/doc_quality.court` — documented gate thresholds (executable
  enforcement lands with the binary)
