# GIT-TRUST-COURT — v26.10.8 fleet workgraph SHA resolution

Motivated successor to `WORKGRAPH-SHACL-REPORT.md`: SHACL shape constraints cannot
catch a pseudo-SHA; git can. This court resolves every 40-hex SHA citation in the
fleet `WORKGRAPH.ttl` files against the owning repo's git object store and against
the repo's pushed default branch (the trust root).

## Method

- Extractor: citation-scoped — `sj:baseSha`, `sj:landedCommit`, `sj:subjectSha`,
  `prov:wasDerivedFrom`, `rdfs:seeAlso`, plus vendored gitlinks
  (`vendor/<name> <sha>`) inside `sj:acceptance` prose. Bare 40-hex strings in
  `dcterms:description` prose are not citations and are excluded.
- Resolution: `git -C <owning-repo> cat-file -t <sha>` in the local checkout of the
  owning repo (from `sj:repository`, or the repo named in the commit IRI, or the
  vendor path).
- Trust root: `git merge-base --is-ancestor <sha> origin/<default>` where default is
  `refs/remotes/origin/HEAD`.
- Verdicts: `RESOLVED-ROOTED` / `RESOLVED-UNROOTED` / `UNRESOLVED` (pseudo-SHA).

## Run

```
python3 scripts/git_trust_court.py \
  --file ~/ash_a2a/docs/sjira/v26.10.8/WORKGRAPH.ttl \
  --file ~/ash_affidavit/docs/sjira/v26.10.8/WORKGRAPH.ttl \
  --file ~/ash_pplan/docs/sjira/v26.10.8-1/WORKGRAPH.ttl \
  --file ~/ash_r2rml/docs/sjira/v26.10.8/WORKGRAPH.ttl \
  --file ~/ash_surface/docs/sjira/v26.10.8/WORKGRAPH.ttl \
  --file ~/beam4pm/docs/sjira/v26.10.8/WORKGRAPH.ttl \
  --file ~/ex4pm/docs/sjira/v26.10.8/WORKGRAPH.ttl \
  --file ~/ggen-ecosystem/docs/sjira/v26.10.8/WORKGRAPH.ttl \
  --file ~/ggen-marketplace/docs/sjira/v26.10.8/WORKGRAPH.ttl \
  --file ~/xaas/docs/sjira/v26.10.8/WORKGRAPH.ttl \
  --file ~/zcode-cli/docs/sjira/v26.10.8/WORKGRAPH.ttl
```

Machine verdict: `COURT VERDICT: 41 RESOLVED-ROOTED, 13 RESOLVED-UNROOTED,
0 UNRESOLVED across 11 workgraphs`. Full JSON evidence was emitted with `--json`
at run time (per-SHA verdicts with owning repo, line number, context).

Note: 11 workgraphs carry the v26.10.8 campaign shape on disk (ash_pplan is
`v26.10.8-1`); no 12th current workgraph exists — `ggen` and `ferroplan` have none.

## Per-repo verdicts

| workgraph | trust root | citations | ROOTED | UNROOTED | UNRESOLVED |
|---|---|---|---|---|---|
| ash_a2a | (n/a) | 0 | 0 | 0 | 0 |
| ash_affidavit | origin/main | 5 | 5 | 0 | 0 |
| ash_pplan (v26.10.8-1) | origin/main | 5 | 5 | 0 | 0 |
| ash_r2rml | origin/dev | 6 | 0 | 6 | 0 |
| ash_surface | origin/main | 6 | 6 | 0 | 0 |
| beam4pm | (n/a) | 0 | 0 | 0 | 0 |
| ex4pm | (n/a) | 0 | 0 | 0 | 0 |
| ggen-ecosystem | origin/main | 7 | 7 | 0 | 0 |
| ggen-marketplace | origin/main | 11 | 11 | 0 | 0 |
| xaas | origin/main | 7 | 7 | 0 | 0 |
| zcode-cli | origin/main | 7 | 0 | 7 | 0 |
| **total** | | **54** | **41** | **13** | **0** |

Workgraphs with 0 citations (ash_a2a, beam4pm, ex4pm) cite only short (7–9 hex)
SHAs inside `prov:wasDerivedFrom` commit IRIs; 40-hex literals are out of their
authoring style.

## UNRESOLVED (pseudo-SHA defects)

None. Every 40-hex citation resolves to a real git object in its owning repo.
No TTL fixes required under the link-sweep law.

## RESOLVED-UNROOTED (13) — real commits, not yet merged to default branch

These are not pseudo-SHAs and not defects in SHA spelling: each object exists and
is pushed, but is not an ancestor of the owning repo's default branch. They are
v26.10.8 campaign lane heads pending merge.

### ash_r2rml (6, default `origin/dev`)

| sha | predicate | on branch |
|---|---|---|
| c25938cdca… | sj:baseSha (L27) | origin/docs/doc-hdit-scaffold |
| 3ed1cd609b… | sj:landedCommit (L28) | origin/docs/doc-hdit-scaffold, origin/fix/v26.9.29-from-source-head |
| 0cb5eb3dc1… | sj:landedCommit (L47) | origin/docs/doc-hdit-scaffold, origin/fix/v26.9.29-from-source-head |
| 11da8e6dc7… | sj:landedCommit (L67) | origin/docs/doc-hdit-scaffold, origin/fix/v26.9.29-from-source-head |
| ce947d4651… | sj:landedCommit (L87) | origin/docs/doc-hdit-scaffold |
| b1d2a9fc28… | sj:landedCommit (L87) | origin/docs/doc-hdit-scaffold |

### zcode-cli (7, default `origin/main`)

| sha | predicate | on branch |
|---|---|---|
| 89265187b3… | sj:baseSha (L156) | origin/docs/doc-hdit-ts-scaffold, origin/fix/v26926-preview-publish-typed-skip |
| daaec82ee2… | sj:subjectSha (L157) | origin/docs/doc-hdit-ts-scaffold, origin/fix/v26926-preview-publish-typed-skip |
| aa0d359ed5… | sj:baseSha (L202) | origin/docs/doc-hdit-ts-scaffold, origin/fix/v26926-preview-publish-typed-skip |
| e416d731fd… | sj:subjectSha (L203) | origin/docs/doc-hdit-ts-scaffold, origin/fix/v26926-preview-publish-typed-skip |
| 23c479aaea… | sj:subjectSha (L249) | origin/docs/doc-hdit-ts-scaffold, origin/fix/v26926-preview-publish-typed-skip |
| 8cb1d4c881… | sj:subjectSha (L292) | origin/docs/doc-hdit-ts-scaffold, origin/fix/v26926-preview-publish-typed-skip |
| 542d223829… | sj:subjectSha (L335) | origin/docs/doc-hdit-ts-scaffold, origin/fix/v26926-preview-publish-typed-skip |

Standing of those citations at their default-branch head is UNKNOWN until the
`docs/doc-hdit-*` scaffold branches merge — exact-head ALIVE requires the cited
SHA to be reachable from the trust root.

## Court hardening note

The first run had a real defect in the court itself: `default_branch` invoked git
without `-C`, resolving every repo's default branch against the invoking repo
(origin/main of ggen-marketplace), which mis-read ash_r2rml (origin/dev) and
autofde-lab (origin/master) and produced false UNROOTED verdicts. Fixed
(`git -C <repo>` in both default-branch probes) and the fleet run above is the
corrected rerun.

## Receipt

- Subject: `scripts/git_trust_court.py` + this report, on `hdit-v2-structs`
  (ggen-marketplace).
- Verdict: 41 RESOLVED-ROOTED / 13 RESOLVED-UNROOTED / 0 UNRESOLVED over 11
  workgraphs, 54 citations.
- Falsifier: any 40-hex citation that `cat-file` cannot resolve in its owning
  repo (currently zero), or an UNROOTED citation claimed as exact-head ALIVE.

## See Also

- `docs/sjira/v26.10.8/WORKGRAPH-SHACL-REPORT.md`
- `docs/sjira/v26.10.8/WORKGRAPH.ttl`
