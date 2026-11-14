# GCP Terraform Pack Divergences

Standing: UNVERIFIED

Registered divergences between pack output and `/Users/sac/fnox/infra/gcp/iam/main.tf`, and
constructs the arcus gcp_emulator may reject with HCL_UNSUPPORTED. No arcus run was observed by
this lane; every row is UNVERIFIED until the coordinator runs the acceptance command.

| id | surface | divergence | status | close condition |
|---|---|---|---|---|
| D-01 | iam locals.apis | pack renders apis list from template input, not ontology | UNVERIFIED | add gtf:api facts |
| D-02 | iam locals.runtime_sas | block not emitted by resource template; carried in preamble add-on | UNVERIFIED | move to template |
| D-03 | iam comments | HCL comments (section banners, KMS rotation note) not emitted | REGISTERED | semantically neutral |
| D-04 | iap/edge/budget/cloudrun/gpu | inventory only (type+name); no body lines or template | PARTIAL | model bodies like iam |
| U-01 | backend "gcs" {} | arcus status UNVERIFIED | UNVERIFIED | arcus run |
| U-02 | for_each toset() | arcus status UNVERIFIED | UNVERIFIED | arcus run |
| U-03 | count conditional | arcus status UNVERIFIED | UNVERIFIED | arcus run |
| U-04 | lifecycle prevent_destroy | arcus status UNVERIFIED | UNVERIFIED | arcus run |
| U-05 | data sources | arcus status UNVERIFIED | UNVERIFIED | arcus run |
| U-06 | dynamic blocks | arcus status UNVERIFIED | UNVERIFIED | arcus run |

No `.terraform/` artifacts are shipped in this pack.
