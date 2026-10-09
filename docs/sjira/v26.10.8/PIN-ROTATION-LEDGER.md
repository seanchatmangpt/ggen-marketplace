# PIN-ROTATION-LEDGER — fleet extractor pin rotation, v26.10.8

Lane R43, 2026-10-09.

## Lineage

- OLD pin: `4c862576ab63595f9cd0417b35341af3ec1001f49450e79bf2e4c291a4a4246f`
  (`ggen-marketplace/scripts/gen_doc_surface.py`; BLAKE3 receipt identity
  `a579e2109941e1f27f2faf0403d6c91e3eebb7f234dcc191a814573001309616`)
- NEW pin: `f51d81ac4f7e4119dff950327237effee4968f4aa9aba52c7d62c5362f441fa9`
  (fn-depth edit, R34) @ ggen-marketplace `b99942bdb`; verified by R49.
- Era: 4c862576ab pinned during the v26.10.8 doc-hdit campaign certify runs
  (2026-10-09) → superseded by f51d81ac via R34 on the same date.

## Sweep scope

`docs/sjira/v26.10.8/` in 19 campaign repos (xaas, ash_surface, ggen,
affidavit, bcinr, ex4pm, beam4pm, wasm4pm, ash_pplan, ash_graphlaw,
zcode-cli, ferroplan, castle, gymact, autofde-lab, graphlaw, ash_a2a,
frozen-duckdb, ggen-marketplace), including `.jsonl` chain files and meta
fields. Hit count: **6 hits in 6 repos** (13 repos clean; zcode's TS
receipt pins the TS extractor `691cb91a` — separate file, unchanged).

## Disposition table

| repo | file | disposition | note / R-item |
|---|---|---|---|
| ash_surface | `/Users/sac/ash_surface/docs/sjira/v26.10.8/doc-hdit-certify-meta.json:3-4` | historical (ACCEPTED certify meta at its subject) | note added: `extractor_pin_sha256` retained as historical subject identity; `_note` field = superseded-by f51d81ac as-of 2026-10-09 (R34) |
| bcinr | `/Users/sac/bcinr/docs/sjira/v26.10.8/DOC-HDIT-CERTIFY-RECEIPT.md:10` | historical (REFUSED:DOC_HDIT_CERTIFY — no receipt minted, no live-standing claim) | note added after pin line: superseded-by f51d81ac as-of 2026-10-09 (R34) |
| ex4pm | `/Users/sac/ex4pm/docs/sjira/v26.10.8/CERTIFY-VERIFY.md:198` | historical (REFUSED:DOC_HDIT_CERTIFY_GATE_FAIL re-certify at `e4963ba`; pin recorded as working-tree bytes) | note added: superseded-by f51d81ac as-of 2026-10-09 (R34) |
| ash_graphlaw | `/Users/sac/ash_graphlaw/docs/sjira/v26.10.8/CERTIFY-VERIFY.md:6` | historical (ACCEPTED certify at subject `66877414b`) | note added: superseded-by f51d81ac as-of 2026-10-09 (R34) |
| castle | `/Users/sac/castle/docs/sjira/v26.10.8/CAMPAIGN-RECEIPT.md:24` | historical (ACCEPTED doc-hdit CERTIFY row, subject `076744f23`, gmp @ `2cf02b276`) | note added: superseded-by f51d81ac as-of 2026-10-09 (R34) |
| frozen-duckdb | `/Users/sac/frozen-duckdb/docs/sjira/v26.10.8/DOC-HDIT-CERTIFY-RECEIPT.md:10` | historical (ACCEPTED certify at `c7e53c352`, Andon-Yellow ceiling carried) | note added: superseded-by f51d81ac as-of 2026-10-09 (R34) |

## R-items (receipts claiming live standing on the stale pin)

None. Every old-pin hit is a pinned historical receipt bound to its
certified subject; no receipt in the sweep claims CURRENT/live-pin
standing on `4c862576ab`. R-items minted: **0**.

## Gate check

- Every old-pin hit dispositioned: 6/6.
- No live-standing receipt left on the stale pin: confirmed (0 R-items).
- Ledger carries real file paths + line evidence: yes (table above).
