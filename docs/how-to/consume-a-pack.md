# How to consume a pack

Reference the selected pack from the consumer project's `ggen.toml` using a local path or another transport supported by the ggen version you have admitted. For a local checkout:

```toml
[packs]
my-pack = { path = "../ggen-marketplace/packs/my-pack" }
```

## Fetching a pack without a local checkout

Every admitted pack is also published as a deterministic `.tar.gz` archive, with its
download URL and SHA-256 digest listed in the marketplace catalog
(`python3 scripts/marketplace.py catalog` — see
[`docs/reference/catalog-command.md`](../reference/catalog-command.md)) under each pack's
`download_url`/`digest` fields. Fetch and verify one directly:

```bash
url=$(python3 scripts/marketplace.py catalog | python3 -c \
  'import json,sys; print(next(p["download_url"] for p in json.load(sys.stdin)["packs"] if p["name"]=="my-pack"))')
curl --fail --location "$url" --output my-pack.tar.gz
sha256sum my-pack.tar.gz   # compare against the catalog's `digest` field before extracting
tar -xzf my-pack.tar.gz
```

This is the same download-then-verify discipline `scripts/install-ggen.sh` already uses to fetch
the pinned `ggen` binary — never extract before the digest matches. Whether a given
`download_url` currently resolves depends on `.github/workflows/publish.yml` having run for that
commit (it runs on every push to `main`); it is unavailable for uncommitted or unmerged pack
changes, which must still be consumed via the local-path form above.

Before running ggen, inspect the pack source and any gates. After `ggen sync run`, validate the generated artifacts with the consumer's native compiler/tests and rerun sync to check stability. Do not treat marketplace CI as proof of the consumer consequence.
