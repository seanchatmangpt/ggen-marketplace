# TAG-STANDING — v26.10.8 Final Tag Audit (backlog [115])

Date: 2026-10-08. Decision rule: advance the tag to `v26.10.8-2` (annotated) only
where the round-5 receipt (0bf1be372) or sealed round-5 records clearly supersede
the tagged state and cite main HEAD in-repo. All three repos met the gate; no tag
was rewritten — `v26.10.8-2` is a new annotated tag, `v26.10.8` left untouched.

| repo | old tag (`v26.10.8`) | new tag (`v26.10.8-2`) | receipts cited |
|---|---|---|---|
| ggen-marketplace | 2ad88900b73708ddff6250bc64fe34e481fdc953 | 0bf1be372e4caf479ca3a7d00d1765500bf254b4 (advanced) | Round-5 receipt refresh `0bf1be372` (backlog [113]) itself at main HEAD; `docs/sjira/v26.10.8/SEMANTIC-WAVE-RECEIPT.md` (round-5); sealed ADMISSION-LEDGER sj-records under `docs/sjira/v26.10.8/seal/` |
| xaas | 86752b3bd0d2f36ae5405ce08a7e0be3affea240 | 8bb4a2f5c251289ddad00c1fb43464f73c583516 (advanced) | Sealed `docs/sjira/v26.10.8/seal/XAAS-26108-1..5.sj-record.json` (ggen-marketplace) binding `subject_sha` 8bb4a2f5, `admit:ACCEPT`, standing ALIVE; replay `python3 scripts/admit_workgraphs.py` exit 0 |
| ash_surface | 061b1e9a6dfc83f3a3fdb0899cec898111ce9a3a | dc214d7b5bea46e160afcb247e1af09d96525c27 (advanced) | `SEMANTIC-WAVE-RECEIPT.md` M5 (repaired `620aa939` re-verified, Phi 0.0 both extractors); `DOCS-DOD-GATE.md` code-doc parity PASS; `dc214d7b5` verified tree-identical to receipted `620aa939` (`git diff 620aa939 dc214d7b5` empty) |

## Post-tag hardening landed between `v26.10.8` and `v26.10.8-2`

### ggen-marketplace (2ad88900b..0bf1be372, 137 commits, 226 files)
Highlights; full list `git log v26.10.8..v26.10.8-2`.

- `0bf1be372` docs(sjira): round-5 receipt refresh (post-merge witnesses) — the audit subject itself
- `b04003b07` feat(extractor): env-var and string-key surface items
- `99abb416b` fix(seal): castle repo labels + retired-record handling
- `66eaea182` feat(doc-surface): .doc-surface.toml generated-surface policy (backlog [107]/[64])
- `961fa54d5` fix(ci): fortune5 battery count guard 75 -> 96
- `c69894c3a` fix(rollout): carry known_external + content-hash cache key
- `c21deecfc` fix(trust-plane-pack): ED25519/ES256K KAT arms + goldens (backlog [82])
- `6c2e0a41a` fix(sjira): row-unique ids for null-order castle-goal seal rows (backlog [81])
- `723a5ef91` feat(extractor): path-claim typing against path surface
- `bdcb8af7b` merge: lane-f5-shapes-wire union (v26.10.8 hardening union)
- doc-hdit campaign: VSA core `97abea822`, scaffold verb `0141c1a6c`, certify verb `20aadd175`,
  fleet rollout `714663087`, content-hash cache `a53442fb7`, P0-P3 filters/fixes
- fortune5 EA pack: generator `8b1092086`, SHACL wire `2248a32d8`, 10-sbb shape `182dd9e3a`,
  conformance vectors `994ebfaa8`, qualification ladder `80bb076ba`
- fleet workgraph/sjira: deterministic generator `27256497d`, admission driver `7b3146788`,
  SHACL validator `f6bb82dfb`, git-trust-root court `ad2ad844d`, seal runbook `ccbf58273`

### xaas (86752b3b..8bb4a2f5, 12 commits, 485 files)
- `8bb4a2f5` docs: repair stale references (audit phantom classes 1-5) — sealed as XAAS-26108-1..5
- `ce498713` docs(reference): XaasWeb.Router route table (generated)
- `975095e1` docs(sjira): v26.10.8 workgraph (archive canonical shape)
- `1c5be2e8` fix(warnings): quiet --warnings-as-errors compile gate
- `599ad105` docs(archive): superseded campaign records -> docs/archive/ (git mv)
- `572c6f4e` docs(changelog): mark v26.10.8 released
- `c6060c5b` test(docs): nav-coverage court (diataxis README <-> disk)
- `53512b84` docs(archive): relocate stale cleanup-plan.json
- `af2b7730` docs(diataxis): graphlaw WASM seam how-to + playwright harness reference
- `5a6c64dc` docs: verify/sync zcode->xaas c4 integration doc
- `819c116f` docs: cross-reference ash_pplan surface
- `d5dd780a` chore(release): sync version carriers to 26.10.8 (post-tag fix-forward)

### ash_surface (061b1e9a6..dc214d7b5, 15 commits, 140 files)
- `dc214d7b5` merge docs/phantom-repair-26108: docs-only phantom symbol repair
- `620aa9392` docs: repair stale symbol references (audit phantom class) — receipted repair
- `555cc1ba9` docs: merge doc-hdit scaffolds round 1 into main
- `dc93530f2` docs: doc-hdit scaffolds for uncovered modules
- `6bfd91d68` fix(sjira): full 40-hex baseSha on WO-ASHSURF-26108-2
- `57c0100f0` fix(agent-card): v1.0 member-contract compliance
- `68d763b24` docs(sjira): v26.10.8 round-2 admission candidates (JSONL)
- `c6010f8c1` docs(sjira): v26.10.8 campaign workgraph
- `8bc9b7509` feat(a2a): persist serialized agent card (regenerable)
- `68f77041b` test(courts): withheld court battery + burn-in fixtures
- `3dc4e8618` docs: withheld court battery + quarantine protocol
- `1b0921875` docs: cross-reference a2a bridge surface
- `6ffe41be6` docs: archive 26.9.x jira dirs
- `008f0d775` docs(diataxis): README nav index + bidirectional nav-coverage court

## Verification

- All three `v26.10.8-2` tags created annotated (`git tag -v` shows tag object + correct commit), pushed to origin 2026-10-08.
- Original `v26.10.8` tags unchanged and untouched.
- Gate held: no tag advanced without in-repo receipts binding the new target SHA
  (gmp: round-5 receipt at that SHA; xaas: sealed sj-records binding subject_sha;
  ash_surface: receipted repair SHA + verified tree identity with HEAD).
