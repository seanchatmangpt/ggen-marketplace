# fnox-io-hosting-2026-11-14

Standing: BLOCKED

Blocked: fnox.io registration is pending ACTIVE (external dependency); hosting in
/Users/sac/fnox/infra/gcp/edge/ is authored, not deployed.

- Date: 2026-11-14
- Subject: /Users/sac/ggen-marketplace/marketplace.toml `[registry.fnox_io]` endpoint entry
- Probe: `curl -sI -m 10 https://fnox.io/` -> observed rc=6 (could not resolve host),
  no HTTP status line obtained.
- Replay: `curl -sI -m 10 https://fnox.io/; echo rc=$?` and
  `grep -n "fnox.io" /Users/sac/ggen-marketplace/marketplace.toml`
- Promotion to PASS requires registration ACTIVE and an HTTP status line from curl.
