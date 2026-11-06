# supabase-pack qualification

Standing: PARTIAL

## Subject

`packs/supabase-pack` — pack.toml version 0.2.0 (on-disk head, 2026-11-05).
Ontology 76 triples; gates: `010_required.rq`, `020_client_runtime_enum.rq`,
`030_rls_requires_policy.rq`, `040_project_ref_shape.rq`.

## What was verified

Wave receipts (cmms v26.11.5):

- `L10.md` — pack binding resolved by `ggen sync run --dry-run` in a /tmp
  probe (exit 0, content hashes minted); planned writes witnessed for
  `lib/supabase/client.ts`, `lib/supabase/server.ts`, `.env.example`,
  `supabase/config.toml`, `supabase/migrations/*` — with the disclosed
  caveat that these render even with zero `sb:` facts in the graph.
  Standing there: PARTIAL (in-repo sync blocked by an in-flight module file,
  not by this pack). No full render+tsc court for supabase outputs witnessed
  in any receipt this wave.
- `L12.md` — consumer seam: `lib/repo/supabase.ts` compiles against the
  projected `@/lib/supabase/client` seam shape (assumed contract; PARTIAL
  standing there for the same reason).

Qualification lane re-run against the CURRENT 0.2.0 head (rdflib, 2026-11-05):

- `ontology.ttl` parse: OK, 76 triples.
- Gate baselines (rdflib SELECT): `010_required.rq` rows=0;
  `020_client_runtime_enum.rq` rows=0; `030_rls_requires_policy.rq` rows=0;
  `040_project_ref_shape.rq` rows=0. All exit-clean.
- Anti-vacuity flip (in-memory mutation, no pack file modified): added
  `sb:Table` with `sb:hasRLS true` and no `sb:hasPolicy` → `030` returned
  1 violation row. First flip attempt used invented vocabulary
  (`urn:supabase-pack:` prefix + `sb:requiresPolicy`) and returned 0 rows —
  that attempt proves nothing about the gate; the second attempt with the
  gate's real vocabulary (`https://ggen.dev/packs/supabase#hasRLS`) fired.

## Standing basis

PARTIAL: gates are ALIVE this session (baseline clean, flip witnessed), but
no end-to-end consumer render of this pack's outputs at the current head has
been receipted — L10's probe covers binding resolution and planned writes
only, and disclosed that templates render from empty bindings.
