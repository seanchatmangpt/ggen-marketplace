# CS2 canonical pack

Pinned marketplace projection for RFC-CS2-001.

Canonical producer is seanchatmangpt/chatman-ecosystem at commit f3d215e9a4fc6fe17ca4e396cf78254d847cbdd7, file cs2/canonical.ttl, blob fdcdbfc00205d9e7d367a64adfee2bbe65f31dd6.

The copied canonical.ttl is a projection, not a new semantic owner. Consumers must preserve the producer commit, exact subject RFC-CS2-001, provenance requirement, replay requirement, and authority ceiling CONSTRUCT.

Falsifier: a downstream consumer can replace this projection with a local surrogate carrying different subject semantics while still claiming RFC-CS2-001.

Retirement rule: local CS2 fixture semantics are not authoritative. Reuse this pinned projection or refuse the claim.
