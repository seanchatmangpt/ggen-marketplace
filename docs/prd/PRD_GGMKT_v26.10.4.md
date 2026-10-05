# Product Requirements Document (PRD): `ggen-marketplace` (`ggmkt`) v26.10.4

**Document ID:** PRD-GGMKT-26.10.4

**Status:** Approved & Implemented

**Date:** October 4, 2026

**Target System:** `ggen-marketplace` / `ggmkt` CLI (`superlinear-ai/substrate` wrapper)

---

## 1. Document Overview & Objective

This Product Requirements Document (PRD) defines the functional requirements, user experiences, acceptance criteria, and success metrics for **`ggen-marketplace` (`ggmkt`) v26.10.4**.

The core objective of v26.10.4 is to deliver a locked, zero-drift, enterprise-grade marketplace and orchestration engine for the **Agentic AI Foundation (AAIF)** open standards stack. It transitions the repository from experimental script execution to a production-ready system featuring an intuitive terminal user experience (`ggmkt`), mathematically verified semantic gating, and an end-to-end commercial realization loop on Google Cloud Marketplace.

---

## 2. Target Persona & User Stories

### Target Persona

* **Enterprise AI Solution Architect / Platform Engineer**: Responsible for deploying multi-agent swarms across hybrid clouds, ensuring strict regulatory and security compliance, and integrating procurement/metering systems with cloud billing.

### Key User Stories

1. **As an Architect**, I want to search and inspect marketplace packs instantly using a rich CLI (`ggmkt search` / `ggmkt info`) so I can evaluate certified agent patterns without digging through raw directories.
2. **As a Platform Engineer**, I want all generated configuration manifests (MCP, A2A, Agentgateway, Agent Router, Goose) to be mathematically validated against RDF ontologies and SPARQL gates (`ggmkt validate`) so that misconfigurations are impossible to deploy.
3. **As a Commercial Officer**, I want to simulate and execute cloud procurement and metered usage billing against Google Cloud Marketplace APIs (`ggmkt k8s-sim`) so I can prove revenue realization against committed cloud spend.

---

## 3. Functional Requirements & Feature Matrix

| Feature / Capability | Description | Priority | Verification Method |
| --- | --- | --- | --- |
| **F1. Rich CLI (`ggmkt`)** | Typer & Rich-powered CLI supporting `search`, `info`, `list`, `catalog`, `validate`, `aaif-audit`, and `k8s-sim`. | P0 (Critical) | `uv run poe test-cli` (Typer test court) |
| **F2. Semantic Pack Compiler** | Parses RDF/Turtle ontologies using `rdflib` and projects them into valid JSON, YAML, and Markdown manifests via Jinja2 templates. | P0 (Critical) | `uv run poe validate` |
| **F3. 100% AAIF Combinatorial Audit** | Automated AST and schema extraction across all 6 canonical AAIF projects enforcing strict `--fail-under 100.0`. | P0 (Critical) | `uv run poe aaif-coverage` |
| **F4. Chicago Test Court** | Rigorous test suite using real collaborators (no mocks/stubs), anti-vacuity fail witnesses, and deterministic byte-replay checks. | P0 (Critical) | `uv run poe test-court` |
| **F5. K8s GCP Marketplace Simulation** | End-to-end deployment in Kind/Colima simulating GCP Partner Procurement and Service Control metered billing. | P1 (High) | `uv run poe k8s-sim` / `uv run poe test-k8s` |

---

## 4. Non-Functional Requirements

1. **Determinism**: Manifest generation must be byte-deterministic across repeated executions to support idempotent CI/CD pipelines.
2. **Fail-Closed Security**: Any configuration violating SPARQL tripwire gates or missing required ontology properties must trigger an immediate non-zero exit status (`exit 1`).
3. **Dependency Isolation**: All execution must occur within a locked, hash-pinned Astral `uv` environment managed via `poethepoet` task automation, eliminating system-level Python environment drift.

---

## 5. Success Metrics & Acceptance Criteria

* **Combinatorial Coverage Score**: Must achieve exactly **100.0%** across all 10 standard facets spanning the 6 AAIF upstream repositories.
* **Test Court Pass Rate**: 100% of test suites (`test_aaif_vanilla_pack_court.py`, `test_k8s_gcp_marketplace_simulation.py`, `test_typer_cli.py`, `test_chicago_gcp_marketplace_indistinguishable.py`) must pass successfully.
* **Native Gate Compliance**: Repository validation must successfully evaluate all **1,828+ native gates** without error.

---

## 6. Operational Runbook (`poe` Tasks)

All execution is managed through `poethepoet` tasks pinned inside `pyproject.toml`:

```bash
# Validate all packs, ontologies, and gates
uv run poe validate

# Run 6-project combinatorial AAIF coverage audit (100.0% PASS)
uv run poe aaif-coverage

# Execute Chicago-style agent swarm test court
uv run poe test-court

# Run Typer CLI test suite (`ggmkt`)
uv run poe test-cli

# Execute live Kubernetes GCP Marketplace simulation
uv run poe k8s-sim

# Run K8s simulation test court
uv run poe test-k8s
```
