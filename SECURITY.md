# Security

Treat packs as executable manufacturing inputs: templates and gates influence files written by ggen consumers. Review pack source with the same care as build tooling.

Report vulnerabilities privately through GitHub's security-reporting surface when available rather than publishing exploit details in a public issue.

Marketplace acceptance is intentionally fail closed on symlinks under `packs/`, malformed manifests, duplicate identities, missing ontology/template source, and invalid gate extensions. Pull-request CI has `contents: read` only and must never push generated corrections.

A passing repository validator is structural evidence, not a sandbox guarantee. Consumers remain responsible for reviewing the outputs and authority boundaries appropriate to the environment in which a pack is used.
