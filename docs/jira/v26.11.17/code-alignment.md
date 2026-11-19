# code-alignment — ggen-marketplace v26.11.17

Standing: PASS

## Identity
- Path: `/Users/sac/ggen-marketplace`
- Branch at generation: main
- HEAD: 1cf20b3f7bb215da97d2d3f6372038b8c992aa7c
- Tracked files: 19206
- Tracked docs markdown: 350

## Build manifests (tracked at the commit above)
- `pyproject.toml`
- `ggen.toml`
- `.tool-versions`
- `CLAUDE.md`
- `AGENTS.md`
- `README.md`

## Top-level layout (tracked file counts)
- `.`: 36
- `.agents`: 9
- `.claude`: 4
- `.claude-plugin`: 1
- `.ggen`: 3
- `.github`: 33
- `.qme`: 1
- `.qualify-scratch`: 3
- `archive`: 57
- `ci`: 97
- `dd-ui`: 1
- `docs`: 486
- `domains`: 5
- `ecosystem`: 1
- `evidence`: 1
- `examples`: 21
- `k8s`: 9
- `notes`: 2
- `ontologies`: 866
- `packages`: 57
- `packaging`: 3
- `packs`: 17013
- `patterns`: 8
- `projections`: 11
- `qualification`: 1
- `receipts`: 202
- `scaffolds`: 11
- `scripts`: 89
- `semantic`: 1
- `solutions`: 7
- `source-audits`: 2
- `spec`: 3
- `src`: 18
- `templates`: 1
- `tests`: 139
- `tools`: 4

## Prior doc waves
- `docs/jira/v26.11.14`
- `docs/jira/v26.11.15`
- `docs/jira/v26.11.16`

## Falsifiers
- Any tracked path above absent at HEAD, or a count differing from `git ls-files`.
- HEAD sha not equal to or an ancestor of the live HEAD.

## Acceptance
```bash
python3 ~/zcode-cli/scripts/docs_v261117.py validate /Users/sac/ggen-marketplace
```
Expected: exit 0 and `PASS`.

## See Also
- `~/zcode-cli/scripts/docs_v261117.py`
