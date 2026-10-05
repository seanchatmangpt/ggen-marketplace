#!/bin/sh
# Pre-v1.0 wire-shape gate (2026-10-04): the generated templates must not
# emit wire shapes the landed ash_a2a v1.0 surface replaced. Scanned tokens
# and their real v1.0 replacements, each cited from /Users/sac/ash_a2a:
#
#   A2A.<Module>   external pre-v1.0 protocol-library module refs
#                  -> `use AshA2A.Protocol.Agent, ...` / AshA2A.Agent
#                     (lib/ash_a2a/protocol/agent.ex, lib/ash_a2a/agent.ex)
#   kind: / "kind" legacy per-frame discriminator key -> v1.0 status-update
#                  frames carry none (lib/ash_a2a/protocol/event.ex:20-27)
#   final: / "final" legacy per-frame finality boolean -> finality is a
#                  terminal status state (same file; task.ex:29-31)
#
# The A2A.[A-Z] arm is anchored so AshA2A.* (char before "A2A" is
# alphanumeric) is never flagged -- only a bare, module-position A2A.* ref.
# Scope is templates/ only: pack.toml/ontology.ttl prose may cite the
# legacy names historically, and fixtures name consumer module namespaces
# (XaasWeb.A2A.NextReadUserAgent), neither of which is a wire shape.
set -eu

pack_root="$(cd "$(dirname "$0")/.." && pwd)"
matches="$(
  grep -nE '(^|[^[:alnum:]_])(A2A\.[A-Z]|kind:|"kind"|final:|"final")' \
    "$pack_root"/templates/*.tmpl || true
)"

if [ -n "$matches" ]; then
  echo "gates/030_no_stale_wire_tokens.sh: STALE pre-v1.0 wire tokens in templates/:" >&2
  printf '%s\n' "$matches" >&2
  exit 1
fi

echo "gates/030_no_stale_wire_tokens.sh: templates/ clean -- no pre-v1.0 wire tokens"
