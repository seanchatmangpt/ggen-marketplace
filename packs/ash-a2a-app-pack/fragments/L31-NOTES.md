# L31 Notes: strict prod profile

Standing: UNVERIFIED

## Seam edits for the coordinator (config.exs.tmpl)

1. Add at the end of config.exs.tmpl (after the profile block):
   `if config_env() == :prod, do: import_config("prod.exs")`
   Needed because compile_env reads :security_profile from compile-time config only
   (ash_a2a lib/ash_a2a/security_profile.ex:10-16, :22-24).
2. In the final `{% if a.security_profile ... %}` block, when the project declares
   `aap:profile "strict"`, do not emit the prod `:legacy_compat`; the dev/test guard
   `config_env() in [:dev, :test]` already excludes prod, so no change is required there.
3. Both L31 templates write fixed paths: `config/prod.exs` and `config/runtime.exs`. If another
   lane owns runtime.exs, merge L31_runtime_prod.exs.tmpl's `if config_env() == :prod` block into it.
4. Register gate gates/L31_010_strict_requires_durable.rq and ontology.d/L31-profile.ttl in the
   pack manifest.

## Evidence (ash_a2a)

- security_profile/boot.ex:119-149: strict refuses missing/short (<32) outbox key, non-durable
  outbox dir, Memory receipt store, non-strict capability_release_mode, missing broker/kill switch.
- boot.ex:96-112: env keys read: receipt_outbox_key, receipt_outbox_dir, claim_store,
  claim_store_dir, receipt_store, capability_release_mode, authority_broker, kill_switch_class.
- Not emitted: :claim_store module (not in vocabulary) and authority_policy; strict may
  refuse for them at boot (boot.ex:150+ not read). Extend L31 if the boot court reports them.
