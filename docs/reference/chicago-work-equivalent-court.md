# Chicago court: marketplace work-equivalent claims

This court operationalizes claims such as:

> "ggen-marketplace can collapse a solution space whose independent human reconstruction cost is 500,000,000 person-years."

**Measured status at v26.9.30: UNSUPPORTED (unmeasured).** The committed ledger
`evidence/chicago/marketplace-work-equivalent.json` holds 0 admitted evidence items, so the court
returns `UNSUPPORTED:INSUFFICIENT_INDEPENDENT_HUMAN_BASELINE_EVIDENCE` with a lower bound of 0.0
person-years. The 500,000,000 person-year figure is a target named by the ledger, not a measured
result, and must not be cited as fact.

It does **not** treat that sentence as true because the repository is large or because many packs can be combined. The court exists to make the claim falsifiable.

## Exact subject

Every receipt binds:

- repository: `seanchatmangpt/ggen-marketplace`;
- exact Git HEAD;
- the observed pack-subject count;
- a SHA-256 fingerprint over the real admitted pack tree;
- the exact evidence ledger used for the calculation.

Historical success at another SHA does not transfer standing.

## What counts

Only independently sourced lower-bound evidence may contribute person-hours. Each evidence row must identify:

- an evidence id;
- the capability or work boundary being estimated;
- a positive **lower bound** in person-hours;
- an overlap group;
- an allowed source type;
- an external source URI;
- a SHA-256 source digest;
- one or more concrete repository subject paths.

Allowed source types are deliberately narrow:

- `audited_record`
- `contract_record`
- `external_measurement`
- `published_study`

The court rejects self-assertion and model estimates as labor evidence.

## What never counts by itself

The following are explicit non-evidence:

```text
commit count
lines of code
pack count
repository size
number of templates
raw Cartesian-product or 2^N combinatorics
LLM-generated estimates
the claim itself
```

These may describe throughput or addressable state space. They do not establish human reconstruction time.

## Double-counting rule

Evidence that describes overlapping human work must share an `overlap_group`.

For each group the court admits only the largest lower bound:

```text
group_hours = max(evidence_lower_bounds_in_group)
```

Only disjoint groups add:

```text
admitted_hours = sum(group_hours)
person_years_lower_bound = admitted_hours / hours_per_person_year
```

This makes duplication reduce leverage rather than inflate it.

## Standing

The ledger currently names a target of:

```text
500,000,000 person-years
2,080 hours/person-year
```

The result is:

```text
ALIVE
```

only when the overlap-safe independently evidenced lower bound is greater than or equal to the target.

Otherwise the claim receives:

```text
UNSUPPORTED:INSUFFICIENT_INDEPENDENT_HUMAN_BASELINE_EVIDENCE
```

Malformed or inadmissible evidence receives a typed `REFUSED:...` result.

`UNSUPPORTED` is not failure of the marketplace. It means only that this specific numerical human-equivalent-work claim has not acquired standing.

## Chicago properties

The court follows the repository's existing Chicago doctrine:

1. **real subject** — scans the actual `packs/` tree;
2. **zero mocks** — CLI and replay tests execute real filesystem and Git boundaries;
3. **exact identity** — receipt binds `git rev-parse HEAD`;
4. **attempted falsification** — self-assertion, non-independent source classes, missing subjects, and double counting are explicitly attacked;
5. **independent observation boundary** — only admitted evidence types can supply person-hours;
6. **deterministic replay** — two runs at the same subject and ledger must produce byte-equivalent JSON;
7. **receipt** — the output is a machine-readable standing receipt;
8. **fail closed** — `--enforce` exits non-zero unless the numerical claim is ALIVE.

## Run

Observe the current standing without requiring the claim to pass:

```bash
python3 scripts/chicago_work_equivalent.py \
  --root . \
  --ledger evidence/chicago/marketplace-work-equivalent.json
```

Write a receipt:

```bash
python3 scripts/chicago_work_equivalent.py \
  --root . \
  --ledger evidence/chicago/marketplace-work-equivalent.json \
  --receipt /tmp/chicago-work-equivalent.json
```

Require the 500M-person-year claim to have standing:

```bash
python3 scripts/chicago_work_equivalent.py \
  --root . \
  --ledger evidence/chicago/marketplace-work-equivalent.json \
  --enforce
```

Exit codes:

- `0` — court executed and emitted a receipt;
- `2` — evidence or subject was refused;
- `3` — `--enforce` was requested but the claim is unsupported.

## Evidence promotion

Do not add a row merely because an estimate sounds conservative. The source needs to support the lower-bound number and the row needs to bind that number to concrete marketplace subject paths.

When two sources cover the same work, put them in the same overlap group. When uncertainty exists about overlap, treat the work as overlapping until independence is established.

The strongest future extension is to replace narrative labor estimates with observed reconstruction trials: independent teams attempt bounded capabilities without the marketplace, the same capability is manufactured from admitted marketplace source, both runs preserve artifacts and receipts, and only the measured counterfactual lower bound enters this ledger.
