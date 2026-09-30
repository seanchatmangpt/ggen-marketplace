# SPIFFE capability donor

Projection target: workload identity adapter, not authority provider.

Donated semantics:
- trust-domain-qualified SPIFFE ID
- X.509/JWT SVID verification
- rotating trust bundles
- local Workload API credential delivery
- federation between explicitly trusted domains

Generated projections MUST preserve these separations:
- authentication != policy decision
- policy decision != actuation authority
- federation != delegation
- resource allocation != authority
- identity selection != principal substitution

Manufactured implementations must project the authenticated SPIFFE ID into the canonical principal/evidence envelope and then use the existing SA2A authority, actuator, receipt, replay and court surfaces.

Required negative fixtures:
wrong_trust_domain_bundle, valid_identity_without_certificate, principal_substitution, stale_bundle, jwt_replay, federation_as_authority, default_identity_confusion, duplicate_trust_domain_quorum.

Source horizon: SPIFFE latest specification family observed 2026-09-29. Runtime package/version selection is a separate admission step.
