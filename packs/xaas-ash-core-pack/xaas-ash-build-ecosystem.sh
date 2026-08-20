#!/usr/bin/env bash
# xaas-ash-build-ecosystem.sh -- Part 2: ecosystem package installs.
#
# Package choices are grounded in the archived primary-source READMEs under
# vendor-readmes/. Prefer each package's own Igniter installer when one exists;
# use `igniter.add` only to make a dependency available before invoking a
# package-specific installer directly.

set -euo pipefail

echo "=== XaaS Ash ecosystem installs: $(date) ==="

# ----- Data layer -----
mix igniter.install ash_postgres --yes

# ----- Identity -----
mix igniter.install ash_authentication --auth-strategy magic_link,password --yes
mix igniter.install ash_authentication_phoenix --auth-strategy magic_link,password --yes

# ----- API surfaces -----
mix igniter.install ash_json_api --yes
mix igniter.install ash_graphql --yes

# ----- Owner console UI -----
mix igniter.install ash_admin --yes
# HAND-EDIT: ash_admin does not wire the route automatically.

# ----- Background jobs -----
mix igniter.install ash_oban --yes

# ----- State machine -----
mix igniter.install ash_state_machine --yes

# ----- Audit / replay -----
mix igniter.install ash_paper_trail --yes
mix igniter.install ash_events --yes

# ----- Retention / archival -----
mix igniter.install ash_archival --yes

# ----- Billing / money -----
mix igniter.install ash_double_entry --yes
mix igniter.install ash_money --yes

# ----- Field encryption -----
mix igniter.install ash_cloak --yes
mix igniter.install cloak --yes
# HAND-EDIT: define Xaas.Vault and runtime key configuration before use.

# ----- Rate limiting -----
mix igniter.install ash_rate_limiter --yes

# ----- IAM-style policy evaluation -----
mix igniter.install ash_iam --yes

# ----- Receipt idempotency / one-time nonce admission -----
# Confirmed real (v1.0.0, re-checked live against the hex.pm API during the
# ggen.gen.* rewrite pass, not just the archived README). Root cause of the
# speedrun's "installers did not exist" failure, resolved by a parallel
# session cross-checking the package's own README: ash_onetime documents
# `mix ash_onetime.install` as its canonical installer task, distinct from
# the generic `mix igniter.install ash_onetime` this script used to invoke
# (which never resolved the task in the target project). Add the dependency
# first, then invoke the package-specific task exactly as documented.
mix igniter.add ash_onetime
mix ash_onetime.install

# ----- AI / agent tool exposure -----
mix igniter.install ash_ai --yes

# ----- Observability -----
echo "WARNING: opentelemetry_ash is retained as an explicitly qualified dependency;"
echo "verify compatibility with the pinned Ash runtime before production reliance."
mix igniter.install opentelemetry_ash --yes

# ----- Explicitly excluded -----
echo "SKIPPED: ash_policy_authorizer -- deprecated; use core Ash.Policy.Authorizer"

mix compile

echo "=== Ecosystem installs complete: $(date) ==="
