# AuthZEN + SPIFFE absorption pack

This pack manufactures adapters and qualification material for the composition:

`SPIFFE attested workload -> AuthZEN policy evidence -> SA2A PreparedEffect -> local C2 certificate authority -> independent actuator`.

It does not generate an authorization service, signing key, or protected effector.

Inherited machinery:
- exact portable PreparedEffect identity;
- principal preservation and confused-deputy guards;
- policy/revocation epochs and generation fencing;
- ActuationCertificate verification;
- actuator-local claim/completion;
- receipts and replay.

Donor negative knowledge retained:
- PDP and PEP remain separate;
- PDP identity is bound to metadata to prevent mix-up;
- unknown AuthZEN metadata remains extension-compatible;
- search pagination preserves the initial request;
- SPIFFE trust-domain identity is cryptographic evidence, not authority;
- federation is authentication reach, not delegation;
- JWT-SVID compatibility carries replay risk and is opt-in for protected PDP binding.
