# Pack replaceability across seanchatmangpt repos

Question: how much handwritten code across all my repos can be replaced by packs, and if not, what is the delta?

All figures are sampled estimates (directory-level line counts plus reading file heads and pack template names). None is a measured pack run. Percentages are accurate to roughly plus or minus 5 points per repo.

## 1. Headline numbers

| Metric | Value |
|---|---|
| Repos in scan | 228 (a few unreachable or empty, see below) |
| Handwritten LOC (denominator, vendored/generated/lockfiles/prose-only docs excluded where scanners could) | about 26.9M |
| Replaceable by existing packs (full credit for matching shapes, covered fraction for partial matches) | about 1.49M LOC, **about 5.5%** |
| Already generated (ggen or other generators) | about 1.06M LOC |
| Of which class `already_pack_manufactured` | about 1.01M LOC |

Per-class LOC (an area is counted in full in its class, so the "gap" row is the whole area, not just the uncovered part):

| Class | LOC | Share of handwritten |
|---|---|---|
| irreducibly_handwritten | 18.33M | 68% |
| pack_exists_but_gap | 5.61M | 21% |
| packable_but_no_pack | 3.74M | 14% |
| replaceable_by_existing_pack | 0.46M | 1.7% |

The shares above sum to more than 100% because the "already_pack_manufactured" LOC is excluded from the denominator in some repos but listed as a class in others. Read them as relative magnitude.

Answer: roughly 5 to 6 percent of handwritten code is replaceable today. The unweighted per-repo median is about 5 to 8 percent. The delta is about 94 percent.

Concentration caveat: a few giant repos dominate the totals. chatman-nano-stack (about 3.3M), bytestar (about 2.4M), yawl (about 1.7M), unjucks (about 1.25M), unrdf (about 1.09M) and wasm4pm (about 0.9M) together account for more than half of the denominator. Their LOC splits are the least reliable (heavy duplication, committed build output, LLM-generated reports).

Unreachable or empty repos (nothing measured, 0% means "no denominator"):
- Unreachable: **seanchatmangpt/unrdf-kgc**, **seanchatmangpt/unrdf-yawl** (empty clone, API fallback denied).
- Empty or placeholder (denominator 0): unrdf-experiments, my-new-repo, hello, hello_youtube_chat, infinite-agentic-cli, tcps-accept-test-28378, tcps-accept-test-sandbox, tcps-accept-test-2-sandbox, become-ai-first, ash_supabase (README only), agent-actor, ranchr, unovis_live_demo.

Other caveats on the headline: the pct figures given per repo are the scanners' own formula (existing pack output plus covered fraction of partial matches). Replaceable is not replaced. Every replaceable figure assumes the consumer first authors the RDF/SHACL facts, so effort moves from code to RDF and is not eliminated.

## 2. Repos ranked by replaceable LOC (approximate, handwritten LOC x scanner pct)

| # | Repo | Handwritten LOC | pct | Approx replaceable LOC | Uses ggen today |
|---|---|---|---|---|---|
| 1 | bytestar | 2.39M | 7.7 | 184k | local ggen.toml (docs only) |
| 2 | chatman-nano-stack | 3.3M | 4.1 | 136k | minimal, no packs |
| 3 | yawl | 1.72M | 7.5 | 129k | local templates |
| 4 | ggen | 641k | 12.2 | 78k | yes |
| 5 | erlmcp | 815k | 7.3 | 59k | ad hoc |
| 6 | unjucks | 1.25M | 4.1 | 51k | no (competing generator) |
| 7 | knhk | 573k | 8.0 | 46k | local pipeline |
| 8 | chatman-ecosystem | 404k | 11 | 44k | shallow |
| 9 | wasm4pm | 897k | 4.0 | 36k | local packs |
| 10 | qlever_poc | 602k | 5.3 | 32k | no |
| 11 | autofde-lab | 380k | 8.3 | 32k | yes |
| 12 | yaml-cloud | 319k | 9.0 | 29k | no |
| 13 | spec-kit | 262k | 8.5 | 22k | local templates |
| 14 | unrdf | 1.09M | 2.0 | 22k | own generators |
| 15 | chatmangpt | 351k | 6.0 | 21k | ontology flow, not packs |
| 16 | clnrm | 217k | 9.4 | 20k | yes (not portable) |
| 17 | jotp | 333k | 5.9 | 20k | local jgen |
| 18 | xaas | 221k | 8.0 | 18k | yes |
| 19 | cre | 392k | 4.0 | 16k | yes |
| 20 | mcpp | 486k | 3.3 | 16k | no |
| 21 | dslmodel | 176k | 8.4 | 15k | no (own Weaver/Jinja) |
| 22 | praxis | 237k | 6.5 | 15k | yes, about 45 local packs |
| 23 | ai-self-sustaining-system | 193k | 8.0 | 15k | no |
| 24 | java-maven-template | 175k | 7.3 | 13k | local |
| 25 | optimus | 171k | 7.0 | 12k | wrapper only |
| 26 | weavergen | 125k | 9.3 | 12k | no |
| 27 | kcura | 122k | 9.4 | 11k | no |
| 28 | ostar | 340k | 3.0 | 10k | local rules |
| 29 | dspygen | 82k | 11.6 | 9.5k | yes (local templates) |
| 30 | gymact | 169k | 5.0 | 8.5k | yes |

The remaining roughly 200 repos each contribute under about 8k replaceable LOC. Many tiny repos show high percentages on tiny bases: homebrew-tap 59.7%, igpgen 30%, ggen-ui 23%, hive 17%. These matter little in absolute terms.

Repos with the highest replaceable share among those over 10k LOC: ggen 12.2%, dspygen 11.6%, chatman-ecosystem 11%, uvmgr 10.8%, ex4pm 10.9%, ash_ex4pm 12.2%, cargo-cicd 13%, ash_planning_center 12.7%, chatgpt-cloud-elixir 12.4%.

## 3. The delta: recurring themes and proposed packs

Pack class follows `docs/reference/pack-classes.md`. Language-target projection templates are CapabilityPacks (one orthogonal capability over an admitted kernel such as SHACL projection). Concrete platform scaffolds are ProfilePacks. Bundles are UmbrellaPacks. LOC unlocked means LOC of the matching area that becomes packable (or more covered) once the pack exists. It is an upper bound on the shape-driven part, not on behavior. Handler bodies and logic stay handwritten.

### Prioritized proposals

| Priority | Pack (new or extended) | Class | Repos it would unlock | LOC unlocked (approx) |
|---|---|---|---|---|
| 1 | **shacl-to-rust-serde-pack** (structs, enums, thiserror errors, serde/schemars, newtype IDs, optional bitflags and port traits) | CapabilityPack over shacl-projection | ggen, knhk, praxis, a2a-rs, tower-lsp-composition, wasm4pm-compat, lsp-max, kgold, ggen-mcp, clnrm, clnrm_prototype, chicago-tdd-tools, dteam, mcpp, stpnt, castle, kcura, osx-clnr, unibit, pm4py-rs, swarmsh-v2, capability-map, semantic_bit, wasm4games | about 170k |
| 2 | **Extend clap-noun-verb-pack with a logic/handler slot** (structural, cross-cutting) | CapabilityPack (extension) | ggen, clnrm, knhk, lsp-max, praxis, mfw, dteam, cargo-cicd, kcura and about 20 other Rust CLI repos | no new LOC; raises today's roughly 25-40% skeleton coverage to cover roughly 10k+ LOC of verb bodies per large repo. Today every Rust repo reports "no logic slot" as the limiting factor |
| 3 | **ts-noun-verb-cli-pack (citty/commander, TS and JS)** | CapabilityPack | unjucks, unrdf, wasm4pm, chatmangpt, gitvan, kgn, figex, citty-test-utils, un-test-utils, zcode-cli, sovedge, zoeapp, astro, ostar-priv, zod-to-from | about 205k |
| 4 | **Nuxt/Vue/Nitro profile family**: nuxt-ui-dashboard-pack, nitro-api-route/mock-fixture pack, nuxt-project-scaffold | ProfilePack (with an UmbrellaPack bundle) | chatman-nano-stack, bytestar, sovedge, dogturk, revops, lawd, igp, gitgym, dsoai-dash, nuxt-pro-all, docs, docs2cli, vue-storybook-test, chat-with-pdf, fastsocket, nuxt-ai-chatbot, neako-web, full-stack-rubric, vuefire-test, starter and others | about 560k, but about 460k of it sits in chatman-nano-stack and bytestar and is the least reliable estimate |
| 5 | **Java family**: shacl-to-java-records-pack, junit5-scaffold-pack, java-eip-messaging-pack, maven-multimodule-pack | CapabilityPack x3 plus ProfilePack | yawl, yawlv6, jotp, java-maven-template, dtr | about 390k, but about 247k is yawl Maven XML (low-yield repetition) |
| 6 | **Erlang/OTP scaffold + eunit/CT suite packs** (gen_server/supervisor/app.src, gen_yawl-style pattern modules) | CapabilityPack | cre, erlmcp, bytestar, chatman-nano-stack | about 135k (about 285k with bytestar's Erlang) |
| 7 | **Test-scaffold packs for non-Rust/Python stacks**: Rust algorithm/test scaffold (driven by algorithm registry), vitest+cucumber/Gherkin, ExUnit contract/conformance, pytest-bdd, Go table tests, JUnit | CapabilityPack family | wasm4pm (90k Rust), ggen (70k), kgn (30k), unjucks (60k), dogturk, xaas (20k), ex4pm, ash_a2a, knowd (15k), yawl, full-stack-rubric | about 450k of scaffolding; assertions stay handwritten |
| 8 | **Phoenix/LiveView/Ash app scaffold + Ecto context + HEEx** (phoenix-ash-app-pack, phoenix-liveview-crud-pack, ash-json-api-resource extension) | ProfilePack | mrkt (27.7k), xaas (6.1k), ash_swarm, helpdesk, kanban, glass, finhelp, dubaiedge, ash_n8n, myapp, srvcol, chatgpt-cloud-elixir, ai-self-sustaining-system, desktop_commander_mcp | about 62k |
| 9 | **Python project scaffold pack** (pyproject/poetry/uv, Dockerfile, compose, devcontainer, pre-commit, Sphinx; cruft/copier replacement) | ProfilePack | about 30 small repos (pyn8n, dspyfun, bkgn, helpgen, swrm, metadspy, streamlitgen, hive, qfc, igpgen, arazzo-ai, foam, agwa, gencli, healgen, lchop, cosg and others) | about 12k, very high repo count, very low LOC per repo |
| 10 | **Python projection variants**: shacl-to-python-dataclass/StrEnum (frozen, slots), SQLModel/SQLAlchemy ORM, OpenAPI-to-client | CapabilityPack | gymact (13k), autofde-lab (30k), uvmgr, yaml-server, dspygen, pyn8n (745 client), kgcl, test_agent, aismt, shipit | about 70k |
| 11 | **C and C++ family**: c-noun-verb/typed-header, C-ABI safe-wrapper and multilang bindings, CMake/Conan | CapabilityPack | bytestar (about 150k C test/bench), autotel (about 36k), bitstar (about 32k), qlever, qlever_poc, kcura | about 230k, mostly harness boilerplate |
| 12 | **wasm-bindgen handle/export shim + TS facade pack** | CapabilityPack | wasm4pm (25k), truex (15k), miniml (5k), pm4wasm (2.5k) | about 48k |
| 13 | **Go family**: shacl-to-go-structs/proto, Cobra CLI, go test scaffold, Bazel | CapabilityPack | knowd, yaml-cloud | about 65k |
| 14 | **Extend github-actions-pack** with language presets (poetry, bun/npm publish, cargo-make), and add Docker/compose, Makefile, Prometheus/Grafana/Loki, Helm packs; extend kubernetes-workload-pack (HPA, PDB, RBAC, NetworkPolicy, Ingress) | CapabilityPack (extension) / ProfilePack | nearly every repo (workflows are the most uniformly replaceable shape); observability stack in ggen-mcp (7.5k), erlmcp, kanban | tens of thousands in CI alone |
| 15 | **Extend ggen-verify-pack / invariant-gate-pack** with repo-ops shell/Python verifier and court scripts (lock reconciliation, release-migration, consumer-court) | CapabilityPack (extension) | ggen (87k shell), clnrm (26k), swarmsh, erlmcp, ggen-ecosystem, gym-ecosystem, xaas, ggen-legacy | gap area is large (over 200k shell), covered fraction only 15-40% today |
| 16 | **Extend otel-weaver-pack** to emit Rust, Python and bash semconv constants and instrumentation | CapabilityPack (extension) | uvmgr, dslmodel, clnrm, swarmsh-v2, pm4py-rs, weavergen, kgold, mcpp | about 60k |
| 17 | **Extend readme-diataxis-pack** (rst/Sphinx and MDX targets, reference tables from RDF) | CapabilityPack (extension) | docs-heavy repos (jotp MDX 81k, many Python templates) | scaffold share only (10-30%); prose stays |
| 18 | **Migrate home-grown generators onto ggen** (not a new pack): unrdf/Nunjucks, kgn, unjucks, Weaver/Jinja, Hygen, local jgen and similar | migration (consolidate per `docs/how-to/consolidate-a-pack-family.md`) | unrdf, unjucks, kgn, dslmodel, weavergen, uvmgr, bitstar, swarmsh-v2, semantic_bit, speckit-ralph, dteam, pcp, many Hygen repos | about 50k of generator code retired |

Cross-cutting dependency: nearly every proposal needs the consumer to author SHACL/RDF first. Without a general ingest path (OpenAPI, AsyncAPI, JSON Schema, XSD, Cap'n Proto, LSP metaModel to SHACL), the "unlocked" LOC is notional. An ingest CapabilityPack (OpenAPI/XSD/AsyncAPI to SHACL) is a force multiplier for items 1, 5, 10 and 13.

### Delta decomposition (what the 94% is made of)

1. **Existing pack covers only the skeleton** (about 21% of LOC). Pack bodies are format-string echoes. The "no logic slot" limitation of clap-noun-verb, typer, fastmcp and rmcp is the biggest single reason partial coverage stays at 15-40%.
2. **Language and framework not targeted** (about 14% of LOC). The marketplace is strong on Rust catalogs, Python, Elixir/Ash, TS/shadcn/Next.js and Terraform. It is weak or empty for Java, Erlang/OTP, C/C++, Go, Vue/Nuxt/Nitro, Phoenix web, Rails, JS/citty and Swift.
3. **Irreducible logic** (about 68% of LOC): see section 4.
4. **Prose and duplication**: an unusually large share of markdown is AI-written status reports (examples: ggen-mcp 160k, knhk 780k, erlmcp 1.26M, yawl 820k markdown lines, mostly excluded from the denominators). Duplicate trees (src-backup, backup/, worktree copies, v1/v2 variants, port/ copies) inflate LOC in unjucks, un-test-utils, citty-test-utils, atman, autotel, erlmcp, neako-web, weavergen. Deletion and consolidation beat any pack here.

## 4. Irreducible residue (what stays handwritten, and why)

About 18.3M LOC (68%). Packs emit catalogs, types, routes, dispatch tables, stubs and proof tests. They do not emit behavior.

- **Engines and algorithms**: process mining and conformance (wasm4pm, pm4py-rs, ex4pm, pm4wasm, truex), SPARQL/graph/OWL engines (ggen, qlever, knowd, kcura), Petri-net and workflow engines (yawl, cre, kgcl), consensus, CRDT and sync, crypto, SIMD kernels (bytestar, autotel, bitstar, unibit, bcinr).
- **Tests with assertions**: about 30-45% of most repos (examples: bytestar C tests, wasm4pm 330k, yawl 455k, unrdf 288k, mcpp 388k). Assertions and negative witnesses encode domain intent. Packs can scaffold the shell only.
- **Handler and verb bodies behind the clap-noun-verb, typer, fastmcp and rmcp seams**.
- **LLM orchestration and agent logic** (prompt strategies, DSPy pipelines, swarm coordination).
- **Runtime and platform glue**: servers and transports, OTP supervision semantics, FFI and bindings logic, native automation (pyautomator), terminal UI engines.
- **Authored semantic source** (about 3M+ lines of Turtle, SPARQL, SHACL; 527k LOC in this repo alone). This is the pack input, not pack output. Adopting packs moves handwritten effort into RDF and does not remove it.
- **Domain data and prose**: fixtures, emoji tables, copy, tutorials, theses, specs.
- **Ad hoc one-off scripts** (fix_*.py, demo_*.py, patchers): better deleted than manufactured.
- **Formal proofs** (Lean in mfw, mfact, praxis): lean-math-pack emits skeletons only.

## 5. Caveats

- Replaceable is not replaced. No pack was run against any of these repos.
- Marketplace validation and qualification (`scripts/marketplace.py`, `qualify_packs.py`) prove structure and bounded manufacture and replay. They do not prove that generated consumer files compile, match existing behavior, or are accepted by the consumer runtime. Each adoption needs the real consumer boundary plus replay and idempotency for the exact subject (per CLAUDE.md).
- Code-as-data packs (shadcn snapshots, tcps-*, gh-terraform, platform-engineers-handbook captures) reproduce files a human already wrote. They give reproducibility, not authoring savings, and should not be counted as replacing authoring.
- Generated existence is not correctness. Workflow YAML or Terraform emitted by a pack gains no DO authority. Deploy, apply and publish stay behind BRCE or `BLOCKED:<reason>`.
- Pack coverage fractions for gap areas are judgment calls from template filenames and the capability map. Several scanners did not open template bodies.
- Per-repo LOC are estimates (wc plus sampling). Giant repos (chatman-nano-stack, bytestar, yawl, unjucks, unrdf) are the least reliable and heavily duplicated. Excluding them would shift the weighted figure but not the conclusion.
- Known measurement hazards: committed build output, vendored trees, "already generated" counted from header markers (not re-rendered), and some already-manufactured claims that are inferences (for example wasm4pm-compat tests/ui fixtures, zoeapp, beam4pm).
- Several repos already use ggen but with local templates rather than marketplace packs. Moving those onto marketplace packs is a consolidation gain, not a coverage gain.
- This report is a scan summary. It makes no Level-5 claim and no standing claim for any repo.
