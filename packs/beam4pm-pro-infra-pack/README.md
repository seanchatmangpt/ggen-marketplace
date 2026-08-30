# beam4pm-pro-infra-pack

Projects an admitted `b4pi:` deployment-infrastructure graph into real, locally-validated
Terraform (GCP Cloud Run) and Packer (GCE custom image) definitions for `beam4pm_pro` —
schema-only pack, ships zero individuals; a consuming project (e.g. `beam4pm`) supplies its
own `b4pi:Deployment` and `b4pi:PackerImage` instance data against the vocabulary declared
here.

## Standing ceiling

Everything this pack renders is validated locally only: `terraform validate` / `tofu
validate` on the rendered Cloud Run module, `packer validate` on the rendered image
template — both without credentials, without `plan`/`apply`/`build`. Real GCP Marketplace
listing, purchase, and entitlement remain `BLOCKED` on external authorities regardless of
anything in this pack. See `docs/jira/v26.8.29/19-marketplace-substrate-gcp.md` and
`marketplace/gcp/listing/README.md` in the `beam4pm` repo for the honest per-gate mapping
(MP0–MP9).

## What it generates

- `templates/cloudrun_main_tf.tmpl`, `cloudrun_variables_tf.tmpl`, `cloudrun_outputs_tf.tmpl`,
  `cloudrun_readme.tmpl` → `infra/gcp/cloudrun/{main,variables,outputs}.tf` + `README.md`: a
  `google_cloud_run_v2_service` module driven by a `b4pi:Deployment` individual's facts
  (serviceName/region/containerImage/cpuLimit/memoryLimit/minInstances/maxInstances/port/
  allowUnauthenticated), rebuilt from two real reference modules (`erlmcp`'s
  `marketplace/gcp/terraform/modules/cloud-run` and `tai-erlang-autonomics`'s
  `gcp/cloud-run.tf`) onto the v2 Cloud Run resource family. Graph facts land as variable
  *defaults*, so an operator can override any of them at plan time without hand-editing a
  generated file. Exactly one `b4pi:Deployment` per consumer graph is projected (first row
  after `ORDER BY`).
- `templates/packer-beam4pm-image.pkr.hcl.tmpl`, `packer-variables.pkr.hcl.tmpl`,
  `packer-readme.md.tmpl` → `infra/gcp/packer/{beam4pm-image,variables}.pkr.hcl` +
  `README.md`: a `googlecompute` Packer template building a Debian-based GCE image with
  Docker installed, the beam4pm container pre-pulled, and a systemd unit running it —
  adapted from `erlmcp/marketplace/gcp/packer/*.pkr.hcl` and `xaas/packer/aws-docker.pkr.hcl`.
  Driven by a `b4pi:PackerImage` individual (imageName/imageFamily/zone/machineType/
  containerImage, etc.); exactly one per consumer graph is projected.

## Vocabulary

Two classes, deliberately namespace-disjoint so a straight ontology concatenation cannot
collide: `b4pi:Deployment` (Cloud Run side, `gates/010_required.rq` refuses any instance
missing one of its nine required properties) and `b4pi:PackerImage` (Packer side). Both are
schema-only in this pack's own `ontology.ttl`; see `beam4pm`'s own ontology fragment for a
real working consumer instance of each.

## Composing this pack

Add `b4pi:Deployment` / `b4pi:PackerImage` instance data to the consuming project's own
`ontology.ttl`, reference this pack by path from that project's `ggen.toml` `[packs]` table,
and run `ggen sync run`. See `beam4pm`'s `ontology.ttl` and `ggen.toml` for a real, working
example consumer.
