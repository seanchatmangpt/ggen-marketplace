# docs-diataxis-pack

Multi-page Diataxis documentation pack. Generalizes `readme-diataxis-pack`
(single README-shaped page set) into a corpus where the consumer declares
ordered pages across all four quadrants plus SUMMARY.md navigation.

## Shape

Consumer RDF facts (own namespace
`https://seanchatmangpt.github.io/ggen-marketplace/docs-diataxis#`):

- `ddx:Book` — singleton; `dcterms:title`.
- `ddx:Page` — `dcterms:title`, `ddx:position` (order within quadrant),
  `ddx:quadrant` (`tutorial|how-to|reference|explanation`), `ddx:relPath`
  (output path, must end `.md`), `ddx:body` (markdown text).

Projections: one markdown file per `ddx:Page` (dynamic `to: "{{ relPath }}"`),
a quadrant-grouped `SUMMARY.md`, and an `index.md` entry point.

## Gates (fail-closed)

- `010_required_properties.rq` — every Book/Page carries the properties its
  template SELECT reads; any row = typed FM-PACK-013 refusal.
- `020_structure_integrity.rq` — quadrant enum membership, duplicate
  relPath (write collision), duplicate position within a quadrant
  (ordering tie), non-.md relPath, Book singleton.

## Qualification

`qualification/consumer.ttl` is a deterministic worked example
(4 quadrants, 6 pages). Point a consumer `ggen.toml` at this pack by path.
