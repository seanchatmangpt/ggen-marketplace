# AAIF commerce seams

Why the AAIF commerce loop is built around two seams, and why the standing
fence is drawn where it is.

## The entitlement seam

Commerce configuration lives in one root registry, `monetization.toml`.
Moving from the simulated commerce backend to a real one is a registry edit:

```toml
[monetization]
backend = "sim"     # -> "real"
```

One line, no pack restructure. The simulator
(`k8s/gcp-marketplace-sim/server.py`) already serves entitlement metadata at
the exact real Google discovery paths and minted-JWT claims shape, so the
client contract does not change when the backend does. What does change with
`backend = "real"`: OAuth2 bearer auth via ADC, real provider id, JWKS
rotation, a Pub/Sub push endpoint, and persistent state.

Real rail standing is `BLOCKED` (vendor onboarding). The seam refuses
`REFUSED_ENTITLEMENT_REAL_NOT_PERMITTED` rather than simulating success. The
flip is an external onboarding act plus a registry line — never a code
change smuggled past the gate.

## The actuation seam

`deploy_aaif_solution.py --target kind|gke` produces byte-identical
`actuation_plan.json` for the same inputs. The target selects the actuator,
not the plan. kind maps host 8080 to NodePort 30080 and 8443 to 30443; a GKE
cluster needs only a different exposure story, and the manifests are
namespaced with no cluster-scoped objects beyond the Namespaces themselves.
Consequence: the plan you qualified locally is the plan you actuate
elsewhere, and any target-induced difference in plan bytes is a defect, not
a portability feature.

## The standing fence

Three standings exist and must never be conflated:

1. **Marketplace standing** — the catalog/qualification standing of the
   packs involved, computed by the marketplace's own courts. It says the
   pack manufactures correctly, nothing about billing.
2. **Manufacture standing** — the standing of a paid delivery run up through
   the consequence digest: entitlement admitted, gates passed, dist
   produced. Governed by the deployer's refusal ladder.
3. **Actuation standing** — the standing of applying the plan to a real
   cluster. Kind actuation on the local rail is `PARTIAL_ALIVE`. Real GKE
   actuation is `BLOCKED` pending vendor onboarding; until a real actuation
   receipt exists, that standing is `BLOCKED`, not unknown-by-omission.

A pack with `ALIVE` marketplace standing does not grant actuation
authority, and a successful simulated entitlement does not make real
procurement alive. Each standing is earned by its own courts on its own
subject.

## Why the fence sits there

The authority fence (`explanation/security-and-authority.md`) says documents
and generated artifacts carry no DO authority. The commerce seams apply that
to billing: registry lines and plan bytes are intents; only an admitted
entitlement check followed by a receipted, replayable delivery is
consequence. Blocking at the seam — rather than faking the real backend —
is what keeps `PARTIAL_ALIVE` honest and makes the eventual real-rail flip a
one-line, receipted transition.

## See also

- `reference/aaif-deployer-contract.md`
- `how-to/run-the-kind-commerce-rail.md`
- `explanation/security-and-authority.md`
