# Qualification evidence

This pack has no SPARQL-driven gates (see PACK.md — it's a captured reference snapshot,
not a parameterized generator), so `qualification/consumer.ttl`-style synthetic gate
satisfaction doesn't apply. The evidence below is what was actually run against real
infrastructure, standing in for that role.

## `ggen-create verify`

```sh
ggen-create verify --output <dir> --ggen-bin "$(which ggen)" --set PlatformEngHandbook
```

Real `ggen 26.8.8` `sync run`, twice (reconstruction + variation), both exit `0`, both write
all 294 files. Checkpoints P1–P6 `ALIVE`. (P0/P7 sit at `UNEXECUTED`/`PARTIAL_ALIVE` — no
`--reference-dir` exists to diff against; not a failure.)

## `scripts/qualify_packs.py`

```sh
python3 scripts/qualify_packs.py --ggen "$(which ggen)" --report qualify-report.json
```

Loads the pack through `ggen` twice in an isolated filesystem-only capsule, requires
convergence to the same consequence hash. `status: ALIVE`.

## Real Kind + Crossplane cluster runs (not filesystem-only)

Six disposable Kind clusters were stood up and torn down across this pack's development to
verify Ch09's infrastructure-provisioning chapter against real Crossplane 2.3.4, real
`provider-kubernetes`, and real `kubectl`:

- Cluster 1–2: found bugs 1–3 (Provider/ProviderConfig apply-ordering, XRD schema gap,
  missing RBAC).
- Cluster 3: verified the RBAC fix via an (later-superseded) imperative
  `kubectl create clusterrolebinding` approach.
- Cluster 4: found bug 4 (missing connection-details aggregation), tried and falsified a
  speculative fix.
- Cluster 5: verified bugs 2–3's shipped fixes (declarative `Group`-based RBAC binding +
  XRD schema) end-to-end — `PostgreSQLClaim` reaches `Ready: True` on the first status
  check, all 5 composed objects `Synced: True / Ready: True`.
- Cluster 6: verified all three shipped fixes together, including bug 1's split
  `crossplane-providers.yaml`/`crossplane-provider-configs.yaml` two-step apply — zero
  errors on either apply, claim reaches `Ready: True` on the first status check.

13 of 14 chapters additionally had at least one of the book's own test suites (`pytest` or
`unittest`) run for real against this pack's content — see
[chatman-ecosystem's completion record](https://github.com/seanchatmangpt/chatman-ecosystem/blob/main/docs/platform-engineers-handbook-ggen-packs.md)
for every command and every real result.
