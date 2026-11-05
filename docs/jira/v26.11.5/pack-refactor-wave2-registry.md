# Pack Refactor Wave 2 — 18 lanes (2026-11-05)

Standing: IN-FLIGHT. House pattern per shadcn v0.2.0 / F1-F3 precedent:
Measure → [consumer_contract] (deps derived mechanically from template
imports) → README (contract + court description) → version bump →
scratch-consumer court with anti-vacuity flip → receipt.

Rules: one pack per lane, disjoint ownership; kafka-wire-pack + the four
cmms-referenced packs (shacl-projection, shacl-to-zod, supabase,
shadcn-ui-primitives) are FENCED — do not touch. Toolchain absence =
typed UNVERIFIED, never fake-pass. Elixir/Rust courts: run if mix/cargo
exist on PATH (`command -v` guard), else record the toolchain gap.

| Lane | Pack |
|---|---|
| G01 | nextjs-ai-sdk-pack |
| G02 | ai-chatbot-shadcn-pack |
| G03 | nextjs-ai-sdk-ui-shadcn-pack |
| G04 | jotp-benchmark-site-shadcn-pack |
| G05 | nextjs-mcp-a2a-pack |
| G06 | semantic-fullstack-factory-pack |
| G07 | shacl-to-fastapi-pack |
| G08 | shacl-to-pydantic-pack |
| G09 | sa2a-fastapi-pack |
| G10 | canonical-ash-projection-generator |
| G11 | ash-pplan-igniter-pack |
| G12 | dspy-pack |
| G13 | fastmcp-pack |
| G14 | typer-azure-pack |
| G15 | github-actions-pack |
| G16 | cargo-cicd-pack |
| G17 | rmcp-pack |
| G18 | gh-terraform-pack |

Cross-lane hazards (from F4's census, each lane must check its own pack):
shared/duplicated helper templates (lib/utils.ts is projected by G03 and
G04 today — do NOT change its body; single-sourcing is a later wave);
identical-hash templates shared across packs (G02/G04 lockstep).
Receipts: docs/jira/v26.11.5/receipts/G{01..18}.md
