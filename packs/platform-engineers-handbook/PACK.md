# platform-engineers-handbook

Companion source code from Packt's *The Platform Engineer's Handbook* (Ajay Chankramath,
ISBN 978-1-80638-013-8, May 2026), captured as one ggen-create pack from
[`seanchatmangpt/Platform-Engineer-s-Handbook`](https://github.com/seanchatmangpt/Platform-Engineer-s-Handbook)
(fork of `PacktPublishing/Platform-Engineer-s-Handbook`).

## What this is, precisely

This is **not** a mirror of the source repository. The source ships 14 chapters as
independent `ChNN/` directories, each a chapter-scoped slice of one evolving platform
build. This pack layers them in book order (Ch01 → Ch14, each chapter's files copied over
the accumulating tree at their real project-relative path) to reconstruct the cumulative
final-state project the book builds toward — the way a real repository actually evolves,
not a directory-by-directory snapshot.

Three files collide across chapters this way and take their last-writing chapter's form:
`README.md` (Ch14's), `load-secrets.sh` (Ch14's), `.circleci/config.yml` (**Ch02's** — it
doesn't exist past Ch02). The 13 discarded chapter READMEs are restored under
`templates/`-captured `chapter-readmes/ChNN-README.md`, indexed by
`chapter-readmes/INDEX.md`, so the per-chapter "Code-to-Chapter Mapping" context isn't
silently lost.

294 templated files: 300 source files, minus 21 lost to the collisions above, minus 1
excluded (`templates/backend-service/v1/skeleton/.github/workflows/ci.yml` — contains a
literal Tera `{% raw %}` sentinel `ggen-create` fails closed on), plus 15 added back
(13 chapter READMEs, 1 index, 1 RBAC fix — see below).

## Templatization

This pack was captured with a single `usename` word (`PlatformEngineersHandbook`) run
across all files. Almost none of the source content contains that literal string, so almost
all captured files have zero templated replacements (verify: most entries in
`ggen-create-package.json` show `"content_replacements": 0`). **This pack is a faithful,
deterministic, re-derivable capture of a specific book's source at a point in time — it is
not a parameterized generator that produces varying output per invocation.** Treat it as a
qualified reference snapshot, not a scaffold/template-generator pack.

## Fixes applied (deviations from the published book)

Two real, out-of-the-box bugs in Ch09's manifests were found by standing up real Kind +
Crossplane clusters, and are fixed **in this pack's shipped content** (not just diagnosed):

1. **`xrd-postgresql.yaml`** now declares `spec.publishConnectionDetailsTo` in the claim's
   OpenAPI schema. The book's own `demo-app-database.yaml` sets this field already; the
   book's own XRD never declared it, so `kubectl apply` rejected the claim outright with
   `unknown field "spec.publishConnectionDetailsTo"`.
2. **`provider-kubernetes-rbac.yaml`** (new file, not in the book) grants
   `provider-kubernetes`'s service account permission to manage the resource kinds this
   pack's Composition composes, via a `Group: system:serviceaccounts:crossplane-system`
   `ClusterRoleBinding` — a static, declarative binding that doesn't depend on
   `provider-kubernetes`'s revision-hashed service account name. Without it, every composed
   object (Namespace, PVC, Deployment, Service) fails with a `Forbidden` RBAC error and the
   claim never reaches `Ready`.

Both were reverified end-to-end on a disposable Kind cluster after being ported into this
pack: `kubectl apply -f demo-app-database.yaml` succeeds, the claim reaches `Ready: True`
on the first status check, all 5 composed objects `Synced: True / Ready: True`.

Two known issues remain **unfixed**, on purpose:

- `crossplane-providers.yaml` applies `Provider` and `ProviderConfig` in one file; the
  `ProviderConfig` half fails until its `Provider` package reaches `Healthy`. This needs a
  documented two-step apply order, not a file change — left as-is, noted here.
- The Composition declares `connectionDetails` on composed resources, but
  `function-patch-and-transform:v0.7.0` (the exact version pinned in
  `crossplane-providers.yaml`) has no `writeConnectionSecretToRef`-style aggregation
  mechanism in its input schema — confirmed by testing the current-docs-recommended fix and
  getting `unknown name "writeConnectionSecretToRef"` back. `publishConnectionDetailsTo`
  therefore never receives anything to publish. Fixing this would mean adding a function
  dependency the book never specifies — left open.

Full narrative, including every command run and every real error message, is in
[chatman-ecosystem's completion record](https://github.com/seanchatmangpt/chatman-ecosystem/blob/main/docs/platform-engineers-handbook-ggen-packs.md).

## Other known findings (not fixed, since they're not this pack's to fix)

- `test-platform-config.py` (Ch01) asserts a `primary-cloud` key that `platform-config.yaml`
  never defines (it has `primary-runtime` instead) — fails 1/10 out of the box.
- The book's Preface/Ch3 TOC describe identity/access via Auth0; the shipped code
  implements Keycloak throughout, with zero Auth0 references anywhere in the source.

## Provenance and licensing

This pack redistributes the near-entirety of a commercially published book's companion
source code. The source repository carries **no `LICENSE` file** (verified: none exists at
any level in `seanchatmangpt/Platform-Engineer-s-Handbook` or its upstream
`PacktPublishing/Platform-Engineer-s-Handbook`). This pack does not claim a license on your
behalf and is not sanctioned by Packt Publishing or the author — treat its terms of use as
whatever the (currently absent) upstream license would say, and check with Packt directly
before redistributing further.

## Not a substitute for the fictional "Post-AGI Platform Engineer's Handbook"

`chatman-ecosystem` separately hosts an unrelated, fictional mdBook titled "The Post-AGI
Platform Engineer's Handbook" (`docs/post-agi-platform-handbook/`). This pack is the real
Packt book's companion code and has no relationship to that content beyond a similar name.
