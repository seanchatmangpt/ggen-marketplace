# Fleet Semantic Map — semantic A2A + sjira consolidation (v26.10.8)

Reference map of the fleet's semantic A2A and semantic-jira (sjira) plane as of
the semantic wave, 2026-10-08. Companion to
[`FLEET-DOC-MAP.md`](FLEET-DOC-MAP.md) (documentation map) and
[`../sjira/v26.10.8/SEMANTIC-WAVE-RECEIPT.md`](../sjira/v26.10.8/SEMANTIC-WAVE-RECEIPT.md)
(the wave's manufacturing receipt). Every path, SHA, and count below was
re-verified on the owning repos' pushed branches on 2026-10-08 (`git branch -r
--contains`); the branch carrying each landing is named.

## 1. Workgraph table

Each retained repo carries its v26.10.8 campaign workgraph under
`docs/sjira/v26.10.8/` (two exceptions noted). "Orders" counts subjects typed
`a sj:WorkOrder`.

| repo | workgraph path | branch (pushed) | SHA | orders |
|---|---|---|---|---|
| ggen-marketplace (hub) | `docs/sjira/v26.10.8/WORKGRAPH.ttl` | `main` / `lane/workgraph-gen` | `0d8d945c5` | 6 |
| ash_a2a | `docs/sjira/v26.10.8/WORKGRAPH.ttl` | `feat/tck-vuln-hardening` | `8e488461` | 4 |
| xaas | `docs/sjira/v26.10.8/WORKGRAPH.ttl` | `main` | `975095e1` | 4 |
| zcode-cli | `docs/sjira/v26.10.8/WORKGRAPH.ttl` | `fix/v26926-preview-publish-typed-skip` | `4a1ff83` | 5 |
| ash_pplan | `docs/sjira/v26.10.8-1/WORKGRAPH.ttl` | `fix/ggen-verify-header` | `e8f0fb5` | 5 |
| ex4pm | `docs/sjira/v26.10.8/WORKGRAPH.ttl` | `main` | `669334e` | 5 |
| beam4pm | `docs/sjira/v26.10.8/WORKGRAPH.ttl` | `main` | `45d28f3b` | 5 |
| ash_surface | `docs/sjira/v26.10.8/WORKGRAPH.ttl` | `main` | `c6010f8c1` | 4 |
| ash_r2rml | `docs/sjira/v26.10.8/WORKGRAPH.ttl` | `docs/doc-hdit-scaffold` | `37ce7e0` | 4 |
| ash_affidavit | `docs/sjira/v26.10.8/WORKGRAPH.ttl` | `main` | `3ecd4f7` | 5 |
| castle | `docs/sjira/v26.10.8/goal.ttl` | `main` | `313d67e` | 2 |
| ggen_igniter | `priv/ggen/semantic-jira-pack/ontology.ttl` | `feat/adr-0010-gate-convention` | `e42dbab` | — |

Path deltas, so consumers globbing the standard path do not miss them:

- **ash_pplan** landed at `v26.10.8-1/`, not `v26.10.8/`.
- **castle** takes the GoalCheckpoint successor shape (`goal.ttl`, 129 lines,
  11 GoalCheckpoint subjects, 2 typed WorkOrders) rather than a flat
  WORKGRAPH.ttl.
- **ggen_igniter**'s landing is the C13 self-hosting fixed-point work order
  inside the semantic-jira-pack ontology, not a per-repo workgraph file.
- The hub workgraph is the canonical sj: shape (102 triples recorded at
  landing; 140 lines on the lane branch today).

## 2. Agent-card table

| repo | card path | skills | generation law | authority statement |
|---|---|---|---|---|
| castle | `.well-known/agent-card.json` | 12 | hand-authored (no generator in repo — the one exception; see summary below) | v1.0 shape, authority NONE; the card exists and asserts no DO authority |
| ash_graphlaw | `priv/graphlaw/cards/` | 14 | registry-generated (one card per `gac:Capability`; `scripts/import_registry.sh` regenerates in write mode, `--check` verifies, gated on the registry_sha256 digest check) — generation is part of the law, not a one-off | authority NONE; cards carry none, standing is receipt-derived |
| ash_a2a | `priv/sa2a/self-agent-card.json` | 4 | capability-index (`mix ash_a2a.self_card` from the capability surface) | deterministic generation; CONSTRUCT-at-most |
| ash_surface | `priv/generated/agent_card.json` | 2 | runtime-serialization (court test regenerates and byte-compares; a stale artifact fails closed) | authority NONE |
| ferroplan | `crates/ferroplan-wasm/cards/` | 38 | registry-generated (one card per op from `crates/ferroplan-wasm/registry/capability-registry.json`, registry_sha256-digest-pinned, `MANIFEST.sha256` over the card set) | planner CONSTRUCT — candidate output, never actuation; returned plans are candidates for host-side admission; no DO authority (`authority_claim: NONE` in every card) |
| ex4pm | `priv/cards/` | 9 clusters / 222 skills | module-docs (`scripts/gen_agent_cards.py` walks `lib/ex4pm`, each skill carries `source_file`/`source_module` provenance; `generatedFrom: lib/ex4pm`) | authority NONE; cards descriptive of the process-mining surface |

Skill counts re-counted at exact pushed SHAs 2026-10-08: castle 12,
ash_graphlaw 14, ash_a2a 4 (@7d646598), ash_surface 2 (@8bc9b7509),
ferroplan 38 cards @057ff803 (39 files minus `MANIFEST.sha256`), ex4pm 9
cluster files / 222 skills @50071c47. All six surfaces carry authority
NONE / CONSTRUCT-at-most; no card grants DO authority by existence.

Generation-law summary: every card set landed in the ferroplan, ex4pm, and
ash waves is generator-emitted from a real surface — registry digest
(ferroplan, ash_graphlaw), capability index (ash_a2a), module-docs walk
(ex4pm), or runtime serialization with byte-compare courts (ash_surface).
Zero hand-authored cards in those waves. Castle's top-level card was the
last hand-authored card in the fleet; it has since been converted
(§2.1).

## 2.1 Final consolidation additions (2026-10-08)

Three late-wave landings, re-verified on the owning repos' pushed refs in
this lane:

| repo | surface | skills | generation law | SHA (branch, pushed) |
|---|---|---|---|---|
| castle | `docs/sjira/v26.10.8/castle-gates-skills.json` + `skills.ttl` | 14 | generator-emitted: `scripts/gen_skills_json.py` renders the fourteen v26.9.28 crown gates (CASTLE-28-0..13) as `gate_status` skills — byte-identical across runs, fail-closed on missing properties / non-exposed skills / missing law sentence / non-ALIVE generator; ceiling CONSTRUCT, law sentence "receipt-driven STOP; SELECT never implies DO" | `0244c82` (`main`) |
| castle (card itself) | `.well-known/agent-card.json` | 12 | generated from `#[verb]` registrations — the fleet's last hand-authored card conversion | `edaf206` (`main`) |
| wasm4pm | `.well-known/agent-card.json` (actuator surface) | 6 | hand-authored truthful v1.0 card: `execute`, `effect.digest`, `certificate.signing_message`, `verify`, `resource.admit`, `ledger` | `7146a53129681008e255375e338fe47bb11cd06f` (`docs/sa2a-actuator-agent-card-v2`) |

Skill counts re-counted at the exact SHAs above; the wasm4pm card carries 6
skills (measured; an earlier consolidation brief said 7 — 6 is the grounded
count at that SHA). The wasm4pm actuator card is the one new hand-authored
surface — its generation-law conversion is the natural follow-up, same as
castle's was.

Workgraph SHACL validation: the wg-shacl lane's validation report had **not
landed** on any pushed ggen-marketplace ref as of this consolidation
(2026-10-08, `git ls-remote` checked) — no SHACL results are citable in
this map yet; they belong in §1 when the report lands.

## 2.2 Seed → generator convergence

From [`../sjira/v26.10.8/CONVERGENCE.md`](../sjira/v26.10.8/CONVERGENCE.md)
(`gen_workgraph.py` regenerates each agent-authored seed from raw repo
state, zero LLM, every delta dispositioned):

| repo | shape convergence | order coverage |
|---|---|---|
| ggen-marketplace | 87.5% (14/16) | 83% (5/6) |
| zcode-cli | 55% (11/20) | 20% (1/5) |
| ash_affidavit | 71% (12/17) | 67% (4/6) |
| **overall** | **69.8% (37/53)** | **~60% (10/17)** |

Refusals the generator correctly will not copy: `authorityCeiling "DO"` on
lane orders, receipt-less ALIVE / `EXECUTED_VERIFIED` standings, vague
ceiling strings. Doctrine: the agent-authored workgraph is the seed; the
generator is the successor format; regeneration without an LLM is the
acceptance test.

## 3. The non-LLM chain

The wave's manufacturing chain runs without LLM participation end to end:

```text
gen_workgraph.py → admit_workgraphs.py → certify (ex4pm)
```

- **gen_workgraph** (`scripts/gen_workgraph.py`, landed `27256497d` on
  `lane/workgraph-gen`): deterministic non-LLM sj: emission — same input,
  same workgraph bytes. Determinism proven on the lane; merge to the default
  branch pending.
- **admit_workgraphs** (`scripts/admit_workgraphs.py`, landed at hub
  `0d8d945c5`): fleet workgraph admission driver +
  `docs/sjira/v26.10.8/ADMISSION-LEDGER.jsonl`. Ledger re-counted from the
  file in this lane: **49 entries, 23 admitted, 26 typed refusals** (e.g.
  `{"refusal_reason": "{:invalid_sha, :base_sha, \"20aadd175\"}"}`) — every
  refusal names its broken term; the 26 refusals are falsifier output, not
  debt.
- **ex4pm certify**: cited as `f4104bfa` at landing, **NOT VERIFIED** —
  `git cat-file -t f4104bfa` returns "not a valid object name" in
  `/Users/sac/ex4pm` and no matching remote ref. Certify commits exist nearby
  (`6d7be38` "certify bounded semantic convergence" et al.) but the cited SHA
  could not be resolved. Standing: UNKNOWN until the correct SHA is supplied.

Standing of the chain: PARTIAL_ALIVE — generate → admit → ledger witnessed;
canonical regen, ex4pm certify SHA, and affidavit signing (§5) remain open.

## 4. Ownership map

`castle` `docs/sjira/v26.9.28/repos.ttl` pins the fleet's capability
ownership: **22 retained runtime capabilities, one irreducible owner each**
(all `KEEP` disposition):

| capability | owner |
|---|---|
| CONSEQUENTIAL_ADMISSIBILITY | castle |
| RUNTIME_EXISTENCE | xaas |
| PROCESS_COORDINATION | beam4pm |
| SA2A_TRANSPORT | ash_a2a |
| SEMANTIC_LAW_DERIVATION | graphlaw |
| BEAM_GRAPHLAW_MEMBRANE | ash_graphlaw |
| CRYPTOGRAPHIC_STANDING | affidavit |
| SEMANTIC_PROJECTION | ash_r2rml |
| PLANNER_SEARCH | ferroplan |
| PLANNING_SEMANTICS | ash_pplan |
| DETERMINISTIC_WASM_RUNTIME | wasm4pm |
| COMPILED_MODEL_PROGRAMS | dspy-wasm |
| BOUNDED_RESOURCE_ALLOCATION | bcinr |
| BOUNDED_ADVERSARIAL_EXECUTION | gymact |
| FAILURE_DISCOVERY | autofde-lab |
| SEMANTIC_MANUFACTURE | ggen_igniter |
| SEMANTIC_CAPITAL_REGISTRY | ggen-marketplace |
| FLEET_MANUFACTURE_QUALIFICATION | ggen-ecosystem |
| LEGACY_EXTRACTION | ash_kudzu |
| PROCESS_ANALYTICS | process-intelligence |
| EVIDENCE_FACT_MODEL | mfact |
| GIT_EVENT_EVIDENCE | gitvan |

Non-`KEEP` dispositions in the same file (not capability owners):
`REPLACE` (ggen), `WRAP` (ex4pm/ash_ex4pm, zcode-cli/chatgpt-cloud-elixir,
ash_surface/ash_expo, zoela/cargo-cicd, and others), `KEEP_KNOWLEDGE_PLANE`
(chatman-ecosystem, engineering-standards, agile-protocol-specification,
praxis→ABSORB), `SUPPORTING_CANDIDATE` (mfw, ostar, mmdio, wasm4pm-compat,
dteam, mcpp, chatman-nano-stack — not permanent dependencies until they prove
a unique capability).

## 5. The dependency arrow

The wave's cross-repo dependency chain, each hop gated on the previous:

```text
affidavit sign → sj:/card claim → graphlaw adjudicate → ferroplan consume
        ↑
  crypto_trust gate
```

- **affidavit sign** (ash_affidavit, `lib/ash_affidavit/signing.ex`, the
  `crypto_trust_verify` law): signing is gated on `crypto_trust` landing —
  per the wave receipt, the signing step cannot be admitted until
  `crypto_trust` lands (open residue §5.7 of the receipt).
- **sj:/card claim**: a signed affidavit becomes an sj:-shaped claim carried
  on the agent-card surface (§2).
- **graphlaw adjudicate**: the graphlaw membrane (ash_graphlaw,
  BEAM_GRAPHLAW_MEMBRANE) adjudicates the claim against its capability
  registry — the same law that generates the 14 cards.
- **ferroplan consume**: the planner (PLANNER_SEARCH) consumes adjudicated
  claims as plan inputs; the hub workgraph's W803 orders witness the
  consumer re-gen + pin determinism side (`ggen sync` in the affidavit
  consumer, `just wasm-gen` in ferroplan, graphlaw pin `fc23a292` re-derived
  reproducible at `f2e6e02`).

The chain is only as strong as its first hop: with `crypto_trust` unlanded,
the arrow is BLOCKED at sign, and nothing downstream may claim ALIVE through
it.

## 6. Per-repo-law doctrine

The wave surfaced a standing rule: **each repo keeps its own landing law, and
the hub does not normalize them away.**

- frozen-duckdb keeps its `changelog.ttl` law;
- wasm4pm's markdown charter is defensible as-is;
- receipts never map into `sj:` — sj: shapes the *workgraph*; receipts stay
  in their native per-repo form (clnrm's TestReceipt → sj:Receipt *spec* is a
  projection declaration, not a rewrite);
- the admission kernel recognizes exactly six standing strings, nothing more
  (`UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE`, `BLOCKED`, `BUILD_BROKEN`,
  `UNSUPPORTED`, plus typed `REFUSED:*`);
- workgraph shape itself is per-repo lawful: castle's GoalCheckpoint
  successor shape and ash_pplan's `v26.10.8-1` path are landings, not
  defects.

## Replay

```bash
# workgraph SHAs on pushed branches
for r in ash_a2a ash_surface beam4pm zcode-cli ash_affidavit ex4pm ash_pplan ash_r2rml castle ggen_igniter xaas; do
  git -C /Users/sac/$r log --all --oneline -1 -- 'docs/sjira/v26.10.8*'
done

# agent-card skill counts
python3 -c "import json;print(len(json.load(open('/Users/sac/castle/.well-known/agent-card.json'))['skills']))"
python3 -c "import json;d=json.load(open('/Users/sac/castle/docs/sjira/v26.10.8/castle-gates-skills.json'));print(len(d['skills']),d['authorityCeiling'])"
ls /Users/sac/ash_graphlaw/priv/graphlaw/cards/ | wc -l
python3 -c "import json;d=json.load(open('/Users/sac/ash_a2a/priv/sa2a/self-agent-card.json'));print(len(d['skills']))"
python3 -c "import json;print(len(json.load(open('/Users/sac/ash_surface/priv/generated/agent_card.json'))['skills']))"
git -C /Users/sac/wasm4pm show 7146a53129681008e255375e338fe47bb11cd06f:.well-known/agent-card.json | python3 -c "import json,sys;print(len(json.load(sys.stdin)['skills']))"

# admission ledger recount
python3 -c "import json;ls=[json.loads(l) for l in open('/Users/sac/ggen-marketplace/docs/sjira/v26.10.8/ADMISSION-LEDGER.jsonl')];print(len(ls),sum(x['admitted'] for x in ls),sum(not x['admitted'] for x in ls))"

# ownership map
grep -c 'ownsCapability' /Users/sac/castle/docs/sjira/v26.9.28/repos.ttl
```

## Card Validation (2026-10-08)

Fleet-wide validation via `scripts/validate_agent_cards.py` (read cards from
each owning repo's canonical checkout; wasm4pm falls back to its card branch
`docs/sa2a-actuator-agent-card-v2` when its land is not in the worktree).

Contract: required `name`/`description`/`version`/`skills[]`
(id/name/description/tags nonempty)/`supportedInterfaces[0].protocolVersion`;
forbidden top-level `url`/`preferredTransport`; skill ids
`<tool>.<cluster>.<verb>`-ish (>=2 dot segments, `[A-Za-z0-9_-]` + trailing
`?`/`!` for Elixir predicates); authority statement required in description.

Result: 69 cards, 0 violations, all 8 repos PASS. Violations found and fixed
in the owning repos via their generators, then regenerated (no hand edits to
generated output):

| repo | cards | violations found | fix | commit |
|---|---|---|---|---|
| castle | 1 | 0 | none needed | 0244c82 (already compliant) |
| graphlaw (ash_graphlaw) | 14 | 0 | none needed | — |
| ex4pm | 9 | 27 | add version/supportedInterfaces/tags (gen_agent_cards.py) | 6758bd7 |
| ferroplan | 38 | 114 | add version/supportedInterfaces/skills[] (gen_capability_cards.py) | 84a6289 |
| ash_a2a | 1 | 1 | authority statement (mix ash_a2a.self_card) | b40abf82 |
| ash_surface | 1 | 2 | drop top-level url, authority statement | 57c0100f0 |
| gymact | 4 | landed by sibling lane | a113a939 + 6204b636 | — |
| wasm4pm | 1 | 2 | drop url, add supportedInterfaces (card branch) | 070c5e96f |

Re-run: `python3 scripts/validate_agent_cards.py` (exit 0 iff every repo PASS;
ABSENT lands fail closed).
