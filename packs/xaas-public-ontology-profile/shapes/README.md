# shapes/ — SHACL qualification, reserved

Per the profile architecture: `profile.ttl`'s composition must pass logical-consistency and
SHACL-conformance checks before any downstream `ggen` projection trusts it. **Not yet built:**

- `profile.shacl.ttl` — validates `xaas:Profile` itself (real `prof:isProfileOf` targets, no
  dangling references).
- `capability.shacl.ttl` — once `queries/competency/` identifies which public terms (or gap-earned
  native terms) model capability, shapes constraining that model.
- `service.shacl.ttl` — same, for service/offering semantics.
- `authority.shacl.ttl` — same, for the CQ09 execution-authority question, which `profile.ttl`
  explicitly does not consider solved by `odrl:Permission` alone.

No SHACL validation has been run this session — `ggen graph validate` against this pack has not
been executed. This directory is a reserved slot, not a completed qualification pass.
