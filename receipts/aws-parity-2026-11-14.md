# AWS Parity Receipt 2026-11-14

Standing: PARTIAL

## Identity

- ggen-marketplace: 6470e25381f5ca7c7dae340545fab9dc367943f7
- arcus: 1a9bb0b330f605a7de1a96dbbae8d51f366562ec
- smalt: d22a1c80f625d970509162a257af0227d58b0fe4
- fnox (matrix): 93d464b86aa3539513e00d89c3c1e592f78d8692

SHAs read from each checkout's `.git` main ref on 2026-11-14.

## Reported test output (operator session observation, not re-run by this receipt's author)

Source: ticket ggen-marketplace-03.

- arcus aws emulator Go tests: pass (count not recorded in the ticket).
- smalt `mix test test/gcp test/aws`: 76 passed.

The coordinator must re-run both and append raw output here before standing rises to PASS.

## Authority

Pack `packs/aws-cloud-dialect-pack/` encodes the aws cells of fnox
`docs/HYPERSCALER_PARITY.md`. Registered divergences KD-AW7, KD-AW8, KD-AW9, KD-AW12 are
cited by that matrix; their rows were not re-read here.

## Replay

- `ggen sync run` in a consumer of aws-cloud-dialect-pack, then both gates.
- smalt: mix test over test/gcp and test/aws.
- arcus: go test over the aws emulator packages.

## Standing detail

PARTIAL: pack and receipt exist with SHAs; arcus count and gate execution outstanding.
