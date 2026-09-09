# How to extend the factory

Add a candidate family by extending `ontology.ttl`, then add one ordered SELECT projection and one admission/refusal gate. Add a deterministic template only when the candidate has an emitted consequence. Add a verifier court that checks the exact new boundary.

Prefer existing pack composition before new templates. Preserve failed candidates as graph topology; do not delete them merely because one consumer or runtime rejects them.
