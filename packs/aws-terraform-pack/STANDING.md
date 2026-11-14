# AWS/Terraform Pack Standing

Standing: UNVERIFIED

Mirrors packs/azure-terraform-pack layout (pack.toml, ontology.ttl, templates/, gates/).

## Authored (files exist, not executed)

- ontology.ttl: awtf: vocabulary plus one illustrative instance (fnox-runner ECS Fargate task).
- gates/010,020,030 *.rq: fail-closed SELECT gates (enums, cardinality, closed shape, orphans).
- templates/: main, providers, variables, outputs rendered per awtf:TaskGroup to deploy/aws/<slug>/.

## Not done

- No `ggen sync run`, `ggen receipt verify`, `terraform validate` or `terraform test` observed.
- No tftest.hcl or PDDL files ported from the azure pack.
- Not a claim about arcus aws parity cells (KD-AW7/8/9/12) or serverless-run.

## Acceptance command (coordinator)

In a scratch consumer with ggen.toml pinning this pack: `ggen sync run` twice, compare sha256 of
deploy/aws/fnox-runner/*.tf, then `ggen receipt verify`. Falsifier: change awtf:taskCpu and the
.tf must change.
