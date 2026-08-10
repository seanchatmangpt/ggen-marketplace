# Reference: catalog command

```bash
python3 scripts/marketplace.py catalog
```

The command emits UTF-8 JSON to stdout with keys sorted deterministically. The root object also
carries `marketplace_version` — this repository's own `[marketplace].version` from
`marketplace.toml` (see `version`, below): a whole-registry-snapshot identifier, independent of
individual packs' own SemVer and of `[ggen].version` (the pinned upstream `ggen` binary).

Records are sorted by pack identity and include:

- `name`, `version`, `description`, and repository-relative `path`;
- derived `profile` (`projection`, `semantic`, or `project`);
- ontology-file count and a deterministic SHA-256 fingerprint over ontology paths+bytes;
- template count;
- native-SPARQL gate count;
- verifier-gate count;
- SHA-256 of `pack.toml`;
- `digest` — `sha256:<hex>` of the pack's deterministic `.tar.gz` (see `scripts marketplace.py
  archive`, below), computed fresh from `packs/` on every invocation — not read from a
  previously-built artifact;
- `size_bytes` — that archive's byte length;
- `download_url` — where the archive is published once `.github/workflows/publish.yml` has run
  at least once for the commit this catalog was generated from: a GitHub Release asset URL under
  the repository's rolling `packs` release. The URL is always computed the same way regardless
  of whether that release exists yet; a consumer fetching it before any publish run will get a
  404, not a stale or wrong artifact.

The root object identifies schema `https://ggen.dev/marketplace/catalog/v2` (bumped from `v1`
when `digest`/`download_url`/`size_bytes` were added — an additive change, no prior field
removed or renamed).

The JSON is a projection and is intentionally not committed as a second editable catalog. Running the command twice at the same filesystem subject must produce byte-identical stdout — this now also requires `python3 scripts/marketplace.py archive`'s own archive-build to be deterministic (fixed file order, zeroed mtime/uid/gid on every tar entry, zeroed gzip mtime), since `digest`/`size_bytes` are computed from a fresh in-process build each call, not cached.

## `archive` — building the published artifacts

```bash
python3 scripts/marketplace.py archive
```

Builds every admitted pack's deterministic `.tar.gz` into `dist/packs/<name>-<version>.tar.gz`
and prints one `<name> <version> sha256:<hex>` line per pack. This is what CI's publish job
(`.github/workflows/publish.yml`) uploads as GitHub Release assets on every push to `main`; the
same command run locally reproduces byte-identical archives, so a consumer can independently
verify a published asset against a from-source rebuild rather than trusting the download alone.

## `version` — this repository's own release identity

```bash
python3 scripts/marketplace.py version
```

Prints `marketplace.toml`'s `[marketplace].version` bare (e.g. `v26.8.9`). This is the
marketplace's own org-owned version for a whole registry snapshot — bump it and publish (push to
`main`) to cut a **second, immutable** GitHub Release tagged with that version, in addition to
the always-mutating rolling `packs` release:

- the rolling `packs` release always reflects the latest `main` — its assets are overwritten
  (`--clobber`) on every publish;
- a versioned release (e.g. `v26.8.9`) is cut once, the first time that version is seen, and
  never overwritten afterward — CI refuses to touch an existing versioned release, so `git tag
  v26.8.9` really does mean "the marketplace as it was," permanently. It carries the same pack
  archives as the rolling release at that moment, plus `catalog.json` — the exact catalog
  snapshot for that version, so a consumer can fetch one release and get both the index and the
  content it describes without depending on the (mutable) Pages deployment matching it later.

`[marketplace].version` is independent of individual packs' SemVer and of `[ggen].version` (the
pinned upstream `ggen` binary this repo qualifies against) — three separate version axes, on
purpose, not aliases of each other.
