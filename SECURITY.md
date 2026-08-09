# Security

Treat packs as executable or execution-adjacent manufacturing inputs: templates, rules, queries, gates, and project configuration can influence files or decisions produced by ggen consumers. Review pack source with the same care as build tooling.

Report vulnerabilities privately through GitHub's security-reporting surface when available rather than publishing exploit details in a public issue.

Marketplace acceptance is intentionally fail closed on symlinks under `packs/`, malformed manifests, duplicate identities, missing RDF authority, unsupported visible template or gate source forms, invalid SemVer identity, and incomplete required Diátaxis documentation. Templates are required only for packs that actually claim a projection surface; semantic packs are not made safer by inventing empty template directories.

Pull-request CI has `contents: read` only and must never push generated corrections. The historical one-shot import actuator was removed after exact-source migration and its reappearance is an explicit CI falsifier.

A passing repository validator is structural/catalog evidence, not a sandbox guarantee and not proof that a pack's verifier program is safe to execute. Consumers remain responsible for inspecting selected pack source, using the matching ggen runtime, validating manufactured outputs, and enforcing the authority boundary appropriate to the environment in which a pack is used.
