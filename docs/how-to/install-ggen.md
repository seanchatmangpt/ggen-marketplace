# How to install ggen

Marketplace scripts and the tutorials need a real `ggen` binary on `PATH`.

## Pinned release (digest-checked)

`marketplace.toml` `[ggen]` pins the repository, release tag, release commit, and per-platform
archive SHA-256. `scripts/install-ggen.sh` admits that config through `star-toml`, downloads the
asset, refuses if the tag no longer points at the pinned commit (`REFUSED:GGEN_RELEASE_TAG_DRIFT`)
or the digest differs, and prints the path of the cached binary:

```bash
export PATH="$(dirname "$(bash scripts/install-ggen.sh)"):$PATH"
ggen --version
```

Supported platforms: Linux x86_64/aarch64, macOS x86_64/arm64. Anything else is
`REFUSED:UNSUPPORTED_GGEN_PLATFORM`.

## Already have ggen

Any `ggen` on `PATH` is used as-is by `python3 scripts/marketplace.py check <pack>` and
`python3 scripts/run_quickstart.py`. Record `ggen --version` with your evidence: a newer binary than
the `[ggen].version` pin is a different toolchain identity, and full-corpus qualification claims
should use the pinned one.

## Verify

```bash
python3 scripts/run_quickstart.py
```

## See Also

- [Tutorial: build your first ggen pack](../tutorials/first-pack.md)
- [How to validate locally](validate-locally.md)
- [ggen qualification contract](../reference/ggen-qualification-contract.md)
