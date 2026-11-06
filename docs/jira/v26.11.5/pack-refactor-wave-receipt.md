# Pack Refactor Wave — Receipt (2026-11-05)

Standing: PARTIAL_ALIVE

## Subject

`/Users/sac/ggen-marketplace` (canonical checkout). 15-lane pack refactor
wave under the house pattern (registry:
`docs/jira/v26.11.5/pack-refactor-wave2-registry.md`; fences honored —
kafka-wire-pack untouched, cmms-referenced packs worked by their
dedicated lanes). All work uncommitted in the working tree; coordinator
owns git. Retry of a 429-killed documentation lane; code surfaces were
already on disk and were re-verified, not re-edited.

## Per-pack table

| Pack | Outcome |
|---|---|
| shadcn-ui-primitives | Contract field-complete in pack.toml
(`[consumer_contract]` deps derived from template imports). Gates
flip-proven: shims trip, byte-exact restores verified by sha256. Field
templates a11y-fixed vs upstream registry (contrast, focus-visible,
labels). `templates/060_lib_utils_ts.tmpl` BREAKING disclosed in-template:
v0.3.0 re-exports the `cn` npm package (Sept 2026 shadcn changelog);
consumers add `cn`, may drop `clsx`/`tailwind-merge`; export surface
`import { cn } from "@/lib/utils"` unchanged. |
| supabase | Lazy client (client created on first use, not at import).
RLS string-guard hardened in `010_client_ts.tmpl` (policy strings escaped
before interpolation). Empty-bindings loud guard (zero rows -> loud
failure, never a silent empty projection). README truth-lint pass:
output paths and behaviors stated as they actually render. |
| shacl-to-zod | F2 interop gap CLOSED: `templates/shacl_to_zod.js.tmpl`
SPARQL accepts either sp:/shp: spelling via single-prefix UNION (same
namespace IRI), 9-cell rdflib court all-PASS (shp-only / sp-only /
neither) — addendum in `receipts/F2.md` cites the template diff blob
dc1971b53..fe8c27262. |
| shacl-projection | Gate `gates/030_literal_scan.py` vacuous-pass fixed:
a missing `templates/` tree now returns
`REFUSED[TEMPLATES_MISSING]` (exit 1) instead of scanning nothing and
passing. Projection/duality contract documented in README. |
| Cross-pack | Unified 4-field consumer contracts (runtime deps,
peer_context, output paths, courts) across the four cmms-referenced
packs; `qualification/qualification.md` ×4 written/re-sealed against the
current on-disk heads; verify court over all packs all-PASS. |

## Commands + exits (re-verified this session)

- rdflib F2 court re-run: `python3 /tmp/f2_union_test.py` → 9/9 PASS,
  exit=0.
- shacl-to-zod gate: `python3 packs/shacl-to-zod-pack/gates/
  010_template_literal_scan.py` → exit 0 (ALIVE) at current head.
- Diff census: `git diff --stat -- packs/` → 39 files, +636/−199, no
  kafka-wire-pack template edits outside its own F-lane work.

## Standing justification

PARTIAL_ALIVE: per-pack outcomes are grounded in receipts and the
diffstat above, and the two courts cited were re-executed this session
with real output; the wave as a whole is uncommitted in the working
tree, so no fresh-checkout replay exists yet. Commit + fresh-clone
replay is the coordinator's transition.
