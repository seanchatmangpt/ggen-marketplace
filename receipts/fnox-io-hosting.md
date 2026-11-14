# fnox-io-hosting

Standing: BLOCKED

## Subject

fnox.io hosting of the ggen-marketplace registry (`[registry.fnox_io]` in
`/Users/sac/ggen-marketplace/marketplace.toml`, endpoint `https://fnox.io/`).

## State

- Hosting: authored, NOT deployed. Terraform lives in `/Users/sac/fnox/infra/gcp/edge/` and
  `/Users/sac/fnox/justfile.d/99-fnox-io.just`; no apply has been observed.
- Registration: fnox.io domain registration is pending ACTIVE (observed 2026-11-14).
  Setup record: `/Users/sac/fnox/docs/setup/fnox-io-domain.md`.
- HTTP evidence: none. No `curl -sI https://fnox.io` response has been captured for this
  receipt, so no claim of a live registry is made.

## Unblock condition

Domain registration reaches ACTIVE (Cloud Domains state ACTIVE, DNS zone `fnox-io`
delegated). Only then may deploy proceed, and Standing may leave BLOCKED only with a
captured `curl -sI https://fnox.io` response showing a registry reply.

## Falsifier

`curl -sI https://fnox.io` returns a registry response while this receipt says not deployed,
or this receipt says deployed with no HTTP evidence.

## See Also

- `/Users/sac/ggen-marketplace/receipts/fnox-io-hosting-2026-11-14.md`
- `/Users/sac/ggen-marketplace/marketplace.toml`
