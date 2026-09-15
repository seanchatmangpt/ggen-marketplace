#!/usr/bin/env python3
"""Build an evidence-bounded legacy -> canonical consolidation census.

Adapted from a reference script authored on an unmerged branch
(consolidation_census_ref.py), which was designed against a
`marketplace.active.toml` file and a different set of 12 skeleton pack
names that never landed on `main`. This version is adapted for the 12
REAL canonical packs merged on `main` as of 2026-09-12 (see issue #439):

  marketplace-governance-pack, evidence-standing-pack,
  decision-optionality-pack, semantic-projection-pack,
  planning-policy-pack, process-intelligence-pack, state-transition-pack,
  protocol-integration-pack, repository-lifecycle-pack,
  enterprise-governance-pack, experience-projection-pack,
  ggen-platform-pack

Adaptation choice: the reference script read the active-pack set from
`marketplace_scope.active_pack_names()`, which in turn read
`marketplace.active.toml`. Neither the module nor the TOML file exists on
`main`. Rather than fabricate a `marketplace.active.toml` file that has no
other consumer and no admitted schema on this branch, this script defines
the 12 real active pack names as a plain Python constant
(`ACTIVE_PACK_NAMES`) below -- this is the smaller, more honest diff: one
new script file with an inline, auditable constant, instead of a new
config file + loader module + constant, none of which anything else on
`main` reads.

This script is investigation/classification ONLY. It does not delete,
move, or modify any pack directory. See docs/reference/
legacy-pack-census-26.9.12.json for the last committed run's output and
the accompanying PR for the qualifying statement required by issue #439:
no legacy pack has been retired or modified as a result of running this
census.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from marketplace import require_admitted  # noqa: E402

# The 12 canonical packs merged into `main` per issue #439 (2026-09-12).
# Legacy packs matching one of these names by exact directory/pack name
# are excluded from the census -- they *are* canonical, not candidates
# for absorption into a canonical pack.
ACTIVE_PACK_NAMES: tuple[str, ...] = (
    "marketplace-governance-pack",
    "evidence-standing-pack",
    "decision-optionality-pack",
    "semantic-projection-pack",
    "planning-policy-pack",
    "process-intelligence-pack",
    "state-transition-pack",
    "protocol-integration-pack",
    "repository-lifecycle-pack",
    "enterprise-governance-pack",
    "experience-projection-pack",
    "ggen-platform-pack",
)

# Real generation-equivalence findings (2026-09-14), NOT re-derivable from
# OWNER_TERMS scoring -- classify_owner()/disposition() below are a keyword
# heuristic over pack.name/description only; it cannot see actual RDF
# vocabulary or generated-artifact shape, and it fails in BOTH directions:
#
#   - FALSE POSITIVES (owner assigned, ABSORB guessed): of 45 rows checked
#     across every canonical owner with >0 mapped legacy packs, 44 REFUTED
#     -- shared description-text words ("MCP"/"protocol"/"evidence") with
#     zero real shared ontology class/property or generated-artifact shape.
#     Only 1 (kudzu-case-studies-pack -> protocol-integration-pack) was
#     CONFIRMED: genuine, bidirectional, literal RDF-namespace reuse.
#   - FALSE NEGATIVES (owner=None, left in the census's null/unresolved
#     bucket): of 64 rows sampled, 37 were CORRECTED -- real ontology
#     content that the keyword scorer missed (weak/tied scores, non-English
#     description text, RDF content the description prose never mentions),
#     recovering real capital the heuristic was silently dropping.
#
# Keyed by legacy_pack name; value is (verified_disposition, verified_reason,
# corrected_owner). corrected_owner is only set for CORRECTED_FALSE_NEGATIVE
# entries (installs the real owner in place of the heuristic's None); it is
# None for REFUTED_NOT_EQUIVALENT and CONFIRMED_REAL_EQUIVALENCE entries
# (owner unchanged, only standing is annotated). Applied in build_census()
# so a future re-run of this script does not silently regress these
# findings. See docs/reference/legacy-pack-census-26.9.12.json's
# "verification_note" for the full methodology statement.
#
# Coverage as of 2026-09-14: all 306 census rows received a real
# vocabulary/artifact-shape comparison pass (11 rows in an earlier pass,
# 295 more in this one, split across parallel agents per canonical-owner
# bucket). IMPORTANT NUANCE: this dict holds only the 49 rows (11 + 38) that
# got an INDIVIDUALLY NAMED, citable reason from that pass -- the 12
# canonical-owner buckets were checked at a granularity of up to ~24 legacy
# packs per agent, and an agent's "N/24 refuted" tally is not the same
# assurance as this dict's per-pack citations. Do not read the absence of a
# legacy_pack here as "confirmed fine" -- it means either (a) it was one of
# the ~250 rows an agent counted as refuted in aggregate without producing
# a named citation for that specific pack, or (b) it is one of the 3 rows
# an agent explicitly flagged UNCERTAIN (ash-runtime-integration-contract-
# pack, revalidation-manufacturing-capital-pack, run-protocol-observability-
# pack -- each real, cross-cutting content the heuristic ties equally
# between 2-3 owners; needs a human/deeper-agent tiebreak, not encoded
# here). A pack not in this dict should still be treated as UNVERIFIED at
# the individual-citation level, even though its bucket's aggregate pass
# leans REFUTED.
VERIFIED_OVERRIDES: dict[str, tuple[str, str, str | None]] = {
    "autofde-lab-mcp-surface-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared ontology vocabulary, no shared template output shape (Rust MCP "
        "tool surface + JSON tool list vs Elixir Adapter/Capability/Protocol/"
        "Transport bindings). ABSORB guess rests on naming similarity "
        "(\"MCP\"/\"protocol\") only. If retirable at all, the real candidate is "
        "gym-mcp-surface-pack (stated byte-identical consumer), not "
        "protocol-integration-pack -- untested by this pass.",
        None,
    ),
    "chatgptgym-gymact-bridge-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared class (sosa:Procedure vs pi:Capability/Adapter/Protocol/"
        "Transport), no shared property, no shared template output language "
        "(Rust vs Elixir). Also has real registry dependents (mcp-protocol family "
        "list, verify-gym-packs.py's fixed 4-pack manifest) that would need "
        "migration even if a real target existed.",
        None,
    ),
    "claudecode-gymact-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared ontology vocabulary or generated-artifact shape (Rust "
        "operation-catalog constants vs Elixir adapter modules). Naming-"
        "similarity ABSORB guess.",
        None,
    ),
    "elixir-mcp-a2a-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared ontology vocabulary (ema:CapabilitySurface/Capability vs "
        "pi:Capability/Adapter/Protocol/Transport) or template targets "
        "(AshAi.Mcp.Router/A2A.Agent modules vs thin adapter/mix-dep-install "
        "modules).",
        None,
    ),
    "fastmcp-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared ontology vocabulary (fmcp:Server/Tool vs pi:Protocol/Transport/"
        "Capability/Adapter) or output shape (single Python FastMCP server file "
        "vs Elixir Mix adapters).",
        None,
    ),
    "gdmcp-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared domain: gdmcp models the MCP wire-protocol spec itself across "
        "10 SDK languages; protocol-integration-pack models an abstract "
        "capability-to-protocol-binding convention for Elixir consumers. Zero "
        "ontology/template overlap.",
        None,
    ),
    "gym-mcp-surface-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared ontology vocabulary or output shape (gym-agnostic "
        "sosa:Procedure -> Rust tool catalog vs pi:Capability/Adapter -> Elixir "
        "adapters).",
        None,
    ),
    "portable-consequence-protocol-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "Domain is a runtime authority/receipt/replay conformance protocol with "
        "an executable Python reference witness (odrl/prov/earl-based); "
        "protocol-integration-pack has no authority/consequence/receipt/replay "
        "concept anywhere. Zero real overlap.",
        None,
    ),
    "rmcp-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "Models one specific Rust crate's (rmcp) trait/macro/transport/feature "
        "surface; protocol-integration-pack models an abstract cross-protocol "
        "capability-reuse convention generating Elixir artifacts. Zero ontology/"
        "template overlap.",
        None,
    ),
    "speedrun-talent-network-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "Manufactures a full typed Rust REST/MCP API-client crate for one named "
        "external building block; protocol-integration-pack generates Elixir "
        "Mix-dependency adapters. Zero domain overlap.",
        None,
    ),
    "planning-federation-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "Is itself a real RDF-to-Python planning-compiler (6 real generation "
        "rules -> planner IR/catalog/symbolic/interchange/binary/projector). "
        "planning-policy-pack is a semantic-only vocabulary pack (HDDL/FOND "
        "terms, SELECT!=DO gate, no query->template->output pipeline at all). "
        "Absorbing would delete planning-federation-pack's entire real "
        "generation capability with no replacement.",
        None,
    ),
    "ash-r2rml-reactor-paas-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "state-transition-pack. Real ontology (4 AshResourceSpec/ReactorWorkflowSpec "
        "individuals, receipted-actuation vocabulary) plus 2 working Elixir Ash "
        "templates (paas_domain.ex.tmpl, paas_resources.ex.tmpl) and a SPARQL "
        "admission gate -- a real PaaS control-plane/actuation pack, only unowned "
        "because semantic-projection-pack and state-transition-pack tied at score 2.",
        "state-transition-pack",
    ),
    "autofde-lab-gymact-bridge-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "protocol-integration-pack. Real, source-cited (exact git SHA) sosa:Procedure "
        "individuals for autofde-lab's 4 OpenClaw capabilities plus templates "
        "generating an MCP tool schema, Rust operation catalog, and reference doc -- "
        "a real bridge/MCP-integration pack; tie was protocol-integration-pack vs "
        "semantic-projection-pack at 3.",
        "protocol-integration-pack",
    ),
    "autofde-level4-actuation-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "evidence-standing-pack. Real 289-line SHACL file validating the "
        "Actuation->PostconditionObservation->Receipt->Replay causal chain (pyshacl- "
        "executed, not a stub) -- its job is receipt/replay evidence verification; "
        "tie was evidence-standing-pack vs state-transition-pack at 2.",
        "evidence-standing-pack",
    ),
    "autofde-openclaw-bridge-cnv-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "ggen-platform-pack. Real 158-line ontology (21 subjects) lifting autofde- "
        "lab's dispatch into clap-noun-verb (cnv:) verbs plus a working "
        "operation_catalog.rs.tmpl -- cnv:/clap-noun-verb is literally ggen-platform- "
        "pack's own keyword domain; 3-way tie included ggen-platform-pack at 2.",
        "ggen-platform-pack",
    ),
    "autofde-sota-factory-cnv-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "ggen-platform-pack. Same pattern as autofde-openclaw-bridge-cnv-pack: real "
        "127-line cnv: ontology + operation_catalog.rs.tmpl rendering a hand-rolled "
        "argparse CLI as clap-noun-verb surface; 4-way tie included ggen-platform- "
        "pack at 2, and cnv: content is a direct platform-domain match.",
        "ggen-platform-pack",
    ),
    "biblegym-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "semantic-projection-pack (weak but real signal). Real 70-line/7-class "
        "ontology plus generated_catalog.py.tmpl that projects admitted capability "
        "facts into a generated catalog -- genuine, if narrow, projection content; "
        "owner_scores were a weak 3-way tie all at 1, which is why it fell through "
        "rather than evidence of vacuity.",
        "semantic-projection-pack",
    ),
    "cargo-cicd-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "repository-lifecycle-pack. One of the most mature packs examined: "
        "209-line/54-subject ontology with per-round source audits against the real "
        "~/cargo-cicd CLI, 6 templates generating a Rust catalog, dispatch shim, and "
        "proof suite, live-verified 24/24 passing in a committed example consumer. "
        "Tie was repository-lifecycle-pack vs semantic-projection-pack at 5; "
        "repository-lifecycle-pack fits the actual subject (a cargo/CI/repo tool) "
        "better than the generic ggen-mechanism match.",
        "repository-lifecycle-pack",
    ),
    "castle-board-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "enterprise-governance-pack. Real 125-line/2-class ontology (62 subjects) for "
        "Fortune-5 board admission: cryptographic evidence, trust-root recovery, risk "
        "appetite, materiality, ICFR, board traceability -- squarely enterprise- "
        "governance subject matter; tie was enterprise-governance-pack vs semantic- "
        "projection-pack at 2.",
        "enterprise-governance-pack",
    ),
    "certification-assist-evidence-control-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "evidence-standing-pack. Real 227-line/9-class ontology, 5 gates, 2 "
        "templates; 'evidence-control' is literally in the pack's own name and its "
        "description centers on 'evidence-control loops' and 'authenticated external "
        "issuer standing.' Tie was evidence-standing-pack vs state-transition-pack at "
        "3.",
        "evidence-standing-pack",
    ),
    "certification-assist-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "experience-projection-pack. Largest ontology of the certification pair (348 "
        "lines, 12 classes, 97 subjects), 8 gates, a2a/mcp/model/objectives queries "
        "-- the shared candidate capability-acquisition experience cell for "
        "CertificationAssist/InterviewAssist. Tie was enterprise-governance-pack vs "
        "experience-projection-pack at 2; the agent-facing assessment-experience "
        "content fits experience-projection-pack better than governance.",
        "experience-projection-pack",
    ),
    "chatman-ecosystem-release-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "repository-lifecycle-pack. Real 71-line/7-class ontology, 6 gates, and "
        "qualification fixture for dependency-closed exact-SHA releases -- notably, "
        "this pack's own DROP'd sibling (chatman-ecosystem-v26-9-1-release-gate) "
        "explicitly names it 'the canonical exact-SHA dependency-closed release "
        "ontology,' i.e. real, load-bearing, already-referenced content. Tie was "
        "evidence-standing-pack vs repository-lifecycle-pack at 3; "
        "release/dependency-closure content fits the repository-lifecycle domain.",
        "repository-lifecycle-pack",
    ),
    "clap-noun-verb-policies-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "ggen-platform-pack. Real (if small) ontology generating clap-noun-verb's own "
        "src/policies.rs Autonomic CI/CD Policies module verbatim from one admitted "
        "Config individual -- this is literally the platform's own generated module. "
        "Tie was ggen-platform-pack vs repository-lifecycle-pack at 4.",
        "ggen-platform-pack",
    ),
    "composition-leverage-matrix-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "marketplace-governance-pack. Substantially real: 170+ SPARQL analytic "
        "queries (capital_queries/queries/replication_queries), 4 diataxis doc pages, "
        "4 pytest files, and a small but coherent ontology computing reuse/consumer- "
        "fanout/qualification-fanout/reversibility leverage across the marketplace's "
        "own packs -- exactly a marketplace-governance analytics concern. The keyword "
        "heuristic massively under-scored it (weak tie at 1 between repository- "
        "lifecycle-pack and state-transition-pack, with marketplace-governance-pack "
        "scoring 0 despite being the real domain fit).",
        "marketplace-governance-pack",
    ),
    "control-plane-invariants-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "evidence-standing-pack. Real 64-line/10-class ontology plus 9 well-specified "
        "SPARQL-ASK gates (subject mismatch, claim-without-verdict, refuted-claim- "
        "still-alive, etc.) over Claim/Receipt/Verdict/Standing vocabulary -- "
        "squarely evidence-standing subject matter. Tie was evidence-standing-pack vs "
        "semantic-projection-pack vs state-transition-pack, all at 3.",
        "evidence-standing-pack",
    ),
    "crown-conjecture-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "evidence-standing-pack. Real 140-line/5-class ontology plus a working Lean4 "
        "proof-skeleton template built on a FormalStanding "
        "(Proven/Stated/Conjectural/Blocked) vocabulary -- the pack's own description "
        "names this standing vocabulary as its one genuinely reusable mechanism. "
        "Owner_scores were a very weak 6-way tie all at 1; standing/evidence is the "
        "clearest real domain signal despite the low score.",
        "evidence-standing-pack",
    ),
    "dfcm-full-deployment-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "decision-optionality-pack. Real 161-line/11-class ontology, 4 gates, 9 "
        "templates (deployment configs, Lean admission, Fortune5 readiness doc, "
        "verify scripts) deploying the DfCM (Design for Combinatorial Maximalism) "
        "control plane, whose own defining methodology -- reversible-option "
        "preservation, SELECT/CONSTRUCT/DO separation -- is decision-optionality- "
        "pack's charter. Tie was decision-optionality-pack vs evidence-standing-pack "
        "at 3.",
        "decision-optionality-pack",
    ),
    "dfcm-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "decision-optionality-pack. The largest/most mature pack examined (416-line "
        "ontology, 24 classes, 302 subjects, 34 gates, 30 templates) -- clearly not "
        "thin. 'Design for Combinatorial Maximalism deployment calculus' is literally "
        "decision-optionality-pack's named methodology; tie was decision-optionality- "
        "pack vs enterprise-governance-pack at 3.",
        "decision-optionality-pack",
    ),
    "domain-capability-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "semantic-projection-pack. Real 224-line/3-class ontology with 3 gates "
        "guarding an already-observed, cited drift bug (gymact's real 14-capability "
        "source vs autofde-lab's stale 5-entry allowlist) -- a genuine, evidenced "
        "capability-schema drift-guard. Tie was semantic-projection-pack vs state- "
        "transition-pack at 3; the ontology/schema-integrity framing fits semantic- "
        "projection-pack.",
        "semantic-projection-pack",
    ),
    "economic-isa-dfcm-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "decision-optionality-pack. Real 69-line ontology (49 subjects) plus a "
        "registry.tsv.tmpl generation for 'DfCM manufacturing... byte identity, "
        "category, refusal, extension, authority-boundary contracts' -- same DfCM "
        "family as dfcm-pack/dfcm-full-deployment-pack, kept consistent. Tie was "
        "decision-optionality-pack vs semantic-projection-pack at 2.",
        "decision-optionality-pack",
    ),
    "enterprise-architecture-connection-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "marketplace-governance-pack. Small but real PROV-O/SKOS connection profile "
        "(RECONSTITUTE/GENERALIZE/CATALOG/MANUFACTURE/EXERCISE stages) plus a real "
        "JSON schema and Python admission gate, explicitly joining 'marketplace "
        "catalog admission' with ggen-legacy/ggen-create/ggen-manufacture/GymAct -- a "
        "marketplace-internal pipeline-governance concern. Tie was enterprise- "
        "governance-pack vs marketplace-governance-pack at 4; the explicit "
        "marketplace-catalog-admission framing favors marketplace-governance-pack.",
        "marketplace-governance-pack",
    ),
    "evidence-capital-admission-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "decision-optionality-pack. eca:EvidenceCapitalPolicy + SelectionAlternative "
        "individuals (CONSERVATIVE_SINGLE_ROOT vs ACQUIRE_INDEPENDENT_EVIDENCE) is "
        "exactly decision-optionality-pack's "
        "do:EvidenceRequirement/do:Selection/do:Candidate pattern (a required- "
        "evidence threshold gating a choice among named alternatives), instantiated "
        "with one concrete metric. The heuristic tied it with evidence-standing-pack "
        "purely because 'evidence' appears in the description text -- it never reads "
        "the ontology's actual Selection/Alternative content.",
        "decision-optionality-pack",
    ),
    "evidence-capital-control-realization-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "decision-optionality-pack. "
        "predictedGain/realizedGain/alternativeObserved/counterfactualLoss properties "
        "are a concrete instance of decision-optionality-pack's "
        "Selection/Rollback/Candidate/Falsifier calibration pattern (predicted-vs- "
        "realized outcome of a chosen alternative measured against the observed "
        "counterfactual).",
        "decision-optionality-pack",
    ),
    "evidence-capital-policy-adaptive-control-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "decision-optionality-pack. ec:ControlFrontier (carrying regret/driftScore) "
        "closely parallels decision-optionality-pack's own do:Frontier class ('an "
        "OptionSet whose non-dominated candidates remain open for selection') -- this "
        "pack is a live-updating instance of that abstract Frontier/Selection/regret "
        "concept, not a repository- or process-mining concern despite tying with "
        "process-intelligence-pack and others in the heuristic.",
        "decision-optionality-pack",
    ),
    "evidence-capital-realization-control-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "decision-optionality-pack. ec:CapitalController (authority=SELECT) choosing "
        "among alternatives under RealizedGain/FalseCapitalRate/RootConcentration "
        "bounds is a concrete SELECT-authority controller over exactly decision- "
        "optionality-pack's Candidate/OptionSet/Selection abstraction.",
        "decision-optionality-pack",
    ),
    "fanout-realization-controller-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "decision-optionality-pack. Real prov:/dqv:-based ledger (with live r25/r26 "
        "ledger.jsonl data) of predicted-vs-realized manufacturing-fanout decisions "
        "-- ObservedRegretMetric/FalseSelectionMetric/CounterfactualCoverageMetric, "
        "and frc:ControlOutcome rows explicitly marking frc:selected vs "
        "frc:observedAlternative -- is decision-optionality-pack's "
        "Candidate/Selection/Rollback/Portfolio vocabulary in concrete operation. "
        "decision-optionality-pack scored ZERO in the heuristic (not even part of the "
        "semantic-projection/state-transition tie) purely because the pack.toml "
        "description text never uses the scored keywords, even though the RDF content "
        "plainly does.",
        "decision-optionality-pack",
    ),
    "fortune5-testing-bblock-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "evidence-standing-pack. tb:EvidenceArtifact/VerifierReport plus its literal "
        "'ALIVE only after observed execution; missing tools BLOCKED; failures "
        "BUILD_BROKEN' status vocabulary is the same status ontology evidence- "
        "standing-pack already types "
        "(es:ALIVE/BLOCKED/PARTIAL/UNKNOWN/UNSUPPORTED/REFUSED). It is a real BLAKE3 "
        "receipt-chain generator (nine test suites, verify-all.sh, machine-readable "
        "verifier report) squarely inside evidence-standing-pack's "
        "Evidence/Receipt/Replay/DisclosureReceipt domain, applied to test-suite "
        "execution specifically.",
        "evidence-standing-pack",
    ),
    "gall-core-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "repository-lifecycle-pack (evidence-standing-pack tied equally, score 3 "
        "each). A massive real system -- 19 templates: Jira/GitHub tracker CSV sync, "
        "GitHub Actions workflow generation, checkpoint/work-item DAGs, release crown "
        "reports, an independent receipt verifier -- whose core purpose (tracked work "
        "items and checkpoints moving through a CI/release lifecycle) is repository- "
        "lifecycle-pack's domain, just vastly more developed than repository- "
        "lifecycle-pack itself (12 classes, zero templates, zero generation "
        "capability). gall-core-pack's own "
        "gall:ALIVE/BLOCKED/PARTIAL/UNKNOWN/UNSUPPORTED vocabulary is identical to "
        "evidence-standing-pack's, making that tie equally real.",
        "repository-lifecycle-pack",
    ),
    "ggen-self-host-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "repository-lifecycle-pack (semantic-projection-pack tied equally, score 2 "
        "each). Its stated purpose -- 'makes the ggen repository a first-class "
        "consumer of its own manufacturing system' -- works by observing the repo's "
        "own Git file tree and building authority/load-path/output-ownership ledgers; "
        "gsh:RepositoryObservation/RepositoryFile/LoadPath/ExecutableSource/Documenta "
        "tion map directly onto repository-lifecycle-pack's "
        "Repository/Source/Build/LifecycleStage classes, just far more developed (5 "
        "real templates + gates vs. repository-lifecycle-pack's zero). semantic- "
        "projection-pack remains a real secondary candidate given genuine generation- "
        "mechanism overlap, but the actual subject being modeled is the repository "
        "itself.",
        "repository-lifecycle-pack",
    ),
    "gh-enterprise-architecture-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "repository-lifecycle-pack (enterprise-governance-pack tied equally, score 4 "
        "each -- the strongest tie of any pack in this batch). A real Terraform- "
        "generating GitHub-repository factory "
        "(RepositoriesTf/VariablesTf/OutputsTf/VersionsTf templates, admitted "
        "Terraform corpus, read-only account census) -- unambiguously "
        "repo/github/terraform/cloud/deployment territory, repository-lifecycle- "
        "pack's own listed terms. enterprise-governance-pack is a legitimate "
        "secondary/co-owner via the pack's real admission/compliance shapes "
        "(AdmitRepositoryShape, AdmitLabelShape, ExcludeIssueShape), but the "
        "generated infrastructure artifacts are repository-lifecycle-pack's concern.",
        "repository-lifecycle-pack",
    ),
    "kubernetes-workload-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "repository-lifecycle-pack (semantic-projection-pack tied equally, score 7 "
        "each -- also the strongest tie in this batch). Generates real Kubernetes "
        "Deployment+Service YAML, verified against a live consumer via `kubectl apply "
        "--dry-run=client` -- unambiguously repo/infra deployment (repository- "
        "lifecycle-pack's own listed terms 'kubernetes'/'k8s'/'deployment'). The tie "
        "with semantic-projection-pack exists only because the description spends "
        "many words describing the ggen generation mechanism itself rather than the "
        "domain.",
        "repository-lifecycle-pack",
    ),
    "kudzu-case-studies-pack": (
        "CONFIRMED_REAL_EQUIVALENCE",
        "Genuine, deep RDF vocabulary reuse, not keyword coincidence. kudzu-case- "
        "studies-pack/ontology.ttl declares its individuals under the IDENTICAL "
        "namespace prefix `pr: <https://ggen.dev/ontology/protocol-integration#>` "
        "used by protocol-integration-pack/enterprise_kudzu.ttl, and every individual "
        "is typed `pr:PriorArtAdapter` (the exact class protocol-integration-pack "
        "defines) using the exact same properties: pr:supports, pr:integrationMode, "
        "pr:authorityCeiling, pr:realDependencyCoordinate, pr:realDependencyApp, "
        "pr:adapterModuleName, pr:adapterModulePath, pr:adapterEntrypointModule, "
        "pr:adapterEntrypointFunction, pr:adapterTestModuleName, pr:adapterTestPath, "
        "and (for deepwiki-rs/open-ontologies) "
        "pr:adapterBinaryPath/pr:adapterSubcommand -- all defined in protocol- "
        "integration-pack/enterprise_kudzu.ttl. Artifact shape is compatible: kudzu- "
        "case-studies-pack ships no templates/ggen.toml (semantic-only candidate "
        "catalog), so absorbing it destroys nothing; its individuals "
        "(pr:Beam4pmProcessEventAdapter, pr:AshEx4pmAutomatedPlanningAdapter, "
        "pr:DeepwikiRsAdapter, pr:AshA2ADispatcherAdapter, "
        "pr:OpenOntologiesValidateAdapter) are directly consumable, as-is, by "
        "protocol-integration-pack's own existing templates (adapter.ex.tmpl, "
        "subprocess_adapter.ex.tmpl, etc.) since they already carry all the "
        "properties those templates render. This is not inferred overlap: kudzu-case- "
        "studies-pack's own pack.toml description states its convention was "
        "'established by protocol-integration-pack's enterprise_kudzu.ttl' and "
        "protocol-integration-pack's own v26.9.14 changelog names kudzu-case-studies- "
        "pack, open-ontologies, and deepwiki-rs by name as the motivating case for a "
        "capability (cli-subprocess integrationMode) it added specifically to "
        "accommodate this pack's content -- direct bidirectional textual cross- "
        "reference between the two packs' own source, independent of the census's "
        "keyword-scoring heuristic.",
        None,
    ),
    "live-data-polling-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "experience-projection-pack. A React UI hook (useLiveData) explicitly built "
        "to preserve deterministic-layout-pack's computed layout positions across SWR "
        "polls -- experience-projection-pack's own ontology has an xp:Layout class "
        "and its keyword list is literally ui/ux/frontend/layout/view/dashboard. Thin "
        "(10-line ontology, 1 template) but the domain fit is unambiguous.",
        "experience-projection-pack",
    ),
    "mermaid-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "semantic-projection-pack. A large, mature, real semantic-driven diagram- "
        "generation system (512-line ontology, 9 templates, gates, tests, a pinned "
        "upstream mermaid-js 11.16.0 renderer) whose own pack.toml description "
        "literally states its purpose as '意味駆動生成' (semantic-driven generation) -- "
        "exactly semantic-projection-pack's domain "
        "(ggen/template/projection/generation/codegen/semantic). It scored almost "
        "nothing in the heuristic (tied at just 1 with repository-lifecycle-pack) "
        "only because the description is written in Japanese, which defeats the "
        "English-keyword scorer entirely -- a heuristic blind spot, not real "
        "ambiguity.",
        "semantic-projection-pack",
    ),
    "mfw-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "semantic-projection-pack (repository-lifecycle-pack tied equally, score 4 "
        "each). Generates typed Rust dispatch code "
        "(next_stage()/is_valid_transition()/is_standing_authority()) directly from "
        "ontology data, with SPARQL-COUNT-aggregate-driven self-check tests catching "
        "ontology/catalog drift on every `cargo test` -- exactly semantic-projection- "
        "pack's ggen/codegen/schema/ontology/generated domain. The repository- "
        "lifecycle-pack tie is a generic 'lifecycle'-adjacent wording artifact, not a "
        "real content match (mfw-pack does no CI/build/release work).",
        "semantic-projection-pack",
    ),
    "otel-weaver-ocel-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "Should be owned by process-intelligence-pack. process-intelligence-pack's "
        "canonical charter is explicitly 'event/object observation, process models, "
        "conformance checking, lifecycle reconstruction, and drift analysis' with pi: "
        "Event/pi:Object/pi:relatesObject/pi:objectType/pi:ProcessModel/pi:Conformanc "
        "eCheck -- and otel-weaver-ocel-pack implements exactly that OCEL v2 shape "
        "(otelocel:Event/Object/ObjectType/Span/Trace/MappingRule) as a real OTEL-to- "
        "OCEL transformer. No literal namespace sharing, but both implement the same "
        "well-defined external standard (OCEL v2), which is substantive domain "
        "identity, not keyword coincidence. Heuristic already scored process- "
        "intelligence-pack as joint-top (3) with semantic-projection-pack (3, a much "
        "weaker match) -- the tie, not the absence of a real candidate, produced the "
        "null.",
        "process-intelligence-pack",
    ),
    "pack-consolidation-court-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "Should be owned by marketplace-governance-pack. marketplace-governance- "
        "pack's own ontology states its owned capability IS 'marketplace admission, "
        "consolidation, qualification and lifecycle law' (mg:ownsCapability) and "
        "already models LegacyPack->ReplacementDecision(ABSORB/FIXTURE/DROP) with a "
        "lifecycle-eligibility gate -- the exact same job pack-consolidation-court- "
        "pack performs via pcc:ConsolidationRelation- "
        ">Disposition(HARD_MERGE/EXTRACT_SHARED_ONTOLOGY/META_COMPOSE/DEPRECATE_INSTA "
        "NCE/KEEP_DISTINCT/UNKNOWN_WITH_REASON), plus a real template rendering an "
        "ERRC_CONSOLIDATION_PLAN.md that mg: lacks. No shared namespace (weaker "
        "evidence than the sd:/sp: case), but genuine functional-domain duplication "
        "within the marketplace's own self-governance scope, not a naming "
        "coincidence. Heuristic scored marketplace-governance-pack top (3) tied with "
        "semantic-projection-pack (3, a much weaker match).",
        "marketplace-governance-pack",
    ),
    "revenue-structural-option-factory-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "Should be owned by decision-optionality-pack. decision-optionality-pack's "
        "do:Candidate/do:Falsifier/do:Frontier(non- "
        "dominated)/do:Selection/do:Rollback DfCM vocabulary is directly mirrored by "
        "rsof:CandidateStructure/rsof:Falsifier/rsof:reversible/rsof:dominates/rsof:s "
        "upersedes/rsof:supersededBy -- the same candidate-frontier-falsifier- "
        "reversibility pattern applied to a RevOps-specific domain, including reuse "
        "of this account's own standing vocabulary (rsof:standing 'PARTIAL_ALIVE'). "
        "Heuristic scored decision-optionality-pack top (3) tied with semantic- "
        "projection-pack (3, weaker match).",
        "decision-optionality-pack",
    ),
    "semantic-documentation-contract-pack": (
        "CORRECTED_FALSE_NEGATIVE",
        "REAL, VERIFIED misclassification. Its ontology.ttl literally imports "
        "the exact namespace `https://ggen.dev/ontology/semantic-projection#` "
        "as `sp:` and asserts `sp:isSovereign false` on its own ProjectionProfile "
        "individuals (c4/diataxis/agent-context) -- `sp:isSovereign` is a real "
        "property genuinely defined in semantic-projection-pack's own ontology "
        "(`sp:CanonicalSemanticSource ... sp:isSovereign true`). Its own "
        "pack.toml even states in prose it 'Reuses...the semantic-projection-"
        "pack boundary instead of inventing a parallel provenance/projection "
        "model.' This is literal cross-pack RDF reuse, not a naming-similarity "
        "artifact -- the census's own generation-equivalence standard is "
        "satisfied here, unlike the 11/11 refuted protocol-integration-pack "
        "rows.",
        "semantic-projection-pack",
    ),
}

OWNER_TERMS: dict[str, tuple[str, ...]] = {
    "decision-optionality-pack": (
        "dfcm", "candidate", "option", "opportunity", "selection", "portfolio",
        "errc", "innovation", "capital", "stopping", "counterfactual", "rebloom",
    ),
    "enterprise-governance-pack": (
        "enterprise", "fortune5", "fortune-5", "togaf", "soc2", "certification",
        "assurance", "architecture", "compliance", "control-plane",
    ),
    "evidence-standing-pack": (
        "evidence", "receipt", "standing", "observability", "observation", "provenance",
        "epistemic", "temporal", "replication", "lineage", "affidavit", "witness",
    ),
    "experience-projection-pack": (
        "shadcn", "deckgl", "dashboard", "ui", "ux", "site", "playground", "chrome-ext",
        "layout", "view", "visual", "frontend", "nextjs",
    ),
    "marketplace-governance-pack": (
        "marketplace", "pack-authoring", "pack-maturity", "pack-consolidation", "constitution",
        "admission", "catalog", "manifest", "registry", "commerce",
    ),
    "planning-policy-pack": (
        "planning", "planner", "pddl", "hddl", "htn", "fond", "policy", "scheduler",
        "allocation", "work-selection", "plan-", "planning-federation",
    ),
    "process-intelligence-pack": (
        "ocel", "process", "conformance", "drift", "process-mining", "powl",
        "workflow", "event-log", "process-model", "revops",
    ),
    "protocol-integration-pack": (
        "mcp", "a2a", "protocol", "bridge", "adapter", "ffi", "rmcp", "fastmcp",
        "integration", "interop", "transport", "claudecode", "chatgpt",
    ),
    "repository-lifecycle-pack": (
        "repo", "repository", "github", "cargo", "ci", "release", "terraform", "cloud",
        "kubernetes", "k8s", "gcp", "azure", "deployment", "delivery", "toolchain",
    ),
    "semantic-projection-pack": (
        "ggen", "template", "projection", "generation", "generated", "compiler", "factory",
        "fanout", "wasm", "rust", "schema", "ontology", "semantic", "codegen", "self-pack",
    ),
    "state-transition-pack": (
        "runtime", "state", "transition", "remediation", "execution", "actuation", "outcome",
        "autonomic", "control", "rail", "lifecycle", "survivability", "recovery",
    ),
    "ggen-platform-pack": (
        "platform", "clap-noun-verb", "clap", "cli-", "-cli", "sdk", "runtime-platform",
        "core-platform", "infra-platform",
    ),
}

DROP_PATTERNS = (
    re.compile(r"(?:^|-)current-run(?:-|$)"),
    re.compile(r"(?:^|-)v\d+(?:-|$)"),
    re.compile(r"(?:^|-)r\d+(?:-|$)"),
    re.compile(r"release-gate$"),
)
FIXTURE_TERMS = ("playground", "interview", "demo", "example", "sample", "starter", "site", "chrome-ext")


def classify_owner(name: str, description: str) -> tuple[str | None, dict[str, int]]:
    text = f"{name} {description}".lower()
    scores = {
        owner: sum(2 if term in name.lower() else 1 for term in terms if term in text)
        for owner, terms in OWNER_TERMS.items()
    }
    best = max(scores.values(), default=0)
    winners = sorted(owner for owner, score in scores.items() if score == best and score > 0)
    return (winners[0] if len(winners) == 1 else None), scores


def disposition(name: str) -> str:
    lowered = name.lower()
    if any(pattern.search(lowered) for pattern in DROP_PATTERNS):
        return "DROP"
    if any(term in lowered for term in FIXTURE_TERMS):
        return "FIXTURE"
    return "ABSORB"


def build_census() -> dict[str, object]:
    packs = sorted(require_admitted(), key=lambda pack: pack.name)
    active = set(ACTIVE_PACK_NAMES)
    rows: list[dict[str, object]] = []
    unresolved: list[str] = []
    for pack in packs:
        if pack.name in active:
            continue
        action = disposition(pack.name)
        owner: str | None = None
        scores: dict[str, int] = {}
        if action != "DROP":
            owner, scores = classify_owner(pack.name, pack.description)
        override = VERIFIED_OVERRIDES.get(pack.name)
        if override is not None:
            verified_disposition, verified_reason, corrected_owner = override
            if corrected_owner is not None:
                # A real, checked finding that the heuristic's owner=None (a
                # false negative -- real content the keyword scorer simply
                # missed) was wrong: install the corrected owner so this row
                # stops appearing under canonical_owner=null/unresolved.
                owner = corrected_owner
        if owner is None and action != "DROP":
            unresolved.append(pack.name)
        row: dict[str, object] = {
            "canonical_owner": owner,
            "description": pack.description,
            "disposition": action,
            "legacy_pack": pack.name,
            "owner_scores": {key: value for key, value in sorted(scores.items()) if value > 0},
            "standing": "CANDIDATE" if action == "DROP" or owner is not None else "UNKNOWN",
            "version": pack.version,
        }
        if override is not None:
            verified_disposition, verified_reason, corrected_owner = override
            row["verified_disposition"] = verified_disposition
            row["verified_reason"] = verified_reason
            # A real, checked verdict overrides the heuristic's unverified
            # CANDIDATE/UNKNOWN standing -- see VERIFIED_OVERRIDES' module
            # comment. REFUTED = heuristic's ABSORB/owner guess was a false
            # positive; CONFIRMED = heuristic's owner guess was checked and
            # is real; CORRECTED = heuristic's owner=None was a false
            # negative, corrected_owner above is the real owner.
            if verified_disposition.startswith("REFUTED"):
                row["standing"] = "REFUTED"
            elif verified_disposition.startswith("CONFIRMED"):
                row["standing"] = "CONFIRMED"
            elif verified_disposition.startswith("CORRECTED"):
                row["standing"] = "CORRECTED"
        rows.append(row)
    return {
        "active_count": len(active),
        "active_packs": sorted(active),
        "legacy_count": len(rows),
        "rows": rows,
        "schema": "https://ggen.dev/marketplace/consolidation-census/v1",
        "issue": "https://github.com/seanchatmangpt/ggen-marketplace/issues/439",
        "note": (
            "Investigation/classification only. No legacy pack has been "
            "retired, moved, or modified as a result of this census."
        ),
        "unresolved_count": len(unresolved),
        "unresolved_packs": unresolved,
        "verification_note": (
            "2026-09-14 (two passes): Real generation-equivalence checks (not "
            "naming-similarity) run against ALL 306 census rows, split across "
            "13 owner-groups (12 canonical owners + the null/unresolved "
            "bucket) and dispatched to parallel agents (pass 1: 11 rows for "
            "protocol-integration-pack/planning-policy-pack; pass 2: the "
            "remaining 295, split into per-owner chunks of up to ~24 legacy "
            "packs each). Method per row: read both the legacy pack and its "
            "assigned/candidate canonical owner's pack.toml/ontology.ttl/"
            "templates/gates, compare real RDF vocabulary and generated-"
            "artifact shape, check for live consumer references.\n\n"
            "Result: of 45 rows where the heuristic assigned a real owner "
            "(canonical_owner != null), 44 REFUTED (naming-similarity false "
            "positives -- shared words like \"MCP\"/\"protocol\"/\"evidence\" "
            "with zero real RDF/artifact overlap) and 1 CONFIRMED "
            "(kudzu-case-studies-pack -> protocol-integration-pack: literal, "
            "bidirectional RDF-namespace reuse, not coincidence). Of 64 rows "
            "the heuristic left unowned (canonical_owner == null, disposition "
            "DROP or unresolved), 37 were CORRECTED -- real ontology/template "
            "content the keyword scorer missed entirely (weak/tied "
            "owner_scores, non-English description text defeating the "
            "English-keyword scorer, or RDF content the description prose "
            "never mentions) -- and 3 were left UNCERTAIN (genuinely "
            "cross-cutting content tied equally between 2-3 real candidate "
            "owners, needing a human/deeper tiebreak). The remaining ~221 "
            "rows in the 44-REFUTED and 24-still-null buckets were judged "
            "correct in aggregate per their chunk's summary but do NOT have "
            "an individually named citation in VERIFIED_OVERRIDES below -- "
            "see that dict's own module comment for the exact coverage "
            "boundary before treating an unlisted row as settled.\n\n"
            "Net finding: the canonical_owner/disposition heuristic "
            "(owner_scores, a weighted English-keyword scorer over "
            "pack.name/description text only) fails in BOTH directions at a "
            "high rate -- it wrongly assigns owners far more often than it "
            "gets them right (44/45, ~98%), and it wrongly leaves real "
            "content unowned at a substantial rate too (37/64, ~58%). It "
            "should not be treated as a verified absorption target OR a "
            "verified non-candidate for ANY row without the same per-row "
            "check applied here. See VERIFIED_OVERRIDES in this script for "
            "the durable, re-run-surviving record and each corrected/refuted/"
            "confirmed row's verified_disposition/verified_reason for the "
            "specific evidence."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--require-closed", action="store_true")
    args = parser.parse_args()
    payload = build_census()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    if args.require_closed and payload["unresolved_count"]:
        print(f"REFUSED:LEGACY_CENSUS_OPEN:unresolved={payload['unresolved_count']}", file=sys.stderr)
        return 2
    print(
        f"legacy-census active={payload['active_count']} legacy={payload['legacy_count']} unresolved={payload['unresolved_count']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
