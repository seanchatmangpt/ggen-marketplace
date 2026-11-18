# smalt-k8s-pack

Standing: UNKNOWN

ProfilePack (v0.1.0). Extends `kubernetes-workload-pack` with StatefulSet, headless/ClusterIP/
NodePort Services, Secret, ConfigMap, typed env/ports/mounts, and swarm hardening gates.

## Contents

- `ontology.ttl` — schema-only `k8s:` extension vocabulary (zero individuals).
- `gates/010_required.rq`, `030_antiaffinity_required.rq`, `040_headless_required.rq`,
  `050_dist_port_range.rq`, `060_network_policy.rq`, `070_cookie_secret.rq`.
- `templates/statefulset_and_services.yaml.tmpl`, `templates/network_policies.yaml.tmpl`.

Gate 020 (SEC-PRIV-001) is not duplicated; it lives in `kubernetes-workload-pack`.

## Dependency

`requires = ["urn:ggen:pack:kubernetes-workload-pack"]` (the pack exists in this repo at
`packs/kubernetes-workload-pack`). Not yet exercised: no real `ggen sync run` of this pack has
been run in this repository.

## Provenance

Source: `/Users/sac/smalt/packs/smalt-k8s-pack` (smalt lane BK-MKT1, v26.10.22), copied
verbatim. Licence: P28-SIL v2.1.0. The templates reference `priv/smalt-k8s.ttl`, the smalt
consumer's fact file, which is not shipped here.

## Open edges

- Not qualified in this repo (UNKNOWN); no replay/idempotency evidence.
- Gate 050 pins smalt-specific names (`smalt-backend-env`, erl-dist 9000..9009). Left as-is
  deliberately: parameterizing the ConfigMap name would require either matching any ConfigMap
  (loosens the refusal) or a typed fact naming the env ConfigMap (ontology change, not done).
- Fixed: the statefulset template's `containers` query no longer groups by the unselected,
  unbound `?volumeMountsBlock` (mounts render from the separate `mounts` query).
