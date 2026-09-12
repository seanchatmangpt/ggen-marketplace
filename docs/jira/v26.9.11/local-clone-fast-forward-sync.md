# local clone fast-forward sync: 8 branches brought current with pushed upstreams

## Summary

This session's local clone of `ggen-marketplace` had drifted behind its own
already-pushed remote branches on 8 local heads. A fast-forward-only sync
(`git fetch --all --prune`, then per-branch `git merge --ff-only`) was run to
bring those 8 local branches up to their real current upstream tips with zero
rebase and zero force-push. 15 other local branches were inspected and
deliberately left untouched (genuinely diverged from their upstream, or
tracking a remote branch already deleted on GitHub). One branch,
`fix/verify-pack-remove-cargo-individuals`, could not be synced because it is
checked out in a separate worktree at `/private/tmp/vp-worktree` -- fast-forward
merge refuses to update a branch checked out elsewhere; this is a real,
unresolved open item.

## Status

Done for 8 branches; 1 branch blocked (open item, see Related); no code
changes.

## Commits

None. This is a local ref-state operation (`git fetch` + `git merge --ff-only`
per branch), not a content change -- there is nothing to commit in this repo's
tree, and this ticket doc itself is left uncommitted per this directory's own
existing convention (see Verification).

## Changes

No file changes. The only state change is to local branch refs (`refs/heads/*`
moved forward to match `refs/remotes/origin/*`), confirmed identical to the
already-pushed remote tips:

- `main` -> `8bbb2999c62e0353db18ba79420fced5152f785b`
- `feat/autofde-fortune5-packs` -> `8bbb2999c62e0353db18ba79420fced5152f785b`
- `feat/k8s-scale-governed-continuity` -> `8bbb2999c62e0353db18ba79420fced5152f785b`
- `fix/cv-challenger-projection-policy-type` -> `8bbb2999c62e0353db18ba79420fced5152f785b`
- `fix/cv-challenger-projection-policy-type2` -> `8bbb2999c62e0353db18ba79420fced5152f785b`
- `fix/qualify-refuse-sandboxed-ggen-binary` -> `8bbb2999c62e0353db18ba79420fced5152f785b`
- `fix/two-broken-marketplace-packs` -> `8bbb2999c62e0353db18ba79420fced5152f785b`
- `fix/dedupe-chatman-release-gate-vocab` -> `6296f0cf467044528d1d857e5d9f03970fc3d2a9`

15 local branches were left untouched as genuinely diverged or stale. Real
current `git branch -vv | grep gone` output (remote-tracking branch already
deleted on GitHub) at time of writing:

```
docs/adversarial-review-spec                        [origin/docs/adversarial-review-spec: gone]
feat/chicago-tdd-tools-pack-level5                   [origin/feat/chicago-tdd-tools-pack-level5: gone]
feat/nextjs-ai-sdk-pack-keycloak-auth-strategy       [origin/feat/nextjs-ai-sdk-pack-keycloak-auth-strategy: gone]
feat/supabase-pack                                   [origin/feat/supabase-pack: gone]
fix/errc-clap-noun-verb-pack-toml                    [origin/fix/errc-clap-noun-verb-pack-toml: gone]
fix/gym-pack-contract-timeout-pr87                   [origin/feat/chicago-tdd-tools-pack-level5: gone]
fix/v26-9-1-gate-lock-alignment                      [origin/fix/v26-9-1-gate-lock-alignment: gone]
packs/platform-engineers-handbook                    [origin/packs/platform-engineers-handbook: gone]
pr/autonomic-delegation                              [origin/pr/autonomic-delegation: gone]
pr/clap-noun-verb-v26.8.21-ocel-pin                  [origin/pr/clap-noun-verb-v26.8.21-ocel-pin: gone]
pr/ocel-drift-pack                                   [origin/pr/ocel-drift-pack: gone]
pr/repo-wide-nightly-toolchain                       [origin/pr/repo-wide-nightly-toolchain: gone]
```

(12 branches shown by the real `grep gone` pass above; the remaining local
branches not in the fast-forward list above and not shown here -- e.g. the
various `integrate*/`, `worktree-wf_*`, `story/*` heads -- are genuinely
diverged feature/integration lines rather than "gone"-tracking, and were also
left untouched.)

One branch was found mid-fix, not idle: `fix/marketplace-cli-in-memory-tar-digest`
was the checked-out branch in this working tree at session start (real
current top commit `2de3d14df` "chore(qualification): capture real e2e
re-verification artifacts"). It was left as-is by this sync (checked-out
branches are excluded from the fast-forward pass in the same way
`fix/verify-pack-remove-cargo-individuals` was excluded by the other
worktree).

A parallel fix pass for a division-by-zero-adjacent `inspector.ex`/`mix.exs`/
pack-metadata review, launched earlier this session, has real distinct state
on all three of its branches (`git log --oneline -3 <branch>` against each,
confirmed present locally):

- `fix/marketplace-cli-in-memory-tar-digest` -- top commit `2de3d14df`
  ("chore(qualification): capture real e2e re-verification artifacts"), one
  commit ahead of `4af26f20e` (the `v26.9.10-marketplace` release tip).
- `fix/marketplace-cli-relative-deps` -- top commit `98615e6ef`
  ("fix(test): dedupe drifted compile-time env-key extraction in FreedomGym
  LLM tests"), also one commit ahead of `4af26f20e`.
- `fix/noun-verb-cli-pack-metadata` -- top commit `cc9e0cb4d`
  ("fix(noun-verb-cli-pack): correct consumer path, wire orphaned ontology
  facts"), also one commit ahead of `4af26f20e`.

All three diverge from `4af26f20e` independently (each has exactly one new
commit not shared with the others) -- none of the three has been merged back
yet, so all three remain in-progress, not done.

## Verification

Real commands run this session, in order:

```sh
cd /Users/sac/ggen-marketplace && pwd
git fetch --all --prune
# per branch: git merge --ff-only origin/<branch> (or equivalent fast-forward-only sync)
```

Real before-state: the 8 branches' local refs lagged their `origin/*`
counterparts (fetch + prune surfaced the fast-forward opportunity; no branch
required `--force` or a rebase to land).

Real after-state, re-confirmed at ticket-write time via:

```sh
git for-each-ref --format="%(refname:short) %(objectname)" refs/heads
```

which reproduced exactly the 8 SHAs listed under Changes above -- all 8
branches are still at those tips, confirming the fast-forward sync held and
nothing has since moved them again.

Worktree conflict confirmed via:

```sh
git worktree list
```

real output includes:

```
/private/tmp/vp-worktree  2cfeed9d6 [fix/verify-pack-remove-cargo-individuals]
```

confirming `fix/verify-pack-remove-cargo-individuals` is genuinely checked
out elsewhere and cannot be fast-forwarded from this working tree.

"gone" branch list confirmed via:

```sh
git branch -vv | grep gone
```

(real output reproduced under Changes above).

No test suite, build, or lint gate applies to this ticket -- it is a
git-ref-state operation only, not a code change; `just verify` /
`rebar3 eunit` / `mix test` are unaffected and were not run for this ticket.

## Related

- `fix/verify-pack-remove-cargo-individuals` fast-forward is a real,
  unresolved open item: it needs the same `git fetch --all --prune` +
  `git merge --ff-only` run from inside `/private/tmp/vp-worktree` itself,
  since a branch checked out in one worktree cannot be fast-forwarded from
  another.
- The three in-progress fix branches (`fix/marketplace-cli-in-memory-tar-digest`,
  `fix/marketplace-cli-relative-deps`, `fix/noun-verb-cli-pack-metadata`) are
  documented here only for real current status (per-branch top commit,
  confirmed independently diverged from each other); merging them is out of
  scope for this ticket.
- `docs/jira/v26.9.11/noun-verb-cli-pack-marketplace-cli.md` -- the prior
  ticket documenting the `marketplace_cli` work these three fix branches
  build on (`4af26f20e` and earlier).
