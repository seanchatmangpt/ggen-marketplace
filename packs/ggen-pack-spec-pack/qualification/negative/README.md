# qualification/negative — the GGEN invalid corpus (T03)

Appendix D `invalid/*` corpus of RFC-GPACK-001 v26.9.17: one fixture per
typed refusal (Appendix C), each with a machine-checkable assertion naming
the expected refusal code.

Law of this corpus (§77 Conformance Philosophy, §15 Gate Evidence):

> PASS = AttemptObserved ∧ ForbiddenOutcomeAbsent ∧ RequiredOutcomeObserved
> A negative test is valid only when the attack reached the gate.

Every fixture below is a minimal but complete pack whose manifest, graph,
and layout are lawful **except for the single attacked law**, so any refusal
an engine produces is attributable to exactly that law. A crash, a silent
success, or a different refusal code is a conformance finding against the
engine, not a pass.

## The fixtures

| Fixture | Attack | Expected outcome | Law |
|---|---|---|---|
| `manifest-unknown-key/` | unknown key `qualification_attack` inside `[pack]` | `REFUSED:PACK_MANIFEST_INVALID` | §7.1 |
| `manifest-semantic-identity-mismatch/` | `pack.toml` name ≠ graph `gp:name` | `REFUSED:PACK_IDENTITY_MISMATCH` | §8 |
| `missing-ontology/` | no `ontology.ttl` beside a valid manifest | `REFUSED:PACK_GRAPH_MISSING` | §6, App. C |
| `gate-positive-select/` | returning SELECT planted in `gates/` (rows > 0) | `REFUSED:GATE_VIOLATION` | §14, §96 row 2 |
| `query-positive-select/` | SAME SELECT in `queries/` — MUST NOT refuse | rows rendered, no `REFUSED:` | §13, §96 row 1 |
| `path-traversal/` | frontmatter `to: "../../gpack-t03-escape-target.txt"` | `REFUSED:PACK_PATH_ESCAPE` | §71, §96 |
| `symlink/` | symlinked source file, planted by `setup.sh` at test time | `REFUSED:PACK_SYMLINK` | §72 |
| `dependency-cycle/` | pack-a requiresPack pack-b requiresPack pack-a | `REFUSED:DEPENDENCY_CYCLE` | §34 |
| `ambiguous-capability/` | one `gp:requiresCapability`, two providers, no selection rule | `REFUSED:AMBIGUOUS_CAPABILITY_PROVIDER` | §31 |
| `target-collision/` | two packs claim `shared-collision-target.txt`, no merge contract | `REFUSED:TARGET_OWNERSHIP_CONFLICT` | §43 |
| `renderer-mismatch/` | advertised `gp:EEx1` pack meets a Tera-only profile | `REFUSED:RENDERER_PROFILE_MISMATCH` **or** `UNSUPPORTED:RENDERER:EEx1` | §19, §100 |

The expected code of each fixture is machine-readable in
`<fixture>/assert/refusal-code.txt` (first non-comment line).

## The D1 falsifier pair (§96 rows 1–2, §4.4 divergence D1)

`gate-positive-select/` and `query-positive-select/` are one falsifier, split
across two surfaces. Both ship a **byte-identical** `SELECT ?s WHERE { ?s ?p ?o }`
(compare `gate-positive-select/gates/010_positive_select.rq` with
`query-positive-select/queries/d1_select.rq` — equality is asserted by
`tests/test_gpack_negative_corpus.py`):

- as `gates/*.rq` it is a falsifier gate: `Violation = RowCount > 0` (§14),
  so sync MUST refuse → `REFUSED:GATE_VIOLATION`;
- as `queries/*.rq` it is a named query (§13): rows MUST render and the
  engine MUST NOT refuse.

An engine that refuses the query half, or admits the gate half, has
collapsed Query into Gate — the D1 conflation this pair exists to kill.
`query-positive-select/assert/run.sh` requires positive evidence of the rows
(the row value `urn:ggen:pack:mkt03-query-positive-select` on the engine's
output streams), so a silently-successful engine cannot pass either.

## How to assert

Each `assert/run.sh` is self-contained and portable:

```sh
<fixture>/assert/run.sh "<engine-command-template>"
```

- The template is a shell command string that contains the literal
  placeholder `{{PACK}}`; run.sh replaces it with the absolute path of the
  attack pack handed to the engine (the fixture directory itself; see
  multi-pack fixtures below). Example:

  ```sh
  packs/ggen-pack-spec-pack/qualification/negative/manifest-unknown-key/assert/run.sh \
    "ggen sync run --pack {{PACK}}"
  ```

- The template also runs with these env vars: `PACK_DIR`, `FIXTURE_DIR`,
  `CORPUS_DIR` — plus, for multi-pack fixtures, one var per member pack
  (`PACK_A_DIR`/`PACK_B_DIR`, `CONSUMER_DIR`/`PROVIDER_ALPHA_DIR`/
  `PROVIDER_BETA_DIR`, `PACK_ONE_DIR`/`PACK_TWO_DIR`). Wire the engine's
  consumer config so pack names resolve to those paths.
- Engines print typed refusals on **stderr**; run.sh captures stdout AND
  stderr and exits **0 iff** the combined output contains the exact typed
  code from `assert/refusal-code.txt` (and, where the RFC admits a second
  classification, that alternate — renderer-mismatch only).
- **Bare crash text is not a refusal** (§83 `UNSUPPORTED ≠ REFUSED`; a panic
  is neither): output matching panic/backtrace/traceback signatures without
  the typed code fails the assertion.
- A typed refusal observed for the *wrong* law is not checked here — each
  fixture is minimal so the attacked law is the only one that can fire; if
  an engine reports a different code, that is a real finding to record.

Multi-pack fixtures expose their entry pack as `{{PACK}}`:

- `dependency-cycle/`: entry `pack-a/` (cycle closes through `pack-b/`);
  `{{PACK}}` = `.../dependency-cycle/pack-a`.
- `ambiguous-capability/`: entry `consumer/` (providers in `provider-alpha/`,
  `provider-beta/`); `{{PACK}}` = `.../ambiguous-capability/consumer`.
- `target-collision/`: entry `pack-one/` (PROJECTION-scope dependency on
  `pack-two/`, §29); `{{PACK}}` = `.../target-collision/pack-one`.

### The symlink fixture never contains a symlink in git

`symlink/setup.sh` materializes the §72 attack
(`templates/linked-source.tera -> ../pack.toml`) at test time;
`symlink/assert/run.sh` runs it against a **scratch copy** (`mktemp -d`) so
the checked-in tree — and this repo's own `PACK_SYMLINK` gate
(`scripts/marketplace.py` refuses any symlink under `packs/`) — stay clean.
Ticket acceptance #3: no real symlink is committed under this corpus.

### Vacuity probe (acceptance #1): the null engine

A guard that cannot fail is vacuous. `null-engine.sh` is a stub that echoes
nothing and exits 0. **Every** `assert/run.sh` MUST exit non-zero against it:

```sh
packs/ggen-pack-spec-pack/qualification/negative/run-null-falsifier.sh
# -> "OK: no assertion in this corpus passes vacuously" (exit 0) iff all 11 fail
```

`tests/test_gpack_negative_corpus.py` runs the same probe permanently, so
the corpus cannot silently rot into assertions that pass without an engine.

## Running against real engines (wave 2)

Out of scope for T03 (see `docs/jira/v26.9.18/PLAN.md`): wave 2 wires real
`ggen` / `ggen_igniter` into the templates above. When doing so, run
fixtures from a checkout or copy — never materialize `symlink/setup.sh`
in-tree (see above).

## Inventory contract

Exactly these 11 fixture directories live here; the expected-code files are
non-empty; the D1 pair's queries are byte-identical; no path is a symlink.
`tests/test_gpack_negative_corpus.py` asserts all of it — add a fixture
there and to the table above in the same change.

## Edges considered and not taken (recorded, not pruned)

- **Spec-pack root manifest**: `packs/ggen-pack-spec-pack/pack.toml` +
  `ontology.ttl` are owned by T01 (`gpack/mkt-01-specpack-scaffold`, §7.1
  strict schema + §8 correspondence gate). This corpus ships without them;
  until T01 merges, `scripts/marketplace.py validate` reports exactly
  `REFUSED:MANIFEST_MISSING:ggen-pack-spec-pack` and
  `REFUSED:ONTOLOGY_SOURCE_MISSING:ggen-pack-spec-pack` — no other refusal
  comes from this corpus (proven with an uncommitted stand-in root; see
  ticket History).
- **`gp:ownsTarget` declarations in target-collision**: §42 says ownership
  SHOULD be exposed before write; the identical frontmatter `to:` fields are
  the minimal sufficient declaration that reaches the §43 law. RDF-level
  `gp:ownsTarget` duplication was left to the engine profiles that consume
  it.
- **Positive-evidence channel for query-positive-select**: engines differ on
  where rendered rows surface, so run.sh requires the row value on ANY
  output stream (stdout or stderr) rather than guessing a file path. Wave 2
  may tighten this to receipt inspection (§54/§55).
- **Consumer-config wiring for multi-pack fixtures** (dependency-cycle,
  ambiguous-capability, target-collision): the engine command template and
  exported per-pack dir vars are the contract; a portable consumer-config
  format arrives with the RFC's consumer profile work, not this corpus.
