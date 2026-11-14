# Known Divergences Register

Standing: UNVERIFIED

Registers pre-existing arcus failures so a later red run can be classed pre-existing versus
session-introduced. Observed in the v26.11.14 session by the coordinator; this lane re-ran
nothing (no build/test rights). Receipt SHAs: ggen-marketplace 6470e2538, arcus 1a9bb0b
(HEAD at register authoring, not the SHA of the failing run; replay identity absent until a
rerun cites its SHA).

## Rows

### KD-ARC-1 HCL_UNSUPPORTED (arcus gcp_emulator)

- Surface: arcus `gcp_emulator` (`/Users/sac/arcus/internal/gcp_emulator/`; rerun: `go test ./internal/gcp_emulator/...` in /Users/sac/arcus).
- Divergence: fails with `HCL_UNSUPPORTED` on the terraform HCL fed to the emulator.
- Evidence receipt: coordinator observation this session, arcus 1a9bb0b; UNVERIFIED (no receipt
  file captured).
- Close condition: emulator parses or typed-refuses the HCL construct, and the gcp_emulator test
  passes at a cited SHA.

### KD-ARC-2 sdlc nil deref (arcus sdlc)

- Surface: arcus `sdlc` test package, `/Users/sac/arcus/internal/gcp_emulator/sdlc/sdlc_test.go`
  (rerun: `go test ./internal/gcp_emulator/sdlc/...` in /Users/sac/arcus).
- Divergence: panics with nil pointer dereference at or near `sdlc_test.go:153` (`if err == nil || rep == nil {`; whether this is the nil site
  or a guard is unverified).
- Evidence receipt: coordinator observation this session, arcus 1a9bb0b; UNVERIFIED.
- Close condition: sdlc tests run green at a cited SHA, or the nil is replaced by a typed error.

### KD-AW7 (arcus aws)

- Surface: AWS S3 object lock and presigned URLs (arcus `KNOWN_DIVERGENCES.md` lines 35, 533).
- Divergence: PutObjectLockConfiguration and query-string SigV4 presign absent; authored in arcus-05,
  court not yet run. Arcus standing PARTIAL / OPEN.
- Evidence receipt: `/Users/sac/arcus/docs/aws-parity/AW7.md`; UNVERIFIED.
- Close condition: both ops served, passing go test court, PASS receipt exists.

### KD-AW8 (arcus aws)

- Surface: AWS DynamoDB indexes, pagination, nested paths (arcus `KNOWN_DIVERGENCES.md` lines 36, 542).
- Divergence: GSI/LSI, pagination tokens, SigV4, nested attribute paths, ADD/DELETE update clauses
  absent. Arcus standing PARTIAL / OPEN.
- Evidence receipt: `/Users/sac/arcus/docs/aws-parity/AW8.md`; UNVERIFIED (not run).
- Close condition: gaps served, passing court, PASS receipt exists.

### KD-AW9 (arcus aws)

- Surface: AWS KMS and Secrets Manager mount and auth (arcus `KNOWN_DIVERGENCES.md` lines 37, 551).
- Divergence: KMS (22 ops) and Secrets Manager authored but not mounted nor SigV4-verified.
  Arcus standing PARTIAL / OPEN.
- Evidence receipt: `/Users/sac/arcus/docs/aws-parity/AW9.md`; UNVERIFIED (not run).
- Close condition: AW1 mount plus SigV4 wired, passing court, PASS receipt exists.

## Falsifier

A row cites a failure that no longer reproduces at the cited SHA, or the nil deref location
differs from `sdlc_test.go:153` when re-run.

## See Also

`/Users/sac/ggen-marketplace/docs/jira/v26.11.5/stale-claims-register.md`
