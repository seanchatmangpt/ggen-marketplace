# MP-RPV gate evidence

Lane MP-RPV (wave MP, GC-26.9.23 release closure; CE23-3, CE23-9, PRD/ARD section 28).
Subject: `66df30ac6cbdcb67f08d25f5c785dfc937535027` on branch `mp23/MP-RPV`
(base `420bc91e7c1e291be73ab749b7e443252bc7bab8` = GitHub origin/main). Every log below was
produced by a run on that committed subject; `head.txt` is `git rev-parse HEAD` taken before the
runs. Tools: ggen 26.9.18 (`/Users/sac/.local/bin/ggen`), Python 3.14.3, git.

| file | produced by | result |
|---|---|---|
| `lane-gate.sh`, `lane-gate.66df30a.log` | `bash lane-gate.sh` (the lane gate from the task, verbatim) | exit 0 |
| `runner.66df30a.log` | `python3 generated/qualification_runner.py --repo-map seanchatmangpt/xaas=/Users/sac/wt/v26922/fri/xaas-int` | exit 0, 78 passed, 0 failed, 0 skipped |
| `run-gates.66df30a.log` | `python3 bin/run-gates.py ontology.ttl` (pack dir) | exit 0, gates 01/02/04/05 pass |
| `gatemut.py`, `gatemut.66df30a.log` | `python3 gatemut.py <pack>` (five one-edit ontology mutants through `bin/run-gates.py`) | each refused (gate 01, 02, 04, 05 x2) |
| `mutation_matrix.py`, `mutation_matrix.66df30a.log` | `python3 mutation_matrix.py <pack> <scratch> lane-gate.sh` | 15 of 16 mutants killed; M16 (fault guard) survives |
| `m0-gate.sh`, `m0.66df30a.log` | the lane gate over the base (420bc91) pack with this lane's fixtures | exit 1 (DIVERGE on GC23-0.json): revert mutation killed |
| `native.sh`, `native-consumer.*`, `native.66df30a.log` | `bash native.sh <pack> <this dir>`: `ggen sync run` in a consumer with `[packs] rpv = { path = "pk" }` | good exit 0 with byte-identical outputs; gate-05 mutant exit 1 `FM-PACK-013` |
| `parity.sh`, `parity.66df30a.tsv` | `bash parity.sh` (pack dir): unified default profile vs `validate_receipt.py` vs durable profile on 34 receipts + 29 fixtures | 63/63 same exit; durable refuses all 63 |
| `legacy.py`, `legacy.66df30a.log` | `python3 legacy.py <worktree>`: old (420bc91) vs new generated validator on the five earlier contracts | 78/78 same exit |
| `fuzz/`, `fuzz.sh`, `fuzz.66df30a.bash.log` | `bash fuzz.sh <validator>` in a copy of `fuzz/` (non-object sections, NUL bytes, option-like paths, non-JSON, bad UTF-8; `deep.json` regenerated) | 32/32 runs without a traceback; durable half exit 1 on 14 JSON inputs, exit 2 on the 2 non-JSON inputs |
| `fuzz.66df30a.log` | the first fuzz run, superseded | kept for conservation: its loop ran under zsh, where the unquoted `$args` is not word-split, so its 16 durable runs measured a usage error (exit 2) instead of the durable profile; the no-traceback result holds in both |
| `marketplace-validate.66df30a.log` | `python3 scripts/marketplace.py validate && catalog > a && catalog > b && cmp a b && fingerprint` (worktree root) | exit 0 (325 packs); catalog deterministic; fingerprint exit 0 |
| `pytest-compare.sh`, `pytest-compare.66df30a.log`, `pytest.66df30a.log`, `pytest-base-420bc91.log` | `bash pytest-compare.sh <worktree> 420bc91e7c1e291be73ab749b7e443252bc7bab8 <scratch>`: full suite at the head, the failing tests again on a `git archive` of the base | 320 passed, 3 failed at the subject; the same 3 fail at the base (pre-existing: docs book navigation, corpus-wide tokenizer bound 1235 > 950, beam4pm-pro-entitlement-pack) -- this pack parses to 919 statements with 0 skipped |
| `build_fixtures.py` | builder of `packs/receipt-provenance-unification-pack/qualification/fixtures/**` | derivations in the pack's `qualification/README.md` |

`lane-gate.sh`, `mutation_matrix.py` and `m0-gate.sh` are the exact files that produced their logs. `gatemut.py`, `parity.sh`, `legacy.py` and `native.sh` were written after their first (inline) runs, then run from the committed file; each reproduced its earlier log byte for byte (`cmp`). `fuzz.sh` did not: it produced `fuzz.66df30a.bash.log`, which supersedes `fuzz.66df30a.log`.

Known limits recorded here, not hidden:

- The lane gate's durable `neg-*` loop runs `test ... && grep ... && ! grep ...` under `set -e`,
  which binds only the last iteration; mutants M8, M9, M10, M11 and M13 pass the lane gate and are
  killed only by `qualification_runner.py`, which checks every fixture independently.
- M16 (the validator's catch-all fault guard narrowed to `ZeroDivisionError`) survives: no known
  input faults the validator, so the guard has no witnessed firing. The traceback falsifier is
  witnessed by the fuzz inputs and every negative fixture instead.
- Under `--require-durable`, none of the 34 current xaas/ggen_igniter v26.9.23 receipts is
  admitted: they name relative-path durable locations (no repository, no commit). Adoption needs
  receipts with `git:` or `git-notes:` locations (CE23-3 out-of-subject seal).
