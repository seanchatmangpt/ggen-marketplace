# Pin and verify packs

Consumers can pin marketplace packs to a digest and refuse any archive that does not match.
Everything here is stdlib Python 3.11 via `scripts/fetch_pack.py`.

## Lock the packs you use

```bash
python3 scripts/marketplace.py catalog > catalog.json
python3 scripts/fetch_pack.py lock catalog.json <pack> [<pack>...] --out packs.lock.json
```

`packs.lock.json` records `name`, `version`, `digest` (`sha256:...`) and `download_url` per pack.
Commit it in the consumer project.

## Verify an archive

```bash
python3 scripts/fetch_pack.py verify <pack>-<version>.tar.gz <pack> --lock packs.lock.json
```

The archive sha256 is recomputed and compared with the lock (or `--catalog`) digest. A difference
exits 2 with `REFUSED:DIGEST_MISMATCH`.

## Fetch and extract

```bash
python3 scripts/fetch_pack.py fetch <pack> --catalog catalog.json --lock packs.lock.json --out packs
```

`--catalog` accepts a file or an `https://`/`file://` URL. The archive at `download_url` is
downloaded, verified, and only then extracted. Extraction refuses absolute paths, `..`, symlinks
and hardlinks, special files, and members outside the `<pack>/` root
(`REFUSED:UNSAFE_PATH`, `REFUSED:LINK_MEMBER`, `REFUSED:SPECIAL_MEMBER`, `REFUSED:OUTSIDE_PACK_ROOT`).
If the lock and catalog digests disagree, `REFUSED:LOCK_CATALOG_DRIFT`.

## See Also

- [Publish a pack](publish-a-pack.md)
- [Pack contract](../reference/pack-contract.md)
