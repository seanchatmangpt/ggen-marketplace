# Arcus Pre-existing Failures Receipt

Standing: UNVERIFIED

Subject: arcus `gcp_emulator` / `sdlc` tests, observed failing before this lane's work.
Ticket: ggen-marketplace-20 (lane W4-20). Not re-run by this lane (no build/test access).

| failure | location | class |
|---|---|---|
| HCL_UNSUPPORTED in gcp_emulator tests | arcus gcp_emulator | pre-existing |
| nil deref | sdlc_test.go:153 | pre-existing |
| fnox e2e test fixes not yet receipted | /Users/sac/fnox | open |

SHA: not captured (coordinator to fill). Replay: run arcus `go test` for
`gcp_emulator` and `sdlc` packages; exit and SHA to be appended by the coordinator.

## See Also

- docs/pack-consumer-contract.md (Budget gate)
