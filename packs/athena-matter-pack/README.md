# athena-matter-pack

Athena security-control ontology pack. The security-control domain of
athena's private matter surface as RDF; TypeScript zod `.strict()` contract
modules (athena style) projected deterministically via `ggen sync`.

## Domain contracts

| Class | Contract | Fields |
|---|---|---|
| `am:AccessGrant` | J7 identity-admission contract | `principalId`, `roles`, `matterIds`, `expiresAt` (mandatory — a grant without expiry is refused) |
| `am:EncryptedRecord` | W2-2 sealed envelope | `scheme`, `keyVersion`, `wrappedDek`, `iv`, `ciphertext` |
| `am:RegionPin` | regional admission | `principalId`, `allowedRegions` (closed membership set) |
| `am:AuditEvent` | sentinel-audit hash chain | `actor`, `action`, `target`, `outcome`, `prevHash` |
| `am:CaseSpace` | per-case custody surface | `tenantId`, `firmId`, `caseId` (+ server-side `am:custodyBinding`) |

## Sync

From this directory:

```bash
ggen sync run
```

Outputs land in `generated/*.contract.ts` (five modules). Regenerate after
any `ontology.ttl` / `queries/` / `templates/` edit — do not hand-edit
`generated/`.

## Verify gates (zero-rows law)

`verify/*.unbound.rq` are inverted gates — each MUST return zero rows over
`ontology.ttl`; a row is a typed refusal:

- `field-orphan.unbound.rq` — a field bound to no declared class.
- `expiry-pairing.unbound.rq` — AccessGrant declared without `expiresAt`
  (J7 permanent-grant channel).
- `chain-pairing.unbound.rq` — AuditEvent declared without `prevHash`
  (unlinkable sentinel-audit chain).
- `custody-drift.unbound.rq` — CaseSpace fields without the
  `am:custodyBinding` annotation.

## Render proof

```bash
# in a scratch dir with zod resolvable (types from zod v3 work):
mkdir -p node_modules && \
  ln -s <path-to>/node_modules/.pnpm/zod@3*/node_modules/zod node_modules/zod
for f in generated/*.contract.ts; do
  tsc --noEmit --strict --target es2020 --moduleResolution bundler \
    --module esnext "$f" || exit 1
done
```

The render step is receipted by ggen (`.ggen-v2/receipt.json`); tsc (strict,
no emit) on the rendered output is the non-vacuity proof that the templates
produce valid TypeScript. Verify gates are checked with any SPARQL runner,
e.g. rdflib over `ontology.ttl`; each must return zero rows.
