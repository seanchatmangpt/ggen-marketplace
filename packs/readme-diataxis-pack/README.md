# readme-diataxis-pack

Converts the facts inside a generic "standard-readme"-shaped project description into a
Diataxis-structured docs tree: tutorial (Run Locally), reference (API/env vars), and
explanation (FAQ) pages, projected deterministically from admitted RDF rather than
hand-written prose.

## Scope, stated plainly

All four Diataxis quadrants plus the meta page are now covered: tutorial, reference,
how-to, explanation, and the index/meta pages this pack's design was originally scoped
against. Verified end-to-end through the real `ggen` binary against an isolated consumer
project (see "End-to-end verification" below), not just through SPARQL re-derivation.

## Section -> Diataxis mapping

| Admitted class | Diataxis destination | Why |
|---|---|---|
| `rdx:RunStep` (kind in clone/install/start) | Tutorial | one guided learning path, in order |
| `rdx:ApiEndpoint`, `rdx:ApiParameter`, `rdx:EnvVar` | Reference | exact contract, table-shaped |
| `rdx:RunStep` (kind in deploy/test), `rdx:UsageExample` | How-to | task recipes, not a single learning path |
| `rdx:FaqEntry` | Explanation | rationale, not instruction |
| `rdx:Project`, `rdx:TechStackItem` | Index | project identity, linked from `docs/index.md` |
| `rdx:RoadmapItem`, `rdx:ContactChannel`, `rdx:license` | Meta | outside the four Diataxis quadrants |

## Gates

- `010_required_properties.rq` — refuses any individual missing a property its owning
  template's SELECT needs with no `OPTIONAL`/`COALESCE` fallback, and refuses
  `RunStep.kind` values outside the enumerated set.
- `020_ordering_integrity.rq` — refuses duplicate `rdx:position` within the same
  RunStep-kind or FaqEntry scope (non-deterministic projected ordering).

Both gates were verified directly against `qualification/consumer.ttl` (0 rows) and
against a deliberately broken fixture per gate (010: 2 rows on a step with a missing
`rdx:command` and an unenumerated `kind`; 020: 1 row on a duplicate `position=0` within
`kind="install"`).
