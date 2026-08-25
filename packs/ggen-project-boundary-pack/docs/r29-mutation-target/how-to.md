# How to admit a GitHub mutation target

1. Resolve repository and PR metadata immediately before mutation.
2. Compare the observed PR number, head ref, head SHA, base SHA, and capability identity with the previously admitted intent.
3. If any identity component differs, emit `REFUSED[TARGET_CORRESPONDENCE_FAILURE]`; do not mutate the candidate target.
4. Re-discover the intended target from immutable head/ref evidence, then re-run admission.
5. Record any already-performed reversible state mutation as an incident and attempt lawful compensation only when authority exists.
6. Bind successful mutation and containment to a receipt; never infer success from PR number or stale metadata alone.
