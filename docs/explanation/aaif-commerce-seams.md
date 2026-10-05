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

## Why the seams fail closed

Every default in the commerce loop is the refusing one. That is not defensive
UX; each closed default is a law about who holds authority.

**Entitlement before manufacture.** Pay-before-manufacture is an
order-of-operations law, not a UX choice. If the gate ran after dist
production, a delivery would already exist when the entitlement check fails —
and the refusal would be an apology, not a fence. Running `decide()` first
means unpaid demand manufactures nothing, so there is never an artifact that
must be clawed back. A refused order leaves no consequence to undo.

**Loopback pinning.** The sim is a simulator, not an authority. Pinning
`AAIF_ENTITLEMENT_ENDPOINT` overrides to loopback keeps the trust boundary
explicit: an entitlement answer is only as trustworthy as the endpoint it
came from, and localhost is where you control both sides. The
`AAIF_ENTITLEMENT_ALLOW_REMOTE=1` escape is deliberate — pointing the gate at
a remote endpoint should be a decision someone records, never a default
anyone inherits.

**Tamper-evident, not tamper-proof.** The paid-delivery chain fold is
unkeyed: anyone who can rewrite `chain.jsonl` can rewrite the hashes too. The
honest claim is exactly that — evidence, not proof. The `HEAD` anchor plus an
out-of-band comparison at grant time detects rewriting; asymmetric
certification (a publisher/oracle signature over the head) is the optional
affidavit seam, deferred rather than faked.

**Forged priors fail against the whole chain.** A receipt is only as good as
the chain it sits in. Verify re-walks every link — payload hash, prev
pointer, fold, per-slug file — so a forged prior breaks not just its own
envelope but every descendant's `prev_chain_hash_hex`. There is no way to
inject a receipt that verifies in isolation; consistency is global or
refused.

## See also

- `reference/aaif-deployer-contract.md`
- `how-to/run-the-kind-commerce-rail.md`
- `explanation/security-and-authority.md`
