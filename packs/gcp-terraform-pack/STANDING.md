# gcp-terraform-pack Standing

Standing: PARTIAL_ALIVE (`mod_iam` verified; `mod_iap`/`mod_edge`/`mod_budget`/`mod_cloudrun`/`mod_gpu` inventory-only)

- `ggen.toml` + frontmatter SPARQL bindings in `templates/*.tera` emit `infra/gcp/iam/{preamble,main,variables}.tf`.
- `gtf:hclLine` (`gtf:lineOrder` + `gtf:text`) orders all `mod_iam` resource body lines deterministically.
- `gates/010_iam_resources.rq` validates module/type/name across all modules plus `order`/`hclLine` for `mod_iam`.
- `gates/020_unsupported_hcl.rq` refuses `UNVERIFIED` or missing `gtf:arcusStatus`; constructs are reconciled against `arcus` `sdlc.ParseLenient`.
- `terraform init -backend=false && terraform validate -no-color && terraform fmt -check -recursive` pass on `infra/gcp/iam`.
