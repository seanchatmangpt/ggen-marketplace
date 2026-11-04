# ZD-132: ggen-marketplace v26.11.3 wave-closing seal

Seal lane for the v26.11.3 wave. Mirror of cgap's ZD-105 seal shape
(`/Users/sac/cgap/docs/jira/v26.11.3/closure/cgap-closure.md`). Own
actuation: exactly two files —
`docs/jira/v26.11.3/closure/marketplace-closure.md` (the seal) and this
receipt. All standing words re-read from cited receipt bodies on disk.

## Subject

`/Users/sac/ggen-marketplace` main @
`7364405a048ae64da3039c4bdbf8cfbf9c224ae6`, origin/main verified equal
(`git fetch && git rev-parse HEAD origin/main`) at seal time.

## Deliverables sealed (pointers — full bodies in the closure doc)

- Baseline 313→347 reconcile (zd-12 / `0e94adbb8`) — ALIVE.
- MKT-01 ambient ggen 26.11.3 adoption with disclosed
  `--skip-ea-admission` opt-out (zd-62 / `55925b64b`) — ALIVE.
- Corpus 347/347 qualified, zero REFUSED, final counts {ALIVE 337,
  WARN 9, SKIPPED 1} (zd-20 `d451e63e4`, zd-49 `b408361c1`,
  zd-65 `9d042c2cf`, zd-28 `808c621c4`) — ALIVE.
- WARN typing: 9 ratchet-residue / 1 real-signal / 1 skipped harness
  limitation (zd-52 / `74397a441`) — ALIVE.
- Cross-pack gate families (zd-28: ash-extension-core 020,
  pptx-presentation 010/020/030, strategic-doctrine 050,
  clap-noun-verb requires-closure; zd-65: smalt-semconv, smalt-substrate,
  ash-pplan-chaos) — ALIVE, per-gate flip witnesses, no court relaxed.
- Pack-lock scope note: ratchet baseline is corpus-wide (347 packs), not
  scoped to `marketplace.active.toml`'s 20-pack `[active]` set;
  `ggen.lock` is the root-manifest sync lock; no per-pack lock artifact.

## Carried, not claimed

- No v26.11.3 tag minted.
- `qualification/baseline.json:ggen_version` reads `"ggen 26.10.11"`:
  zd-28's final pinned-court re-projection mechanically overwrote zd-65's
  `"ggen 26.11.3"` stamp; ambient court identity is 26.11.3 (disclosed in
  zd-28's receipt; next ambient re-projection restamps mechanically).

## This seal's own commands / exits

Run this session, marketplace @ `7364405a0`, ambient `ggen 26.11.3`
(`/Users/sac/.local/bin/ggen`):

- `python3 scripts/qualify_packs.py --workers 3 --pack a2a-conformance-pack
  --pack typer-azure-pack --pack clap-noun-verb-crate-pack --report
  /tmp/seal_sample.json` → exit 0, `qualified packs=3
  profiles={"project":1,"projection":2,"semantic":0} ggen="ggen 26.11.3"
  timeout_seconds=5`.
- `python3 scripts/warn_ratchet.py check /tmp/seal_sample.json --subset`
  → exit 0, `ratchet ok counts={"ALIVE": 2, "REFUSED": 0, "SKIPPED": 0,
  "WARN": 1}`.
- `jq -e . qualification/baseline.json` → valid; `jq -c .counts` →
  `{ALIVE:337, REFUSED:0, SKIPPED:1, WARN:9}`.
- `ls docs/jira/v26.11.3/receipts | wc -l` → 12 pre-seal (14 after this
  commit lands two files).
- `git rev-parse HEAD origin/main` → equal pre-commit; re-verified after
  push.

## Standing

ALIVE for the seal itself (commands above, exits witnessed this session
against the exact subject). Corpus standing carried by the cited lane
receipts; not re-graded here.

## Falsifier

Any command above re-run now exiting non-zero, the landed counts
disagreeing with `jq -c .counts`, or origin/main ≠ the subject SHA
refutes this receipt.
