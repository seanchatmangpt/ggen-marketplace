# Parity Receipts Index

Standing: UNVERIFIED

One row per matrix PASS cell of `/Users/sac/fnox/docs/HYPERSCALER_PARITY.md`. Court:
`python3 /Users/sac/ggen-marketplace/scripts/check_parity_receipts.py`. A cell is pass only
when its row here points at an existing receipt JSON with standing PASS; registered
divergences (KD rows) are read from the matrix; PASS-UNRECEIPTED, MISSING and FAIL cells are
reported MISSING.

| repo | cloud | service | receipt |
|---|---|---|---|
| smalt | gcp | storage | `/Users/sac/fnox/receipts/parity/smalt-gcp-storage.json` |
| smalt | aws | storage | `/Users/sac/fnox/receipts/parity/smalt-aws-storage.json` |
| smalt | aws | document-db | `/Users/sac/fnox/receipts/parity/smalt-aws-document-db.json` |
| smalt | aws | secrets-kms | `/Users/sac/fnox/receipts/parity/smalt-aws-secrets-kms.json` |
| arcus | gcp | storage | `/Users/sac/fnox/receipts/parity/arcus-gcp-storage.json` |
| arcus | aws | queue-pubsub | `/Users/sac/fnox/receipts/parity/arcus-aws-queue-pubsub.json` |
| arcus | gcp | secrets-kms | `/Users/sac/fnox/receipts/parity/arcus-gcp-secrets-kms.json` |
| arcus | gcp | identity-iam | `/Users/sac/fnox/receipts/parity/arcus-gcp-identity-iam.json` |
| arcus | azure | secrets-kms | `/Users/sac/fnox/receipts/parity/arcus-azure-secrets-kms.json` |

## See Also

- `/Users/sac/ggen-marketplace/receipts/aws-parity-2026-11-14.md`
