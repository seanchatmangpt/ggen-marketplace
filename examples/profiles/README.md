# Profile Fixtures

Sample deployment profiles for the AAIF solution flow.

`enterprise.json` is a Fortune 5-shaped profile: it feeds
`scripts/profile_intake.py` (normalized JSON + RDF individuals) and is pinned
into `solutions/enterprise-aaif/` via its `solution.json` lock
(`profile_sha256` = sha256 of the normalized profile). The deployer
(`scripts/deploy_aaif_solution.py`) verifies the digest before manufacture and
re-runs pack gates at deploy time — a tampered profile is refused before any
dist is produced.

`team.json` is a small-team profile exercising the alternate enum corner
(EU residency lock, CMEK `NONE`, BASIC finops, CHRONICLE SIEM, ML-DSA-65,
single replica) with two team members.
