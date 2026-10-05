# ggen pin bump — PENDING v26.10.5 release artifacts

Status: BLOCKED. Execute when the v26.10.5 release lands. ~10 min.

## 1. marketplace.toml edits (exact)

```toml
[ggen]
version = "v26.8.11"        -> version = "v26.10.5"
release_commit = "402cecdff8784767eb9f26e235d87c759610c066"
                             -> release_commit = "<sha>"   # v26.10.5 tagged commit
```

Four asset sha256 placeholders (`[ggen.assets.*]` keys unchanged; archive
names below are the release.yml matrix targets, same filenames as today):

| key                | archive                            | sha256      |
|--------------------|------------------------------------|-------------|
| linux_x86_64       | ggen-x86_64-unknown-linux-gnu.tar.gz | `<sha256>` |
| linux_aarch64      | ggen-aarch64-unknown-linux-gnu.tar.gz | `<sha256>` |
| darwin_aarch64     | ggen-aarch64-apple-darwin.tar.gz   | `<sha256>`  |
| darwin_x86_64      | ggen-x86_64-apple-darwin.tar.gz    | `<sha256>`  |

## 2. Verification sequence after the bump

```bash
# admit config
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json

# version court (refuses GGEN_VERSION_DRIFT on mismatch vs installed binary)
GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json \
  bash scripts/qualify-marketplace.sh \
  /tmp/ggen-marketplace-admitted.json /tmp/ggen-marketplace-qualification.json

# tag->commit binding + digest checks (independent of the above)
bash scripts/install-ggen.sh   # verifies v26.10.5 tag == <sha>, then all 4 sha256

# full pack corpus qualification
python3 scripts/qualify_packs.py --report /tmp/pack-qualification.json
```

## 3. Why BLOCKED right now

- Release assets for v26.10.5 are unpublished — no artifacts to digest.
- sha256 digests unknown until assets exist.
- The v26.10.5 tag exists only locally in ~/ggen; not pushed to origin.
- Release workflow requires manual workflow_dispatch per C1's checklist
  (per-target matrix build, then tag→commit binding must be recorded).
