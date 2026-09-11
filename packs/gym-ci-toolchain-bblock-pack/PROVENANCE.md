# PROVENANCE — gym-ci-toolchain-bblock-pack

Every number in `ontology.ttl` came from a command run against the real trees on
2026-09-06, not from a repo name or a field name.

## Commands and their real output

```
$ cd /Users/sac/gym-ecosystem
$ ls vendor/*/.github/workflows/*.yml | wc -l
      62

$ grep -h "uses: actions/checkout" vendor/*/.github/workflows/*.yml | sort | uniq -c | sort -rn
  28         uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6
  23       - uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6
   9         uses: actions/checkout@v4
   7       - uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803
   5       - uses: actions/checkout@v4
   4         uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1
   2         uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
   1         uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803
   1         uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262

$ for r in autofde-lab beam4pm ggen-ecosystem; do
    grep -c "@v[0-9]$" vendor/$r/.github/workflows/*.yml | awk -F: '{s+=$2} END{print s}'
  done
29   # autofde-lab
0    # beam4pm
7    # ggen-ecosystem
```

The list/dash prefix difference is presentation only; the ontology folds the two
`d23441a4… # v6` spellings into 51 and the two bare-SHA spellings into 8.

## What is deliberately NOT asserted

Ten of the thirteen `vendor/` submodules (`awesome-ai-gyms`, `biblegym`,
`chatgptgym`, `claudecodegym`, `fdegym`, `gitgym`, `gymact`, `lifegym`, `rrgym`,
`SREGym`, `ww3gym`) have no checked-out working tree on this machine — `ls` of
each returns empty. They are recorded as `gymci:UninitializedSubmodule` with no
workflow counts. An uninitialized submodule is UNKNOWN, not evidence of no CI.

## Authority boundary

`gymci:directActuation false`, mirroring `fortune5-deployment-blocks-pack`'s
`bb:directActuation false` and its `gates/020_safe_acyclic_broker_only.rq`
refusal shape. Verified as a real refuser, not a decorative gate:

```
$ # inject an actuating step and a floating pin into the graph
020_no_actuation  REFUSED rows= 1   step-evil gymci:runCommand terraform apply -auto-approve
010_pin_required  REFUSED rows= 1   bad-pin   gymci:actionRef  actions/checkout@v4
$ # against the pack's own unmodified ontology (219 triples)
010_pin_required.rq violations= 0 PASS
020_no_actuation.rq violations= 0 PASS
```

## Real generation run

```
$ ggen sync run   # ggen 26.8.28
{
  "written": ["docs/GYM_CI_PIN_DRIFT.md", ".github/actions/gym-toolchain/action.yml"],
  "graph_hash_hex": "50da4feb9dc7a988d3dfec1123e870e74c53204a71afd72dfeccf019ed8c7e99",
  ...
}
```

Re-running with no input change produced byte-identical output (`shasum` equal),
and the second run after a template-only edit reported `action.yml` as `skipped`
while rewriting only the report — real idempotence, checked, not assumed. The
rendered `action.yml` parses under `yaml.safe_load` with 3 composite steps.
