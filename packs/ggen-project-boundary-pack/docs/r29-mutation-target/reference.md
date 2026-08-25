# Mutation-target correspondence R29

A GitHub mutation target is admitted only by the conjunction `repository × PR number × head ref × head SHA × base SHA × intended capability`. PR number alone is not identity under concurrent autonomous publication. Before readiness, close, merge, review, label, or branch-affecting mutation, re-resolve the full tuple and typed-refuse any mismatch.

The R29 incident fixture preserves the observed concurrent publication race: intended postmerge-capital PR #224/head `16a8e4b…` coexisted with unrelated opportunity-currentness PR #223/head `18fcc286…`. A ready-state mutation reached #223 before the mismatch was detected; no wrong-target merge occurred. The incident is retained as falsifier capital.
