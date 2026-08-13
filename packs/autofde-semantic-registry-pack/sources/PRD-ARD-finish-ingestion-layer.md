# PRD/ARD — finish the acquisition → admission ingestion layer

## Executive summary

PR #15 (`agent/vendor-public-semantic-sources`, draft) built the **acquisition layer**:
`sources.lock.toml` (30 real, `kind`-typed public semantic authorities) and `materialize.py`
(a fail-closed, sha256-pinned vendoring script). Separately, this session built the
**admission/consumption layer** in `~/gymact` and `~/autofde-lab`:
`public-ontology-admission-pack`, generating a real `is_admitted()`/`classify()` Python API
from an ontology of `pa:PublicAuthority`/`pa:AdmittedClass` individuals.

**Standing, stated per `standing-law.md` vocabulary before any other section**: `PARTIAL_ALIVE`.
Nothing in this document claims the two layers are connected — they are not. The admission
pack's 11 classes (PROV-O, ORG, SKOS) are hand-transcribed RDF, written from live WebFetch
verification during this session, not generated from `materialize.py`'s output, because
`materialize.py` has never actually been executed and observed in a session with live network
access. This PRD's entire scope is closing that one real gap — replacing hand-transcription
with mechanical ingestion from real vendored bytes — not re-describing either layer as if it
were already whole.

**Explicit, previously-flagged unverified claim, restated here so it does not silently
propagate**: `sony-principal-fde-public-semantics.md` (this same PR) states MovieLabs' OMC
"was co-developed with Sony Pictures Entertainment and the other major studios." A direct
WebFetch of `https://mc.movielabs.com/docs/ontology/` this session did **not** confirm that
sentence — the page returned only a navigation/TOC with no development-history content. This
is `UNVERIFIED`, not false — a deeper MovieLabs "about"/credits page may substantiate it — but
it must not be repeated as fact (e.g. in an interview) without that further check.

## Grounding: what already exists, real, confirmed this session

- `packs/autofde-semantic-registry-pack/sources/sources.lock.toml` — 30 real `[[source]]`
  entries, each `kind`-typed (`ontology`/`taxonomy`/`schema-standard`/`protocol-schema`/
  `knowledge-base`/`rights-vocabulary`/`controlled-vocabulary-family`). Spot-verified this
  session (WebFetch): `org` (`https://www.w3.org/ns/org.ttl`) and `dcat-3`
  (`https://www.w3.org/ns/dcat.ttl`) both resolve to real Turtle. `prov-o`, `org`, `dcat-3`,
  `dqv`, `shacl`, `schema-org` are `mode = "vendor"` with a real `retrieval_url`; `skos` is
  `mode = "reference"` (no `retrieval_url`) despite SKOS having a real, directly-fetchable RDF
  representation at `http://www.w3.org/2004/02/skos/core#` (confirmed this session via
  `https://www.w3.org/TR/skos-reference/`) — this is a real, fixable inconsistency, not a
  deliberate scoping choice documented anywhere in the PR.
- `packs/autofde-semantic-registry-pack/sources/materialize.py` — real, fail-closed: refuses
  any non-`vendor`-mode entry, refuses a missing `retrieval_url`, refuses a sha256 mismatch,
  emits a `materialization-receipt.json` with per-source standing
  (`ALIVE`/`PARTIAL_ALIVE`/`BLOCKED`/`REFUSED`/`UNSUPPORTED`). **Never executed and observed
  this session or, per the PR's own text, the session that authored it** ("this execution
  environment has no outbound DNS/network... actual retrieval is currently BLOCKED"). This
  session's own environment *does* have working network access (two real WebFetches
  succeeded) — the `BLOCKED` standing is specific to whatever environment produced the PR, not
  a property of the script itself.
- `~/gymact/ggen/public-ontology-admission-pack/` and `~/autofde-lab/ontology/public-ontology-
  admission.ttl` (this session) — real, working admission layer: `ontology.ttl` (3 authorities,
  11 classes, hand-transcribed with inline WebFetch-verification comments), one gate
  (`010_admission_completeness.rq`, proven this session to both pass and refuse a real
  corrupted fact), two generic Tera templates that required **zero changes** when a third
  authority (SKOS) was added. Both repos' generated tests are fully SPARQL-derived — no
  hardcoded class/authority counts remain, after a real `mode="Create"`-vs-`"Overwrite"` drift
  bug was caught and fixed this session (`autofde-lab`'s `ggen.toml`).
- The two layers **do not reference each other anywhere in either codebase** — confirmed by
  the fact that `public-ontology-admission-pack/ontology.ttl`'s grounding comments cite
  "verified live (WebFetch, this session)," never a `sources.lock.toml` entry or a
  `materialization-receipt.json` path.

## PRD — what this system must do

### Goal

Replace the admission layer's hand-transcribed ontology facts with facts mechanically ingested
from `materialize.py`'s real vendored bytes, for the subset of `sources.lock.toml` entries
that are native RDF/OWL (`kind = "ontology"`) — closing the acquisition↔admission gap for the
smallest, already-scoped slice, not all 30 entries.

### Non-goals (explicit)

- Does **not** attempt ingestion for the other ~24 non-`kind="ontology"` entries
  (`taxonomy`/`schema-standard`/`protocol-schema`/`knowledge-base`/rights vocabularies) — each
  of those kinds needs its own one-time projection script (JSON/STIX/OpenAPI → RDF), a
  materially different and larger engineering task than parsing a `.ttl` file, named here as
  deferred, not silently absorbed into FR3 below.
- Does **not** claim `materialize.py` has been run and produced real bytes — FR2 below is
  "execute it for real, in an environment with network," which this PRD schedules but does not
  itself perform (this document is a spec, not an execution transcript).
- Does **not** repeat the MovieLabs/SPE co-development claim as fact anywhere it produces.
- Does **not** attempt the domain-namespaced package split (`admission/` subpackage) floated
  in the earlier "what would using all of those look like" discussion — premature until class
  count actually grows past the current 11.

### Functional requirements

1. **FR1 — Fix `skos`'s `sources.lock.toml` entry**: change `mode = "reference"` to
   `mode = "vendor"` and add `retrieval_url = "http://www.w3.org/2004/02/skos/core#"` (or the
   equivalent `.ttl`-suffixed namespace document, whichever `materialize.py`'s real
   content-negotiation `Accept` header resolves to `text/turtle` — verify at execution time,
   don't assume the URL shape from `org`/`prov-o`'s pattern without checking). Smallest real
   fix, unblocks FR2 covering all 6 real `kind="ontology"` + vendor-eligible entries
   (`prov-o`, `dcat-3`, `dqv`, `org`, `shacl`, `skos`) instead of 5.
2. **FR2 — Execute `materialize.py` for real**, in a network-enabled context (this session's
   own environment has confirmed network access — use it, or an equivalent CI runner).
   Commit the resulting `vendor/<id>/source.ttl` + `receipt.json` payloads and the top-level
   `materialization-receipt.json`. This converts every `kind="ontology"`+`vendor`-mode
   entry's standing from `BLOCKED` to a real, observed `ALIVE`/`PARTIAL_ALIVE` with a real
   sha256 digest — the literal "next crown" already named in the PR's own text.
3. **FR3 — Native-RDF ingestion script**: a new `sources/ingest_native_rdf.py` (or
   equivalent), that for each vendored `kind="ontology"` payload from FR2, parses the real
   `.ttl` and emits `pa:AdmittedClass` individuals for **every** real `owl:Class`/`rdfs:Class`
   found — not a hand-picked subset like this session's 3-of-9 ORG classes or 3-of-3 PROV-O
   classes (PROV-O's 3 admitted classes happen to be its only 3 starting-point classes, so
   that one is already complete; ORG's 4-of-9 is not). Output: a regenerated
   `public-ontology-admission.ttl` in both `gymact` and `autofde-lab`, replacing the
   hand-typed version, with each `pa:PublicAuthority` individual gaining a new
   `pa:materializationReceipt` property citing the real `receipt.json` path from FR2 —
   provenance becomes the vendored byte, not a session's inline comment.
4. **FR4 — Per-`kind` gate for `ontology`**: extend `010_admission_completeness.rq` (or add a
   sibling gate) refusing any `pa:AdmittedClass` whose `pa:belongsTo` authority has no
   `pa:materializationReceipt` — i.e., once FR3 exists, hand-typed-without-provenance classes
   become structurally refused, not just discouraged by convention.

### Non-functional requirements

- Idempotency: FR3's ingestion script run twice against the same vendored bytes must produce
  byte-identical `public-ontology-admission.ttl` output (mirrors the `ggen sync run` twice /
  diff proof already established as this session's own verification convention).
  Non-determinism risk: RDF individual ordering from a Turtle parser is not guaranteed stable
  — FR3 must sort emitted individuals by a stable key (e.g. class IRI) before serializing.
- No class may be admitted without either (a) a real `pa:materializationReceipt` (FR3's path)
  or (b) an explicit, named "hand-transcribed, verified live this session on `<date>`" comment
  (this session's current pattern) — never silently unattributed.

## ARD — how it is built

### Components

- **Acquisition** (`materialize.py`, real, unmodified by this PRD except FR1's one-line lock
  fix): fetches, pins, receipts. Already built.
- **Ingestion** (`ingest_native_rdf.py`, FR3, new): parses vendored `.ttl`, walks `owl:Class`/
  `rdfs:Class` triples via a real RDF library (the ingestion script's own dependency — not yet
  chosen; `rdflib` is the obvious real candidate given `materialize.py`'s existing Python-only
  toolchain, but confirm no license/dependency conflict with either consuming repo before
  committing to it), emits `pa:` individuals.
- **Admission** (the existing `public-ontology-admission-pack` in both `gymact`/`autofde-lab`,
  unmodified templates): consumes whatever `public-ontology-admission.ttl` it's given,
  hand-typed or ingested — this is the load-bearing proof from this session (SKOS added with
  zero template changes) that FR3's mechanically-larger ontology needs no template changes
  either.

### Data flow

```
sources.lock.toml (FR1: skos -> vendor mode)
  -> materialize.py (FR2: executed for real)
  -> vendor/<id>/source.ttl + receipt.json  [real bytes, real digests]
  -> ingest_native_rdf.py (FR3, new)         [real owl:Class/rdfs:Class walk, sorted output]
  -> public-ontology-admission.ttl            [regenerated, provenance-linked, both repos]
  -> gate (FR4: requires materializationReceipt)
  -> admission.py.tmpl / .tera (UNCHANGED)    [proven generic this session]
  -> gymact + autofde-lab admission.py        [same shape, mechanically larger]
```

### Rollout

1. FR1 (lock fix) — smallest, unblocks FR2's full 6-entry coverage.
2. FR2 (real execution) — requires a network-enabled environment; this session's own
   environment is one candidate, confirm before assuming CI is required.
3. FR3 (ingestion script) — the real new code in this PRD; depends on FR2's real bytes
   existing to parse against.
4. FR4 (gate) — depends on FR3's `pa:materializationReceipt` property existing to check for.
5. Explicitly deferred: the other ~24 non-ontology-kind sources' projection scripts — each is
   its own future PRD, not folded in here.

## Verification

- FR1: `sources.lock.toml`'s `skos` entry has a real `retrieval_url` that `materialize.py`
  successfully fetches (real command, real output, this session or the one that executes it).
- FR2: `vendor/skos/receipt.json` (and the other 5 `kind="ontology"` entries') exists with
  `standing: ALIVE` and a real sha256 matching a fresh independent fetch of the same URL.
- FR3: `ingest_native_rdf.py` run against FR2's real vendored PROV-O bytes produces at least
  the 3 classes this session already hand-verified (`Entity`/`Activity`/`Agent`) — a real
  regression check against the one authority already known-complete.
- FR4: a real negative-case probe — an admitted class with no `materializationReceipt` — is
  shown refusing the gate, mirroring `010_admission_completeness.rq`'s already-proven pattern.
- Before this PRD's own claims are cited elsewhere (e.g. an interview), re-verify the
  MovieLabs/SPE sentence against a real, deeper MovieLabs source, not left as `UNVERIFIED`
  indefinitely if it's going to be used.
