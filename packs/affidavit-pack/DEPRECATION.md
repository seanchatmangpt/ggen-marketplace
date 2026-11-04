# DEPRECATED — superseded by affidavit-consumer-pack

This pack is deprecated. `packs/affidavit-consumer-pack` is the successor
(declared in `pack.toml` lifecycle metadata, line 5).

New consumers should depend on `affidavit-consumer-pack`. This pack is
retained for existing pins only; expect no further development here.

Freeze retention: this pack's freeze declarations (`freeze_policy: checksum`,
`freeze_slots_dir: .ggen/freeze/affidavit-pack`) are retained as-is; existing
consumers keep FM-WRITE-005 protection, and no freeze witnesses are refreshed
post-deprecation.
