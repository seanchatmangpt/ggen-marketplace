# Ingest a profile into the AAIF pipeline

Use this guide when you have profile-shaped input (JSON, HTML, or plain text)
and need it normalized into the JSON + RDF form the AAIF solution pipeline
consumes.

## Scope

Intake is a local, offline normalization step. It performs no network I/O.
The commerce and actuation steps it feeds are covered by
`how-to/run-the-kind-commerce-rail.md` and
`reference/aaif-deployer-contract.md`. The sim/kind rail this feeds is
`PARTIAL_ALIVE`; real GCP procurement is `BLOCKED` (vendor onboarding).

## Prerequisites

- Python 3.11+ (older interpreters are refused at startup).
- `rdflib` available to the interpreter (intake emits Turtle).

## Run intake

```bash
python3 scripts/profile_intake.py <input.{json,html,txt}> \
  --out <dir> [--lock]
```

- `.json` input must be LinkedIn-profile-shaped JSON.
- `.html` input is parsed with stdlib heuristics (no external fetches).
- `.txt` input is parsed with line-based heuristics.

## Outputs

With `--out solutions/acme`:

- `profile.json` — normalized profile, sorted keys, schema
  `https://ggen.dev/marketplace/profile-intake/v1`.
- `profile.ttl` — graph using vendored `ontologies/public/` vocabularies
  (FOAF, Schema.org, Org) plus parallel `aaif:Agent` individuals minted from
  the normalized fields.
- `profile.lock.json` — with `--lock`, a sha256 fingerprint over both
  outputs using the length-prefixed-fold idiom shared with
  `scripts/marketplace.py`.

## Refusals

All refusals exit 2 and print a typed string:

| Code | Meaning |
| --- | --- |
| `REFUSED_PROFILE_UNREADABLE` | Input file could not be read or parsed |
| `REFUSED_PROFILE_EMPTY` | Input parsed to nothing usable |
| `REFUSED_PROFILE_NO_NAME` | No name could be extracted |

There is no LinkedIn API call anywhere in this path. Any guidance that says
otherwise is stale.

## Verify the outputs

```bash
python3 -c "import json;print(json.load(open('solutions/acme/profile.lock.json')))"
```

Lock digest mismatches after re-intake mean the normalized outputs changed
for the same input — that is a determinism defect, not expected behavior.

## See also

- `tutorials/deploy-an-aaif-solution.md` — the full loop.
- `reference/aaif-deployer-contract.md` — what consumes the intake outputs.
