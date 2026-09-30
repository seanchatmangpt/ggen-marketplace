# Industry Closure Pack

Industry Closure treats a future software requirement as a semantic subject to be
closed over known public knowledge before any implementation work is admitted.

The pack does **not** assume that a new requirement implies new software
semantics. It tests the stronger default:

```text
future requirement
  -> public ontology bindings
  -> semantic composition
  -> closure assessment
  -> qualified manufacture
```

Only the exact residual that cannot be represented by the admitted ontology set
may leave the closure court.

## Law

For a requirement `R` and admitted public ontology set `O*`:

```text
closed(R) := representable(R, Cl(O*))
residual(R) := R - Cl(O*)
```

A requirement marked `CLOSED` MUST have at least one admitted public-ontology
binding and qualification evidence, and MUST NOT have an unresolved residual.

A requirement marked `RESIDUAL` MUST identify the exact missing semantic
capability. The residual is an input to Semantic Jira / marketplace feedback,
not permission for ambient prompt-to-code or DO authority.

## Why this is different from a template catalog

A concrete future application does not have to exist in advance. A requirement
may be novel as a combination while its semantic constituents are already
known. The closure subject is the mapping from admitted semantics to a
manufacturable artifact, not a lookup of previously generated source code.

This pack deliberately separates:

- **public domain semantics** — the vocabulary of the industry;
- **local requirement facts** — the particular requested system;
- **closure assessment** — whether the requirement is representable now;
- **semantic residual** — the exact missing meaning, if any;
- **manufacture** — owned by ggen projection packs after admission.

The companion `sjira-marketplace-feedback-pack` turns residuals into admitted
Semantic Jira work orders and marketplace capability deltas so the closure
frontier can expand rather than repeatedly rediscovering the same gap.
