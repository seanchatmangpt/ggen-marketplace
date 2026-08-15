# fde20-revops-pack provenance receipt

## Source identity

- import origin repository: `seanchatmangpt/ggen`
- import origin commit: `eaa8c37619318fb36e4140c62173d9928f685226`
- import origin path: `packs/fde20-revops-pack`
- import origin pack tree: `240b19712dc6ff90d0cbe95496b65e27ab516987`
- destination repository: `seanchatmangpt/ggen-marketplace`
- destination admitted base: `17b716d133cf67a45d62e514cc38939283337222`

## Byte-identity proof

The nine pack-source blobs were recreated content-addressably in `ggen-marketplace`. Git returned the same blob SHA for every destination blob as the import origin:

- `README.md`: `a3d7d8869f7d5ef54dd5045bf44b5c870344556a`
- `pack.toml`: `cdc76bc9f56fd60c7d1416b7de9d36e0d1656e11`
- `ontology.ttl`: `838d01646c7862ab3279bf5575aee79cf15635ba`
- `gates/010_economic_contract.rq`: `cde36789a44ff8d03acd5ef495664c57ff54b62e`
- `gates/020_process_topology.rq`: `f97ff86f22a46ab6cffb9a1a1ee235084f9c409c`
- `gates/030_brce_authority.rq`: `38c02bf9b163c56649fbc9ab9b81905d94b67306`
- `templates/challenger_motion.md.tmpl`: `b8ad7c71e81863d6dc6523f6561e54b3149532ef`
- `templates/operating_contract.md.tmpl`: `b4af5365c10117efa77ccae21394b277dccb8c80`
- `templates/pipeline.json.tmpl`: `196cf12be7ddf5882019fe7b06cc02ef85213fd1`

This receipt records import provenance only. After marketplace admission, `seanchatmangpt/ggen-marketplace` is the canonical writable source authority for this pack; the `ggen` origin is provenance and must not silently regain authority.
