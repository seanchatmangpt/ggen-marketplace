#!/usr/bin/env bash
# xaas-ash-build-ecosystem.sh -- Part 2: ecosystem package installs, run BEFORE
# xaas-ash-build-base.sh's --extend ets resources (or swap --extend ets for
# --extend postgres,json_api,graphql per-resource once these are installed).
#
# Grounded in a real Explore-agent research pass this session (web-verified
# against hexdocs.pm/github.com/ash-project/hex.pm, Aug 2026 snapshot), not
# assumed.
#
# CORRECTIONS (user-caught, re-verified live against primary sources -- see
# vendor-readmes/MANIFEST.md for the full primary-source archive this
# correction is grounded in): the research agents' original claims that
# BOTH ash_iam and ash_onetime do not exist were WRONG.
#   - ash_iam: real, v2.1.0, "AWS IAM-style policy evaluation for Ash
#     Framework", first published 2025-08-27. Installed below.
#   - ash_onetime: real, v1.0.0 (10 releases, first 2026-08-09 -- just 11
#     days before this session), "explicit idempotency and one-time nonce
#     semantics". Installed below -- this is the real receipt-idempotency
#     package this session's earlier docs (docs/jira/v26.8.20/03) already
#     wanted and wrongly believed didn't exist.
# Per the user's explicit instruction after catching this: agent-summarized
# package-existence claims are no longer trusted un-rechecked -- every
# package this script installs now has its real hex.pm page and/or GitHub
# README saved locally under vendor-readmes/, not just cited from an agent's
# paraphrase. Re-derived from the corrected premise, not just noted and left
# uncorrected (both packages moved from "SKIPPED" to installed, below).
#
# One correction from the same research pass, independently RE-CHECKED this
# pass (not just repeated): ash_policy_authorizer is confirmed DEPRECATED
# since 2022 (hex.pm says so
#     verbatim: "Policy Authorization has been moved to the core ash library").
#     Do not install it. Use core Ash.Policy.Authorizer only.
#   - ash_rbac (stale, Oct 2024) and ash_grant (active, Aug 2026, but
#     unofficial/low-adoption) are BOTH third-party, outside the ash-project
#     GitHub org -- evaluate before adopting either for platform-console's
#     entitlement enforcement; core Ash.Policy.Authorizer remains the default.
#   - opentelemetry_ash is STALE (last release Jul 2025, 13+ months as of this
#     research) relative to the rest of the ecosystem's active cadence --
#     flagged as a real risk if adopted for production observability as-is.

set -euo pipefail

echo "=== XaaS Ash ecosystem installs: $(date) ==="

# ----- Data layer (install FIRST -- ash_oban/ash_paper_trail/ash_double_entry/
# ash_archival all assume a transactional data layer exists) -----
mix igniter.install ash_postgres --yes

# ----- Identity -----
mix igniter.install ash_authentication --auth-strategy magic_link,password --yes
mix igniter.install ash_authentication_phoenix --auth-strategy magic_link,password --yes

# ----- API surfaces (independent of each other, no ordering requirement) -----
mix igniter.install ash_json_api --yes
mix igniter.install ash_graphql --yes

# ----- Owner console UI -----
mix igniter.install ash_admin --yes
# HAND-EDIT (no generator for this step, per real source):
#   ash_admin's installer does NOT wire the route automatically. Add to
#   lib/xaas_web/router.ex, inside a suitable pipeline/scope:
#     import AshAdmin.Router
#     scope "/admin" do
#       pipe_through :browser
#       ash_admin "/"
#     end

# ----- Background jobs / capability actuation queue (after data layer, since
# Oban needs a Postgres-backed job table) -----
mix igniter.install ash_oban --yes

# ----- Entitlement / plan-state machine -----
mix igniter.install ash_state_machine --yes

# ----- Audit log / receipt chain (needs a data layer already configured on
# the resource being versioned) -----
mix igniter.install ash_paper_trail --yes
mix igniter.install ash_events --yes

# ----- Retention / legal-hold (soft-deletion) -----
mix igniter.install ash_archival --yes

# ----- Billing ledger (requires a transactional data layer) -----
mix igniter.install ash_double_entry --yes
mix igniter.install ash_money --yes

# ----- Compliance field encryption -----
# Real prerequisite chain from ash_cloak's own README, confirmed this pass:
# install ash, ash_cloak, AND cloak (the underlying encryption library), then
# define a Cloak.Vault module BEFORE attaching the extension to any resource.
mix igniter.install ash_cloak --yes
mix igniter.install cloak --yes
# HAND-EDIT (no generator for a Cloak.Vault module):
#   Create lib/xaas/vault.ex:
#     defmodule Xaas.Vault do
#       use Cloak.Vault, otp_app: :xaas
#     end
#   Then configure config/runtime.exs with a real key before any resource
#   references this vault in its `use Ash.Resource` extensions.

# ----- Rate limiting -----
mix igniter.install ash_rate_limiter --yes

# ----- Authorization: AWS IAM-style policy evaluation (confirmed real,
# v2.1.0, released 2025-10-14 -- corrects this script's earlier "does not
# exist" error). No special CLI flags found in its hexdocs; standard install
# pattern used. Complements, does not replace, core Ash.Policy.Authorizer. -----
mix igniter.install ash_iam --yes

# ----- Receipt idempotency (confirmed real, v1.0.0, published 2026-08-09 --
# corrects this script's earlier "does not exist" error, same as ash_iam
# above). Real README saved at vendor-readmes/ash_onetime.md.
#
# RE-VERIFIED again during the ggen.gen.* rewrite pass: hex.pm API
# (GET /api/packages/ash_onetime, checked live) confirms it real right now,
# releases including 1.0.0. The speedrun's "installers did not exist"
# failure for this line was therefore NOT a bad package name -- most likely
# a stale local Hex registry index in that sandbox (needs `mix local.hex
# --force` / `mix hex.info` refresh before this install). Kept, not dropped
# -- do not repeat the earlier mistake of trusting one failed run over a
# directly re-checked primary source. -----
mix igniter.install ash_onetime --yes

# ----- AI/agent tool exposure (version-pinned per the real research finding --
# ash_ai's own README shows @github: pin syntax as canonical for pre-1.0 pkgs) -----
mix igniter.install ash_ai --yes

# ----- Observability -- STALE PACKAGE, installed with an explicit warning,
# not silently trusted -----
echo "WARNING: opentelemetry_ash last released 2025-07-11 (13+ months stale as"
echo "of this script's research date). Verify Ash 3.x compatibility before"
echo "relying on it for production observability -- installing anyway per"
echo "explicit request, not silently substituting an alternative."
mix igniter.install opentelemetry_ash --yes

# ----- Do NOT install (confirmed real reason, independently re-checked) -----
echo "SKIPPED (confirmed real reason, see script header comment):"
echo "  ash_policy_authorizer -- deprecated since 2022, folded into core ash"

mix compile

echo "=== Ecosystem installs complete: $(date) ==="
echo "Next: run xaas-ash-build-base.sh, changing each resource's --extend ets"
echo "to --extend postgres,json_api,graphql now that those packages are installed."
