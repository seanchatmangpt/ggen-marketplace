# v26.9.30 Capability Ecology Wave — Lane Map

Coordinator wave (2026-09-30): 10 parallel lanes in ONE canonical checkout building the
qualified capability ecology `ash_pplan` v26.9.30 consumes, plus the adversarial workflow
corpus. Parallel to Claude's `ash_pplan` implementation wave — NO lane touches `~/ash_pplan`
except read-only inspection.

Pinned seams live in `RESOLUTIONS.md` (capability ID table, `wfc:` corpus schema,
namespace table). Lanes code against those, never against each other's files.

| lane | owns (exclusive write) | deliverable |
|---|---|---|
| 1 | `packs/domain-capability-pack/**` | EXTEND existing pack: Ash domain-action capability contract (dcp: aligned to pinned IDs) |
| 2 | `packs/filesystem-capability-pack/**`, `packs/network-capability-pack/**` | filesystem family (fscap) + network/HTTP family (ncap) |
| 3 | `packs/process-capability-pack/**`, `packs/scheduling-capability-pack/**` | OTP/process family (pcap) + scheduling family (scap) |
| 4 | `packs/event-state-capability-pack/**`, `packs/observation-capability-pack/**` | events/state family (escap) + observation/telemetry family (ocap) |
| 5 | `packs/durability-capability-pack/**` | durability/replay/resume family (dcap) |
| 6 | `packs/a2a-capability-pack/**` | SA2A distributed invocation family (aacap), composing existing sa2a-* pack vocabulary read-only |
| 7 | `packs/authority-capability-pack/**`, `packs/evidence-capability-pack/**` | authority family (authcap) + evidence/provenance family (ecap) |
| 8 | `packs/workflow-corpus-pack/**` EXCEPT lane-9/10 subtrees | corpus pack owner: scaffold, `wfc:` ontology exactly as pinned, fixtures 01–04, shared f000 gates |
| 9 | `packs/workflow-corpus-pack/fixtures/{05,06,07,08}-*/**`, `packs/workflow-corpus-pack/gates/f0{5,6,7,8}_*.rq` | corpus fixtures 05–08 (HDDL, FOND, durability+evidence, distributed SA2A) |
| 10 | `packs/workflow-corpus-pack/fixtures/{09,10,11,12}-*/**`, `packs/workflow-corpus-pack/gates/{f09,f10,f11,f12}_*.rq` | corpus fixtures 09–12 (dynamic branch/switch, dynamic recursion, authority-denied, interchangeable realizations) |

Shared-file ownership (no lane may write): `marketplace.toml`, `scripts/`, `scaffolds/`,
`docs/**`, existing `tests/**`, every pack dir not in the lane's row above, and the untracked
`packs/affidavit-consumer-pack/generated/` tree. New per-pack test files are allowed only as
`tests/test_<owned-pack-name>.py`.

Coordinator (this session) owns: git transitions, marketplace.toml, lifecycle.toml,
integration verification ladder, per-lane atomic commits.
