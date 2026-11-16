# AWS/Terraform Pack Standing

Standing: PARTIAL_ALIVE (`ggen sync run` + `terraform validate` + `terraform fmt -check` verified; `arcus` runtime parity out-of-scope for ECS/Logs/IAM)

Mirrors `packs/azure-terraform-pack` layout (`pack.toml`, `ontology.ttl`, `templates/`, `gates/`).

## Verified

- `ontology.ttl`: `awtf:` vocabulary plus one illustrative instance (`fnox-runner` ECS Fargate task).
- `gates/010,020,030 *.rq`: fail-closed SELECT gates (enums, cardinality, closed shape, orphans).
- `templates/`: `main`, `providers`, `variables`, `outputs` rendered per `awtf:TaskGroup` to `deploy/aws/<slug>/`.
- `providers.tf.tmpl`: documents `arcus` endpoint configuration and notes that ECS Fargate / CloudWatch Logs / IAM are outside `arcus`'s current AWS emulator surface (`S3`, `SQS`, `DynamoDB`, `Kinesis`).

## Not done

- No `tftest.hcl` or PDDL files ported from the azure pack.
- Not a claim about `arcus` aws parity cells (`KD-AW7/8/9/12`) or `serverless-run`.
