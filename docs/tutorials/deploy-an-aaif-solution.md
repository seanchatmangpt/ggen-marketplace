# Deploy an AAIF solution on kind

This tutorial walks the full AAIF commerce loop on your machine: paste a
profile, run intake, manufacture a solution, pay the simulated entitlement
gate, and produce a deployment plan against a local kind cluster.

Standing scope: everything in this tutorial runs on the simulated commerce
backend and the kind actuation rail. That rail is `PARTIAL_ALIVE`. Real GCP
Marketplace procurement and real GKE actuation are `BLOCKED` pending vendor
onboarding. Do not point this tutorial at a real billing authority.

## What you will build

A `solutions/<slug>/` directory holding a two-pack lock (the AAIF vanilla pack
plus the profile tailoring pack), a manufactured `dist/` tree, and a
paid-delivery receipt chain under `receipts/paid-delivery/`.

## Prerequisites

- Python 3.11+ (`profile_intake.py` refuses older interpreters).
- `ggen` on PATH (see `how-to/install-ggen.md`).
- Docker and `kind` for the actuation rail.
- A checkout of this repository at a known SHA.

## 1. Pick a slug and intake a profile

Intake normalizes profile-shaped input into JSON plus RDF with zero network
I/O:

```bash
python3 scripts/profile_intake.py profile.html \
  --out solutions/acme --lock
```

Outputs land in `solutions/acme/`: `profile.json` (normalized),
`profile.ttl` (vendored FOAF/Schema.org/Org vocabulary plus parallel
`aaif:Agent` individuals), and `profile.lock.json` (sha256 fingerprint over
both outputs).

Refusals are typed: `REFUSED_PROFILE_UNREADABLE`, `REFUSED_PROFILE_EMPTY`,
`REFUSED_PROFILE_NO_NAME` all exit 2. Fix the input and re-run.

## 2. Check the monetization registry

`solutions/<slug>` commerce configuration comes from `monetization.toml` at
the repository root. Read it once so later refusals make sense:

```bash
cat monetization.toml
```

The `[monetization]` block names the backend (`sim`), the billing authority,
the provider id, and the unit price. Exactly one billing authority is
required; the loader refuses cardinality violations.

## 3. Start the commerce simulator

The simulator is a stdlib HTTP server with no environment-variable
configuration:

```bash
python3 k8s/gcp-marketplace-sim/server.py &
curl -s http://localhost:8443/app/servicecontrol_discovery.json > /dev/null \
  && echo "sim up"
```

## 4. Seed an entitlement

Seed the simulator's approval store so the entitlement check returns active
for your entitlement id:

```bash
export AAIF_ENTITLEMENT_ID=ent-acme-001
# pass this id to the deployer with --entitlement-id ent-acme-001
```

Seeding is environment-specific; see `how-to/run-the-kind-commerce-rail.md`
for the concrete simulator seeding steps.

## 5. Deploy the solution

The deployer is the single ordered entry point. It runs the flow documented
in `reference/aaif-deployer-contract.md`:

```bash
python3 scripts/deploy_aaif_solution.py \
  --solution solutions/acme \
  --out solutions/acme/dist \
  --target kind
```

`--out` is the dist directory the deployer manufactures into; it must not
exist when the deployer starts (pay-before-manufacture). `--receipts-dir`
defaults to `<repo>/receipts`, `--config` defaults to `<repo>/monetization.toml`,
and `--entitlement-id` defaults to the solution slug (`acme` here); pass
`--entitlement-id ent-acme-001` to reuse the id you exported in step 4.
Add `--actuate` to print the kind `kubectl` sequence after the plan is
emitted; the deployer prints the sequence, it does not execute it.

On success the deployer prints a JSON summary with the receipt chain hash
and plan path. On refusal it prints a typed `REFUSED:<CODE>:<detail>`
string and exits with a nonzero code from the deployer contract's exit
table.

## 6. Inspect the receipts

```bash
python3 scripts/paid_delivery_receipt.py verify receipts
```

Verify walks the chain: each envelope folds `sha256(prev‖payload)` from the
64-zero genesis. A tampered line fails verification.

## 7. Read the plan

`actuation_plan.json` is byte-identical for `--target kind` and
`--target gke` on the same inputs. The target changes only the actuator, not
the plan bytes. For real GKE, actuation is `BLOCKED` (vendor onboarding);
the plan itself is still produced.

## Troubleshooting

| Symptom | Where to look |
| --- | --- |
| Exit 2 with `REFUSED:...` | Deployer contract refusal table |
| Simulator 403 `ENTITLEMENT_INACTIVE` | Seeding step, entitlement id |
| `REFUSED_BILLING_AUTHORITY_CARDINALITY` | `monetization.toml` authorities list |
| Plan differs between targets | Falsifier — file a defect; plans must be identical |

## Next steps

- `how-to/ingest-a-profile.md` — intake in depth.
- `how-to/run-the-kind-commerce-rail.md` — the simulator and mesh manifests.
- `reference/aaif-deployer-contract.md` — the exact contract.
- `explanation/aaif-commerce-seams.md` — why the seams are shaped this way.
