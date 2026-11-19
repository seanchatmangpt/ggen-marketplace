# ip-allowlist-network-policy-pack

Closes the Fortune 5 `global-network` catalog stub
(`bb:commonPack "fortune5-network-law-pack"`) with real IP-allowlist +
NetworkPolicy shapes, gates, and templates.

## Catalog binding

| Surface | Value |
|---|---|
| Catalog group | `global-network` |
| Catalog version | `26.7.31` |
| Catalog pack id | `fortune5-network-law-pack` |
| Output directory (group) | `infrastructure/network` |

## Law

- Named `ianp:IpAllowlist` of `ianp:CidrEntry` rows (closed purposes:
  admin / vpn / corp / peer).
- `ianp:NetworkPolicySpec` with closed posture:
  `ZeroEgress` | `DefaultDenyWithAllow` | `IngressAllowlistOnly`.
- Zero-egress jail: `policyTypes: [Egress]`, `egress: []` (fnox
  `sovereign-zero-egress-jail` pattern).
- `directActuation false` everywhere (broker-only).

## Gates

| Gate | Refusal |
|---|---|
| `010_program_contract.rq` | Incomplete program / allowlist / policy contract |
| `020_cidr_shape.rq` | Bad/missing CIDR, empty allowlist, open purpose |
| `030_posture_coherence.rq` | Posture vs policyTypes / egressEmpty / allowlist incoherent |
| `040_catalog_binding.rq` | catalogGroup / catalogPackId drift |
| `050_broker_only_blocked_surfaces.rq` | directActuation or claimed `github_ip_allow_list_entry` |

## BLOCKED residue

GitHub org-level IP allow-list terraform (`github_ip_allow_list_entry`) is
not generatable — provider gap disclosed in gh-terraform-pack. This pack
documents and gate-refuses that claim; it does not invent a substitute.

## Standing

See `STANDING.md`. Coordinator sync / court required before any upgrade.
