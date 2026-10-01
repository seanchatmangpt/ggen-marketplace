# workflow-corpus-pack

Adversarial workflow corpus: 12 increasingly difficult semantic workflow
fixtures that a capability-resolution manufacture engine (ash_pplan v26.9.30,
built in a parallel wave -- this pack supplies its Chicago-test SUBJECTS, not
implementation) must successfully manufacture.

Lane 8 deliverable of the v26.9.30 capability-ecology wave
(`docs/jira/v26.9.30/_LANES.md`); the `wfc:` schema is pinned verbatim from
`docs/jira/v26.9.30/RESOLUTIONS.md`.

## What a fixture is

One directory `fixtures/<NN>-<slug>/` per subject:

- `fixture.ttl` -- individuals only. No class definitions, no cross-pack
  imports. Capabilities are referenced as pinned dotted-ID **string literals**
  (`wfc:capability "File.Write"`); the join to capability-family ontologies
  happens in the consumer resolver, never in-tree.
- `expected.md` -- human-readable rendering: goal, ordered tasks, branch
  table, required evidence, required authority, provider closure, forbidden
  realization, falsifier.

Every fixture records: semantic subject, goal, typed tasks
(`prov:Activity`, ordered by `prov:wasInformedBy` -- public PROV-O, no custom
ordering term), capabilities (pinned IDs), expected decomposition,
branch-explicit expected outcomes, required evidence, required authority,
expected provider closure (real realization names), forbidden realization
where useful, and the falsifier -- the observation that kills an engine that
mishandles the fixture.

## Corpus index

| # | fixture | adversarial condition | author |
|---|---------|------------------------|--------|
| 01 | `fixtures/01-filesystem-network-failure-isolation/` | typed network failure must not corrupt the file step's outcome | lane 8 |
| 02 | `fixtures/02-qualification-gated-release/` | release actuation reachable only through qualification gates, under authority; a refusing gate must prevent release | lane 8 |
| 03 | `fixtures/03-approval-halt-resume/` | halt opens an authority gap; resume re-binds FRESH authority; stale-envelope resume must be a typed refusal | lane 8 |
| 04 | `fixtures/04-provider-refusal-alternate/` | primary realization refuses typed; admitted alternate must complete; no stop-on-first-refusal | lane 8 |
| 05 | `fixtures/05-hddl-decomposition/` | HDDL hierarchical decomposition (pinned method, exact subtask set) | authored by lane 9 |
| 06 | `fixtures/06-fond-replanning/` | FOND replanning with typed recovery branches | authored by lane 9 |
| 07 | `fixtures/07-durability-evidence/` | durability + evidence: outcomes survive across checkpoint/replay | authored by lane 9 |
| 08 | `fixtures/08-sa2a-remote-refusal/` | distributed SA2A invoke under a verified remote authority envelope; typed remote refusal falls back to the admitted local realization | authored by lane 9 |
| 09 | `fixtures/09-dynamic-branch-switch/` | dynamic branch/switch | authored by lane 10 |
| 10 | `fixtures/10-recursive-bounded/` | dynamic recursion with a bound | authored by lane 10 |
| 11 | `fixtures/11-authority-denied-refusal/` | authority-denied: the engine must refuse typed | authored by lane 10 |
| 12 | `fixtures/12-interchangeable-realizations/` | interchangeable realizations inside one closure | authored by lane 10 |

## Join doctrine (consumer-side resolution)

There are NO in-tree cross-pack imports. `wfc:capability` literals are the
pinned dotted IDs from `RESOLUTIONS.md`; the consumer (ash_pplan) joins them
against the capability-family packs (`capability-ecology-pack (filesystem family)`,
`capability-ecology-pack (network family)`, `capability-ecology-pack (authority family)`, ...) by literal. The
same join-by-literal doctrine names realizations on `wfc:ProviderClosure`
individuals (this corpus uses `dcterms:identifier`; the conflict gate scans
all literal values on a closure individual property-agnostically).

## Gates (violation-row SELECTs: rows mean refusal)

Shared `f000_*` gates refuse MALFORMED fixtures corpus-wide; per-fixture
`f01_..f12_` gates fire on that fixture's specific adversarial condition and
are scoped by `wfc:fixtureNumber` so they can never fire on another fixture.
Every gate shipped by lane 8 carries a witnessed firing (anti-vacuity: a gate
with no witnessed refusal carries no bits).

| gate | fires on | witnessed firing by |
|------|----------|---------------------|
| `gates/f000_fixture_missing_goal.rq` | fixture with no `wfc:goal` | `qualification/fixtures/negative-missing-goal.ttl` + `witnesses/fail/f000_fixture_missing_goal.ttl` |
| `gates/f000_fixture_missing_capability_closure.rq` | task covered by no capability at any attachment point | `qualification/fixtures/negative-no-capability-closure.ttl` + `witnesses/fail/...` |
| `gates/f000_fixture_missing_expected_outcome.rq` | fixture with no `wfc:expectedOutcome` | `qualification/fixtures/negative-missing-expected-outcome.ttl` + `witnesses/fail/...` |
| `gates/f000_fixture_missing_falsifier.rq` | fixture with no `wfc:falsifierStatement` | `qualification/fixtures/negative-no-falsifier.ttl` + `witnesses/fail/...` |
| `gates/f000_consequential_task_without_required_authority.rq` | actuation-shaped capability with no declared authority (ambient-authority shape) | `qualification/fixtures/negative-missing-authority.ttl` + `witnesses/fail/...` |
| `gates/f000_forbidden_plus_expected_realization_conflict.rq` | closure admitting exactly what the fixture forbids | `qualification/fixtures/negative-forbidden-conflict.ttl` + `witnesses/fail/...` |
| `gates/f01_file_network_failure_isolation.rq` | fixture 01: write/post tasks sharing an outcome node | `witnesses/fail/f01_file_network_failure_isolation.ttl` |
| `gates/f02_release_requires_gates.rq` | fixture 02: qualification task not informing the release actuation | `witnesses/fail/f02_release_requires_gates.ttl` |
| `gates/f03_resume_rebinds_authority.rq` | fixture 03: resume with no re-bound authority or disconnected from its halt | `witnesses/fail/f03_resume_rebinds_authority.ttl` |
| `gates/f04_alternate_realization_completes.rq` | fixture 04: forbidden realization declared, no lawful primary->alternate pair | `witnesses/fail/f04_alternate_realization_completes.ttl` |

Gates `f05_*..f12_*` are owned by lanes 9/10 with their own negative fixtures
(see each fixture directory's header comment).

### Consequential-capability set (explicit, not heuristic)

`f000_consequential_task_without_required_authority.rq` enumerates the pinned
DO closure explicitly: `File.Write`, `File.Delete`, `File.Move`, `Http.Post`,
`Remote.Invoke`, `Domain.Action.Invoke`, `Domain.Change.Apply`,
`Process.Spawn`, `Process.Signal`, `Event.Emit`, `Authority.Grant`,
`Actuation.Execute`, `Workflow.Resume`, `A2A.Invoke`, `Receipt.Sign`.
Deliberately excluded: read/observe/query/record/schedule capabilities
(`File.Read`, `File.Exists`, `File.Copy`, `Dir.*`, `Http.Get`,
`Domain.Query.Read`, `State.*`, `Observation.*`, `Telemetry.Emit`,
`Schedule.*`, `Durability.*`, `Workflow.Halt` -- a halt suspends, it does not
actuate -- `Evidence.*`, `Provenance.Record`, `A2A.Discover`, `A2A.Await`,
`Authority.Verify`, `Endpoint.Resolve`). The pinned schema carries no
consequence-class flag, so the set is enumeration, not derivation (see failed
edges).

## Conformance notes for fixture authors (lanes 9/10 contract)

- Canonical falsifier shape is the PIN's: `wfc:falsifierStatement` as a string
  literal on the fixture. The corpus ALSO tolerates the variant lane 9 emitted
  first (property pointing at a `wfc:Falsifier` individual carrying the
  statement) -- the missing-falsifier gate accepts both.
- `wfc:capability` may attach per task or per fixture; the capability-closure
  gate accepts both attachment points. Fixture 01–04 use task-level.
- Realization names on closure individuals: use `dcterms:identifier` (join-by-
  literal doctrine). hex-package realizations (`reactor_file`,
  `reactor_req`) are cited as provider metadata ONLY -- never claimed as
  locally inspected. `AshAffidavit.*` / `AshA2A.*` names cited in fixtures
  01–04 were read off the local read-only checkouts `~/ash_affidavit`,
  `~/ash_a2a`.

## Verification

```bash
python3.11 qualification/verify.py                      # this pack's semantic court
python3.11 scripts/marketplace.py check workflow-corpus-pack   # real ggen, scoped
python3.11 -m pytest tests/test_workflow_corpus_pack.py        # structural + mutation courts
```

`gate-court.toml` deliberately runs with `require_pass=false, require_fail=false`
(failed edge below); the semantic pass/fail execution of witnesses lives in
`qualification/verify.py`.

## Failed edges (recorded, not pruned)

1. **exact-stem court vs concurrent gate authorship.** The structural witness
   court is pack-global, but gates/ carries per-fixture gates from three lanes.
   Requiring fail witnesses structurally would demand witness files for gate
   stems lanes 9/10 own -- a cross-lane break baked into the court. Resolution:
   `require_pass/require_fail=false` at the structural layer; semantic
   pass/fail witness execution enforced by `qualification/verify.py` (which
   asserts 0 rows on each owned pass witness and >= 1 row on each owned fail
   witness). `failed(edge_court) ≠ failed(G)`.
2. **Pin property count.** The wave dispatch prose said "the 12 properties";
   the pinned block in `RESOLUTIONS.md` lists 11 property definitions. The
   ontology defines EXACTLY the pinned 11 -- no 12th term was invented to
   reconcile the count. The pin is the authority, not the prose.
3. **No consequence-class flag on capabilities.** The pinned schema cannot
   express "this capability is actuation-shaped", so the authority gate's DO
   set is an explicit enumeration. Automatic classification from the
   capability-family ontologies is `UNSUPPORTED(generator-capability)` in this
   version -- intended owner: the capability-family packs (lanes 2-7), by
   admitting a consequence class their ontology side, after which this gate's
   VALUES-free successor can join on it. Until then, a corpus fixture using a
   NEW actuation-shaped capability must either declare
   `wfc:requiredAuthority` or extend the enumeration.
4. **No public ordered-decomposition vocabulary.** Task ordering is expressed
   with public PROV-O `prov:wasInformedBy` between task individuals plus a
   narrative `dcterms:description` on the `ExpectedDecomposition` individual;
   no custom order term was minted (public vocabularies before custom).
5. **No pinned realization-name property.** The pin fixes neither the
   property carrying realization names on a `ProviderClosure` individual nor
   the closure/conflict join. Resolution: `dcterms:identifier` recommended;
   the conflict gate scans ALL literal values property-agnostically so any
   lane's choice is checked.
6. **Shared `Http.Post` capability across primary and alternate tasks
   (fixture 04).** The alternate is the same semantic capability realized by
   the same hex package against a resolved alternate endpoint
   (`Reactor.Req.Post@alternate-endpoint`), not a different capability --
   without the shared literal, no gate could require the lawful
   primary->alternate ordering.

## Evidence boundary

Marketplace admission and ggen qualification only. SELECT-only; grants no DO
authority; BRCE remains the sole consequential actuation boundary. Provider
facts are cited, never fabricated: hex coordinates for `reactor_*`, read-only
local inspection for `ash_affidavit` / `ash_a2a`.
