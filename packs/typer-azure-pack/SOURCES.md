# Sources: vendored bicep-types-az excerpt

`sources/vendor/bicep-types/storage.json` — minimal frozen excerpt of the
Microsoft bicep-types-az type index for **one** resource type:
`Microsoft.Storage/storageAccounts@2022-09-01`.

- Upstream: `/Users/sac/bicep-types-az` (microsoft/bicep-types-az),
  `generated/storage_0/microsoft.storage/2022-09-01/types.json`
- Upstream commit at vendor time: `03f72b6d1309458d28f4369d382d701e638b904f` (2026-10-21)
- Extraction: the `ResourceType` node plus the transitive `$ref` closure of its
  body (535 → 180 type nodes, `$ref` indices remapped consistently within the
  frozen manifest). The manifest is a single self-contained JSON document —
  **frozen-manifest law: the excerpt is one manifest with internally
  consistent `#/N` indices, consumers concatenate/read it whole; no consumer
  imports type nodes from a second manifest.**

Regenerate (from this pack root):

```bash
python3 sources/vendor_extract.py
```
