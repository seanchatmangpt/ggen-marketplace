# v26.10.8 — Landing Batch 2 Receipt

Batch of six commits landed in `ggen-marketplace` under the v26.10.8 campaign:
L4/L5 ontology maturity doctrine plus closure of the wasmex-pack deprecation gap
(lifecycle registry, capability-index repoint, banners/links, lifecycle court),
and the campaign runbook seed with landing batch 1. Each row verified via
`git show --stat` / `git rev-parse` at receipt time (2026-10-08).

## Commits

| SHA (full) | Landing | Paths | Court result | Receipt |
|---|---|---|---|---|
| `92eb05bf7e3b14875f8484164fe3e23d77e37531` | L4/L5 ontology maturity mapping + ggen bridge doctrine | `docs/reference/ONTOLOGY-MATURITY-L4-L5.md` (+82, new) | docs-only; Diátaxis reference quadrant; no code surface | this row |
| `92233bdfdbafdb2fcba51a79576e3bb8414a4aad` | lifecycle: register wasi-json-abi-pack and beam-wasmex-host-pack as deprecated | `lifecycle.toml` (+14) | lifecycle court test 1 (`deprecated` state + successor) PASSED | this row |
| `d5c7ea045eb51ab9c38fb0badd0431ff56b9a785` | capability-closure: repoint wasm-abi capabilities to rust-wasi-wasmex-pack | `packs/capability-closure-pack/index/declared.ttl` (+9/−9) | lifecycle court test 3 (index repoint, no precursor names) PASSED | this row |
| `164843b689a6a8d98c96402c9ed7034ecf8acce9` | deprecation banners, repo-relative DEPRECATED.md links, book.ttl nav titles | `docs/book.ttl`, 4 docs pages (banners+links), `docs/rust-wasm-elixir/ADOPTION/bcinr.md`, 2 pack `DEPRECATED.md` (9 files, +25/−5) | lifecycle court test 2 (`DEPRECATED.md` present, successor named, no `file:///Users/sac`) PASSED | this row |
| `68c351ed08ef4da200d57a9039de7455d4646f79` | pack lifecycle court guarding the wasmex-pack deprecation | `tests/test_pack_lifecycle_court.py` (+51, new) | `python3 -m pytest tests/test_pack_lifecycle_court.py -q` → **3 passed**, exit 0 (real files, no mocks) | this row |
| `a02d45248c867e3f1cc9edb59936fb113cdd677e` | campaign runbook seed + landing batch 1 receipt | `docs/sjira/v26.10.8/_INTEGRATION_RUNBOOK.md`, `docs/sjira/v26.10.8/LANDING-BATCH-1.md` (+84, new) | docs-only; batch-1 court outputs recorded in LANDING-BATCH-1.md | `docs/sjira/v26.10.8/LANDING-BATCH-1.md` |

## Batch-wide court output (re-run at receipt time, 2026-10-08, subject = committed tree)

- **Lifecycle court**: `python3 -m pytest tests/test_pack_lifecycle_court.py -q`
  → `3 passed in 0.05s`, exit 0. Chicago-style: reads real `lifecycle.toml`,
  real `DEPRECATED.md` files, real `declared.ttl`; zero mocks.
- **Marketplace validate**: `python3 scripts/marketplace.py validate` →
  **exit 0**, `validated packs=306 manifests=306 ontologies=504
  templates=1837 native_gates=1868 verifier_gates=21
  profiles={project:101,projection:159,semantic:46} diataxis=20`.
- **Catalog determinism**: `marketplace.py catalog` twice + `cmp` →
  **IDENTICAL**, exit 0.
- **Validate/determinism caveat (disclosed)**: at the raw working tree these
  two courts currently exit 2 with `REFUSED:PACK_SYMLINK` — caused solely by
  the *untracked* `packs/semantic-fullstack-factory-pack/qualification/generated/`
  tree (node_modules symlinks from another lane's qualification run, present in
  no commit). With that untracked dir set aside (and restored after), both
  courts pass as recorded above. This is a pre-existing working-tree condition,
  not introduced by batch-2 commits.

## Open items (disclosed)

- `.tool-versions` still untracked in the checkout (uncommitted).
- `docs/sjira/v26.10.8/UNIFIED-WASM-PACK.md` pins receipts at `e987f3717`,
  which is unreachable from this history; pin receipts to follow.
- graphlaw `b7664a5e` claim was rejected as uncorroborated; pin re-derivation
  in flight.
