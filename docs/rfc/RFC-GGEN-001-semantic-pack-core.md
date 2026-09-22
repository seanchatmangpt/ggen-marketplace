# RFC-GGEN-001 v26.9.17

## Semantic Pack Core — What a ggen Pack Is

**Status:** Proposed Standard
**Version:** v26.9.17
**Category:** Architecture / Data Model
**Companion specification:** None. This document does not extend, require conformance
to, or claim membership in the RFC-SA2A series. §8 discusses convergent terminology
and deliberately borrowed house style only; no dependency edge exists in either
direction.
**Intended audience:** ggen pack authors; ggen-marketplace corpus maintainers;
ggen_igniter maintainers and consumers; authors of any future runtime (Rust, Elixir,
or otherwise) that reads, writes, or admits ggen packs.

> This document uses RFC-style normative language but is not an IETF publication.

---

# 1. Abstract

A "ggen pack" is not, today, one thing. Real, currently-running code in three
independent repositories — the Rust `ggen` CLI (`/Users/sac/ggen`), the
`ggen-marketplace` pack corpus and its Python admission scripts
(`/Users/sac/ggen-marketplace`), and the Elixir `ggen_igniter` Igniter library
(`/Users/sac/ggen_igniter`) — each parse a file named `pack.toml` (or an equivalent
directory convention) into a *different* shape, for a *different* purpose, admitted
by a *different* law. This RFC does not paper over that fact. It names the minimal
tuple of properties a pack MUST have for any of these three real implementations, or
a future one, to agree on what a pack **is**, independent of which concrete registry,
RDF library, template engine, or programming language reads it.

This RFC is **law**, not **court**: it specifies invariants a pack manifest and its
containing tree MUST or SHOULD satisfy, and attaches a falsifier to every load-bearing
requirement. It deliberately does **not** build, and does not require building, a
qualification corpus, a conformance-test harness, a new marketplace registry entry, or
any change to the real `marketplace.active.toml`, `scripts/marketplace.py`, or any
file under `packs/`, `/Users/sac/ggen`, or `/Users/sac/ggen_igniter`. That machinery
is named explicitly, as real future work, in §19.

# 2. Status of This Document

This is a Proposed Standard within the ggen ecosystem's own document series. It has
no relationship to the IETF RFC series beyond borrowing its normative-language
convention. It has not been ratified against a formal conformance suite (none is
defined by this document; see §19). It supersedes no prior ggen document — no prior
`RFC-GGEN-*` document exists.

# 3. Conventions Used in This Document

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are to be
interpreted as normative, in the sense conventional to specification documents. This
document, like the real RFC-SA2A-001/002 documents that were consulted for house
style (see §8), does not cite BCP 14 / RFC 2119 / RFC 8174 by number — that omission
is itself the observed convention of the nearest real precedent in this user's
corpus, not an oversight.

Boxed formulas use fenced ` ```math ` blocks (the convention observed in the more
recently authored of the two real RFC-SA2A documents), not raw `$$` LaTeX, so this
document renders correctly in a plain Markdown viewer. Enumerations of fixed
vocabularies are rendered as fenced ` ```text ` blocks, one item per line, not as
prose lists, matching the same observed convention.

Every numbered requirement in §12 attaches a **falsifier**: the invariant under
attack, the exact subject, the stimulus, the boundary expected to decide it, the
forbidden standing or consequence, and — critically — what would make a **passing**
result invalid (a check that never actually exercised the forbidden transition). A
falsifier that cannot observe its own forbidden transition is not evidence of
conformance; it is silence, and silence is not a court verdict.

# 4. Terms and Definitions

```text
Pack               — the subject of this RFC: a named, versioned, admittable unit
                      of semantic and/or generative content, defined formally in §5.
Registry           — a filesystem or network location plus an admission law (§9)
                      that decides which candidate trees are packs in good standing.
Manifest           — the structured file (pack.toml, or an equivalent) a registry's
                      admission law parses to extract a pack's declared identity.
Grounding graph     — the admitted RDF individuals and classes a pack contributes
                      (G in the tuple, §5); the pack's actual semantic content.
Projection          — a deterministic query→render step that turns (grounding
                      graph, generation rule) into generated output (Π in §5).
Profile             — one of {project, projection, semantic}; derived, not
                      declared, from a pack's own filesystem shape (§7.3).
Admission           — the act of a registry's law (A) accepting or refusing a
                      candidate pack tree; see §9.
Qualification       — the separate, heavier act of proving a pack's generation
                      pipeline is deterministic and non-mutating under real
                      re-manufacture (Q in §5); see §7.5 and §19.
Composition         — one pack declaring, and a runtime resolving, a dependency on
                      another pack's content at generation time (§10).
Capability contract — an abstract behavior this RFC requires of some pluggable
                      component (an RDF store, a template engine), independent of
                      which concrete implementation satisfies it; see §13.
Reference
  implementation    — a concrete, currently-real piece of code (the Rust ggen CLI,
                      the ggen-marketplace Python scripts, ggen_igniter) that
                      satisfies a capability contract today, named for
                      grounding, not mandated as the only legal satisfier.
```

# 5. Preserve — The Thin Waist

## 5.1 The formal pack tuple

A pack is the tuple

```math
\boxed{
P = (I, G, D, \Pi, A, Q, E, L)
}
```

where:

- **I — Identity.** A `(name, version)` pair, bound to exactly one location inside
  its owning registry, independently re-derivable from that location without
  trusting the manifest's own self-report. See §7.1.
- **G — Grounding graph.** Zero or more admitted RDF documents constituting the
  pack's actual semantic content — the individuals, classes, and properties the
  pack contributes to whatever graph a consuming project unions it into. See §7.2.
- **D — Declared composition.** The pack's own statement of which other packs (or
  external components) it depends on, and by what resolution mechanism. See §7.4
  and §10.
- **Π (Pi) — Projections.** The pack's query→template generation rules: SPARQL (or
  an equivalent query capability, §13.1) paired with a template (Tera, EEx, or an
  equivalent rendering capability, §13.2), producing deterministic output. See §7.6.
- **A — Admission law.** The specific, real function a registry runs over a
  candidate pack tree to decide REFUSED vs. admitted. See §9.
- **Q — Qualification contract.** The (separate, heavier, currently
  marketplace-repo-owned, NOT part of this RFC's scope to build) manufacture-twice-
  compare obligation a pack's generation pipeline must satisfy to be trusted beyond
  bare admission. See §7.5 and §19.
- **E — Evidence.** The reproducible content-digest(s) binding a pack's identity to
  its actual bytes, so a claim of "this is pack X at version Y" is falsifiable
  against the real tree, not merely asserted. See §7.7.
- **L — Lifecycle.** The pack's position along three independent axes — profile
  (derived from shape), scope (declared "active" vs. "legacy" membership in a
  registry's curated subset), and trust tier (derived from how it was admitted,
  never from what it claims about itself). See §7.3, §7.8.

## 5.2 Why this tuple, and not a bigger or smaller one

Each element of `P` is included because at least one real, currently-running
implementation treats it as load-bearing, and excluded from being merged with a
neighboring element because at least one real implementation treats the two as
independently variable. The tuple is not aspirational: every letter names something
a real admission function, a real CLI verb, or a real qualification script actually
computes today, cited in §7. Where a real implementation does not yet compute an
element this RFC specifies as required (most notably: no schema-A registry
computation of G — see §7.2), that gap is named explicitly as **specified, not yet
implemented**, not silently assumed true.

## 5.3 Why this tuple survives a full rewrite

None of `I, G, D, Π, A, Q, E, L` names a programming language, an RDF library, a
template engine, or a wire format. Substitute Rust for Elixir, `oxigraph` for any
other conformant triplestore, Tera for EEx, SHA-256 for BLAKE3 — every letter of the
tuple is still the right question to ask about the resulting pack. §13 states this
explicitly as capability contracts rather than a vendor enumeration; §14 states
explicitly which real, currently-observed mechanisms are *not* part of the invariant
core and could change without requiring a new major version of this RFC.

# 6. Fence — Why Pack Identity, Capability Identity, and Semantic Authority Are Three Different Things

This section exists because the real research grounding this RFC found direct,
first-hand evidence that "pack.toml" is not one schema, and that conflating these
three notions has already produced real, observable divergence across the ecosystem.
Refuting this fence requires showing the three notions collapse to one inside a
*single* real system and boundary — not that they resemble each other across
different systems.

## 6.1 Three real, differently-shaped `pack.toml`-named artifacts exist today

1. **The registry entry the Rust CLI actually reads for `ggen pack {add,list,show,
   search,doctor}`**: `<packs_dir>/<pack_id>.toml`, parsed as
   `ggen_marketplace::packs_registry::types::{Pack, PackFile}`
   (`crates/ggen-marketplace/src/packs_registry/types.rs:1-103`). Fields: `id`,
   `name`, `version`, `description`, `category`, `author`, `repository`, `license`,
   `registry_type`, `packages: Vec<String>` (crate/dependency names — a *capability*
   bundle, not semantic content), `templates: Vec<PackTemplate>`,
   `sparql_queries: HashMap<String,String>`, `dependencies: Vec<PackDependency>`,
   `tags`, `keywords`, `production_ready: bool`, `metadata`. There is **no
   `ontology` field anywhere in this struct**. Eleven real instances exist under
   `/Users/sac/ggen/marketplace/packs/`, e.g. `mcp-rust.toml` (verbatim, §16.1).

2. **The `ggen-marketplace` repository's own pack corpus**:
   `/Users/sac/ggen-marketplace/packs/<name>/pack.toml`, validated by
   `scripts/marketplace.py`'s `inspect_marketplace()`
   (`scripts/marketplace.py:232-327`). Fields checked: only `[pack].name`,
   `.version`, `.description` — but the *directory itself* is required to carry at
   least one `*.ttl` file (root or under `ontology/`) or the pack is refused with
   `ONTOLOGY_SOURCE_MISSING` and dropped from the admitted list entirely
   (`marketplace.py:219-229,313`). This is the corpus with real, admitted semantic
   content — 318 real pack directories as of this writing.

3. **The `ggen` repository's own `packs/<name>/pack.toml`** (e.g.
   `/Users/sac/ggen/packs/mfact-pack/pack.toml`): only `name`, `version`,
   `description` — no `id`, no `category`, no `packages` — and its **only real
   reader is a Python audit script**
   (`/Users/sac/ggen/scripts/audit/sync_pack_inventory.py:66-77`), never the `ggen`
   binary itself. The pack's real content (its own `ontology.ttl`, `templates/`,
   `gates/`, `ggen.toml`) is driven by mechanism (2)'s shape, not by this manifest.

No implementation reads all three as the same type. A registry design that assumes
one unified `pack.toml` will misdescribe at least two of these three real systems.
This RFC's tuple `P` in §5 is deliberately shaped to be satisfiable by (2), the
`ggen-marketplace` corpus, without literally being (1) or (3) — because (2) is the
only one of the three whose admission law today enforces every element the RFC
requires.

## 6.2 Pack identity ≠ capability identity

`packages: Vec<String>` in schema (1) — a bundle of crate/dependency names such as
`["rmcp", "axum", "tokio"]` (verbatim from `mcp-rust.toml`) — names *what a
generated consumer needs installed*. It says nothing about the pack's own admitted
semantic content. A pack can validly declare capability identity (I want to help you
depend on `axum`) with zero grounding graph (schema (1) enforces none). This RFC
requires (§12, R4) that any pack claiming semantic authority MUST carry a grounding
graph, but explicitly does not require every pack to claim semantic authority —
a pure capability-bundle pack is a legitimate, narrower kind of pack, distinguished
by `G = ∅`.

## 6.3 Pack identity ≠ semantic authority

`marketplace.py`'s `PACK_CLASSES` dict (lines 59-70) assigns a portfolio-taxonomy
label (`CompatibilityPack`, `ProfilePack`, `KernelPack`, `EvidencePack`,
`CapabilityPack`) to exactly 9 of 318 real packs — a sparse, deliberately
non-exhaustive, human-curated organizational label. `docs/reference/pack-classes.md`
states explicitly (lines 94-102) that this classification is **not wired into any
generation-affecting computation**. This RFC's R13 (§12) makes that a MUST going
forward, not merely a present-day accident: a pack's organizational label is
identity metadata, never semantic authority, and no admission, qualification, or
generation step MAY branch on it.

## 6.4 Pack profile ≠ declared field — it is filesystem-shape-derived

`Pack.profile` (`marketplace.py:106-112`) is a computed property, not a manifest
field:

```math
\boxed{
\text{profile}(P) =
\begin{cases}
\text{project}    & \text{if } (P/\text{ggen.toml}).\text{is\_file()} \\
\text{projection} & \text{else if } P.\text{templates} \neq \emptyset \\
\text{semantic}   & \text{otherwise}
\end{cases}
}
```

Verified against the real corpus: 123 project-profile, 153 projection-profile, 42
semantic-profile, 123+153+42=318, exhaustive and disjoint. A pack cannot lie about
its own profile in its manifest, because no manifest field for profile exists to
lie in — this is a genuinely load-bearing design choice this RFC preserves (§12,
R-implicit via §7.3), not incidental.

## 6.5 Active scope ≠ admission validity ≠ trust tier

`marketplace.active.toml`'s `[active].packs` list (12 real entries today) is a
**curation** decision — which admitted packs are in the currently-promoted set —
completely independent of (a) whether a pack is admission-valid (any of the 318 can
be, regardless of active-scope membership) and (b) what trust tier it was installed
at (`TrustTier::Experimental` floor for any locally-installed pack via
`install_pack_by_id_with_profile`, `crates/ggen-marketplace/src/marketplace/
install.rs:1711,1767,1775`, regardless of anything the pack's own manifest claims —
schema (1)'s `Pack` struct has no `trust_tier` field to claim one with in the first
place). Three independent axes; conflating any two of them misrepresents a real,
observed property of at least one real system.

# 7. Real Grounding for Each Tuple Element

## 7.1 I — Identity

**Directory-bound (ggen-marketplace corpus):** `Pack.name` MUST equal the containing
directory's basename or admission refuses `PACK_DIRECTORY_IDENTITY`
(`marketplace.py`, `inspect_marketplace`). **Filename-bound, not
name-cross-checked (ggen CLI registry):** the loader resolves
`<packs_dir>/<pack_id>.toml` by the requested `pack_id`
(`packs_registry/metadata.rs:65-100,147-149`) — the `id` field inside the file is
not independently re-derived from the filename in the code paths read for this RFC.
This RFC's R1 (§12) requires directory/filename-independent re-derivability of
identity for any registry claiming I-conformance; today only the marketplace corpus
enforces it.

## 7.2 G — Grounding graph

REQUIRED by the marketplace corpus (`ONTOLOGY_SOURCE_MISSING` refusal,
`marketplace.py:219-229`). Loaded, at the engine layer, via `oxigraph`
(`= "0.5.8"`/`"0.5.9"` across `ggen-marketplace`, `ggen-engine`, `ggen-graph`
`Cargo.toml`s) as `RdfFormat::Turtle` (confirmed call sites:
`crates/ggen-engine/src/graph.rs:57`; `crates/ggen-graph/src/dialect.rs:23,72,230`;
`crates/ggen-graph/src/shacl.rs:44`) and, on one replay/mirror path, `RdfFormat::
NQuads` (`graph.rs:1228`). **NOT present as a field or a check in schema (1)** — the
CLI-facing registry's own `Pack` struct has no ontology field at all. This is the
single most important honest gap this RFC names: a pack admitted by `ggen pack add`
today can carry zero grounding graph.

SHACL/ShEx validation of the graph is real but **engine-conditional**, not
universal: the default `GraphLawStore` engine implements
`validate_shacl`/`validate_shex` for real (`crates/ggen-engine/src/graph.rs:
1087-1130`, with real passing tests, e.g. `graphlaw_validate_shacl_flags_focus_node`,
~lines 1596-1628); the alternate `oxigraph`-engine variant explicitly refuses:
`Err(AppError::fm_law(2, "the oxigraph engine has no SHACL support..."))`
(`graph.rs:870-876`). §13.1 states this engine-conditionality as a capability
contract, not a universal guarantee.

## 7.3 L (profile component) — see §6.4 above; not duplicated here.

## 7.4 D — Declared composition

`PackDependency { pack_id: String, version: String, optional: bool }`
(`types.rs:63-69`) — `version` is a bare, unconstrained `String`. No
`semver::VersionReq` range-matching call site was found anywhere under
`crates/ggen-marketplace/src` (zero `grep` hits for `VersionReq`); real
`semver::Version` exact-parsing is used elsewhere (`install.rs:266`, `ownership.rs:
179-180,218`), but no transitive dependency *resolver* over `PackDependency` lists
was confirmed — `packs_registry/dependency_graph.rs` exists but was not opened in
the grounding research; this RFC treats transitive dependency resolution as **an
open question, not a confirmed capability** (see §15, item 5). `.ggen/packs.lock`'s
own `LockedPack.dependencies: Vec<String>` (`crates/ggen-marketplace/src/packs/
lockfile.rs:131`) likewise carries bare IDs with no version constraint recorded.

The one real, filesystem-path composition mechanism that *is* confirmed to
generate real output is `ggen.toml`'s `[[packs]]` table
(`crates/ggen-config/src/manifest/types.rs:54-69`, real syntax at
`packs/clap-noun-verb-zeroconfig-pack/ggen.toml:13-19` — six sibling-pack path
references) — see §10 for its composition semantics.

## 7.5 Q — Qualification contract

Owned entirely by `ggen-marketplace`'s `scripts/qualify_packs.py`
(`qualify_pack()`, lines 555-685), **not** part of the Rust CLI's own admission
path. Real steps: fingerprint pack source before → build an isolated tempdir
capsule per profile → run `ggen sync run` (pass 1, 5s-bounded subprocess) → snapshot
the output tree (SHA-256 per file) → run `ggen sync run` again (pass 2) → snapshot
again → **byte-for-byte digest comparison**; any difference refuses
`GGEN_PACK_NONDETERMINISTIC_REPLAY` with the changed-path list. A final re-check of
the *source* fingerprint refuses `GGEN_PACK_SOURCE_MUTATED` if qualification itself
touched the admitted source. This RFC specifies Q's contract abstractly in §12 (R7,
R8, R9) without requiring this document's author to build, extend, or modify the
real script that implements it — building the actual qualification *court* (test
corpus, CI wiring, coverage targets) is explicitly out of scope; see §19.

## 7.6 Π — Projections

Query capability: SPARQL, real via `oxigraph`, expressed as `gates/*.rq` files in
the marketplace corpus (split `native_gates` (`.rq`) vs. `verifier_gates` (`.py`) by
suffix, `marketplace.py`'s `GATE_SOURCE_EXTENSION` check), or `sparql_queries:
HashMap<String,String>` in schema (1), or `QuerySource::Pack{pack,output,file}` in
`ggen.toml` generation rules (`manifest/types.rs:453-528`). Render capability: Tera
(`= "1.20.0"`, `crates/ggen-engine/Cargo.toml:75`) for the Rust pipeline
(`templates/*.tmpl|*.tera`, `TEMPLATE_SUFFIXES` check in the marketplace corpus),
**or** EEx for the independent Elixir reimplementation in `ggen_igniter`
(`priv/ggen/<pack-name>/templates/*.eex` — README.md:70-100 and `lib/ggen_igniter/
pack.ex:3-12`). Two real, independently maintained render engines already satisfy
the same abstract "render capability" today — direct, in-repo grounding for §13.2's
capability-contract framing, not a hypothetical.

## 7.7 E — Evidence

At least five real, non-unified digest mechanisms exist across the two repos
grounding this RFC: `sha256_file` (per-file SHA-256, `marketplace.py:159-164`);
`fingerprint_paths` (canonical length-prefixed SHA-256 over a sorted path/content
concatenation, `marketplace.py:167-177`, used for both a pack's own
`ontology_fingerprint_sha256` and the whole-corpus fingerprint); `build_pack_archive`
(deterministic PAX tar.gz, then SHA-256 of the archive bytes as the catalog
`digest`, `marketplace.py:180-197`); `qualify_packs.py`'s independent
`snapshot_tree`/`snapshot_digest` scheme (lines 108-130), purpose-built for
before/after mutation detection, not the same code path as the catalog digest; and
`ggen.lock`'s own `blake3:`-prefixed content hash
(`/Users/sac/ggen-marketplace/ggen.lock`, repo root, 5 real lines) — a
genuinely different algorithm from every SHA-256 mechanism above. `.ggen/keys/
{signing.key,verifying.key}` exist on disk but their consuming code path was **not
located** in the grounding research — this RFC does not assert a signing mechanism
beyond the digest schemes actually confirmed (see §15, item 1). §13.3 frames E as a
capability contract (reproducible content-addressability) rather than mandating
SHA-256 or BLAKE3 specifically.

## 7.8 L (trust-tier component)

Two divergent real admission paths exist in `crates/ggen-marketplace/src/
marketplace/install.rs`: `Installer::install` (lines ~372-460,543-598,696-706)
mandates Ed25519 signature verification ("mandatory for all pack installations,"
~line 435) plus checksum verification; the path the CLI's actual `ggen pack add` /
`ggen agent install` use, `install_pack_by_id_with_profile` (lines 1699-1784), sets
`RegistryClass::PrivateEnterprise{require_signature:false, allow_unlisted:true}`
for local/bare-id packs and floors every such pack at `TrustTier::Experimental`
(lines 1711,1775) regardless of any tier the manifest might claim — because schema
(1)'s `Pack` struct has no `trust_tier` field to claim one with. With the CLI's
actual default (`profile = None` — note this is the CLI's own
`marketplace::profile::Profile` trust-policy struct, e.g. a "Fortune-5-CISO"
enforcement policy; it is a different, unrelated real type from this RFC's
pack-shape `profile` defined in §4/§6.4, and the collision is the real
codebase's own naming, not introduced by this RFC), only an explicitly
`Blocked`-tier pack is refused (`install.rs:1142`). §12 R12 makes disclosure of
this floor a MUST for any registry claiming L-conformance.

# 8. Relationship to Prior Ecosystem House Style (RFC-SA2A-001/002)

Direct, verified search found **no `rfc/` directory precedent inside
`ggen-marketplace` itself** — the repo's own real conventions for a binding
design/decision document are `docs/adr/ADR-NNNN-kebab-title.md` (5 real ADRs exist,
ADR-0001 through ADR-0005, each Status/Context/Decision/Consequences-shaped) and
`docs/jira/vX.Y.Z/NN-TICKET-title.md` for milestone-scoped tickets. This document
follows neither pattern exactly; it instead adopts the real `RFC-SA2A-NNN` naming
and internal house style found in `/Users/sac/ash_a2a/docs/rfc/` (RFC-SA2A-001,
RFC-SA2A-002 "Chicago", both v26.9.16), because the task producing this document was
explicitly scoped as an RFC, and that is the only real RFC-shaped precedent found
anywhere on this filesystem.

**What this RFC deliberately borrows**, because it is genuinely convergent with this
user's own standing doctrine (`~/CLAUDE.md`), not decoration:

- The **falsifier format** applied to every normative requirement (§3, §12) —
  RFC-SA2A-002 §11's exact field list (invariant / exact subject / stimulus /
  boundary / forbidden standing / positive evidence of attempt / evidence of
  survival).
- The **standing vocabulary** — `UNKNOWN, PARTIAL_ALIVE, ALIVE, BLOCKED,
  BUILD_BROKEN, UNSUPPORTED, REFUSED` — used identically in RFC-SA2A-002 §23, in
  this user's `~/CLAUDE.md`, and in `~/.claude/rules/no-overclaiming-rust.md`; used
  identically again in this document's §15 and §19.
- The **repair discipline** (RFC-SA2A-002 §118's 8-step list) and the **layered
  verification ladder** (§143), both near-identical to this user's own
  `~/CLAUDE.md` "Repair" and "Verify ladder" doctrine.
- The Zero-Mock discipline named in RFC-SA2A-002 §10 ("For Chicago Crown gates, the
  load-bearing path MUST NOT depend on `Mock`... Mocks MUST NOT be used as the sole
  evidence for standing") — nearly identical wording to this user's own personal
  `~/.claude/rules/testing-chicago-style.md`, confirming real, pre-existing lineage
  between the two, not a borrowing invented for this document.

**What this RFC does NOT claim:** no ggen-specific normative text exists anywhere
in either real RFC-SA2A document — `grep -n -i "ggen"` against both canonical files
returns zero matches. RFC-SA2A-002 §113 states generically that courts "SHOULD be
generated or parameterized from canonical semantic requirements where practical
rather than hand-maintained independently of them," naming no specific generator.
The only place `ggen` and RFC-SA2A meet on this filesystem is a **gap finding** in
a separate, independently authored document
(`/Users/sac/autofde-lab/docs/rfcs/RFC-SA2A-002-compliance-matrix.md`), which
reports that RFC-SA2A-002's own conformance courts are "hand-written Python
modules, not ggen-generated projections." This RFC therefore cannot honestly present
itself as extending an existing ggen-SA2A convention — none exists — only as filling
a documented gap using SA2A's own generic principle and directly borrowed house
style. This RFC also does **not** adopt the user's personal
Preserve/Fence/Calculus/Exclusions/Falsifier/Extension/Operationalize (守/柵/算/
除/偽/延/実) section-naming pattern as an SA2A convention — it was confirmed absent
from both real RFC-SA2A documents (searched explicitly; not found) — this document's
own §5/§6/§10/§11/§12 structure applies that pattern as an explicit import from the
user's own personal doctrine, named honestly as such, not presented as continuing
established RFC-SA2A style.

The `\boxed{}`-wrapped math-block convention, the flat section numbering
(`# N. Title`, no nested H2 chapters except where genuinely tabular), and the fenced
` ```text ` vocabulary-enumeration convention are all borrowed directly from the real
RFC-SA2A documents and applied here without alteration.

# 9. Admission Law A — Three Real, Non-Unified Gates

This RFC does not define a fourth admission function. It names the three that
exist, states which properties of `P` (§5) each one actually checks, and requires
(§12, R-various) that any future unified admission law be at least as strict as the
union of checks already load-bearing in at least one real system today.

```text
Gate 1 — marketplace.py::inspect_marketplace()   (ggen-marketplace corpus, repo-wide)
  checks: I (directory identity), manifest presence/parseability, version SemVer,
          description non-empty, G presence (>=1 .ttl), template-suffix well-
          formedness, gate-suffix well-formedness, no symlinks under packs/.
  scope:  all-or-nothing at the REPOSITORY level — one bad pack fails the whole
          corpus (require_admitted(), SystemExit(2) on any issue).

Gate 2 — ggen_marketplace::packs_registry::validate::validate_pack()   (Rust CLI,
          `ggen packs validate`)
  checks: has_name, has_description, has_packages (WARNING only, not blocking),
          version validity (hand-rolled 3-part splitter, NOT the real `semver`
          crate despite it being a real dependency of the same crate), has_content.
  scope:  per-pack, scored 0-100, `valid = errors.is_empty()` — a real, disclosed
          gap: this gate does not check G at all (schema (1) has no G field).

Gate 3 — install_pack_by_id_with_profile() trust-tier evaluation   (Rust CLI,
          `ggen pack add` / `ggen agent install` actual default path)
  checks: only whether the pack's tier (if any) is `Blocked`; everything else is
          floored at `TrustTier::Experimental` for local/unsigned packs.
  scope:  per-install-attempt; signature/checksum verification exists but on a
          DIFFERENT code path (`Installer::install`) than the CLI's actual default.
```

No single one of these three gates checks everything `P` requires. This RFC's own
requirements (§12) are written against the union of what a conformant future gate
MUST check — not against any one of the three as currently implemented.

# 10. Calculus — Pack Composition

## 10.1 The composition operator

```math
\boxed{
P_1 \oplus P_2 \text{ is legal} \iff
\text{Resolvable}(P_1.D \to P_2) \land \text{Admitted}(P_2, A) \land \neg\text{Cyclic}(P_1, P_2)
}
```

**`Resolvable`** — the ONE real, confirmed mechanism: a project-profile pack's own
`ggen.toml` `[[packs]]` table names a sibling pack by relative filesystem path
(verbatim, `packs/clap-noun-verb-zeroconfig-pack/ggen.toml:13-19`:
`clap-noun-verb-schema-pack = { path = "../clap-noun-verb-schema-pack" }`). At
generation time this resolves through `ggen`'s own manifest loader; at qualification
time, `qualify_packs.py`'s `copy_composed_packs()` (lines 356-416) makes the same
relative path resolve correctly inside an isolated capsule, with its own
escape-check requiring the composed pack's source to resolve *under* the packs
root.

**`Admitted(P_2, A)`** — this RFC specifies (R11, §12) that a composed pack MUST
itself independently satisfy admission before being composed. Whether the real
`ggen.toml [[packs]]` path-resolution code path *re-runs* admission on `P_2` at
generation time was **not confirmed** in the grounding research (only the
qualification-side `copy_composed_packs` escape-check was directly read) — this RFC
treats it as an open question (§15, item 6), not a settled fact.

**`¬Cyclic`** — no confirmed evidence either way that the real implementation
detects a composition cycle (P1 depends on P2 depends on P1). This RFC specifies it
as a MUST (R11) without claiming it is enforced today.

## 10.2 Semantic-graph composition is explicitly UNSUPPORTED today

`Resolvable` above is filesystem/path composition — it makes P2's *files* available
to P1's generation rules. It is **not** the same as unioning P1's and P2's own
`ontology.ttl` graphs at the RDF level. The grounding research confirmed this
directly and independently, not by assumption:

- `qualify_packs.py`'s `write_semantic_consumer`/`write_projection_consumer`
  (lines 301-343) union only a pack's *own* `ontology.ttl` files plus its *own*
  `qualification/consumer.ttl` fixture — never a sibling pack's real ontology.
- The one apparent escape hatch, `qualification_extra_ontologies`, is
  escape-checked (lines 214-227) to require the path resolve **inside** the pack's
  own directory (`source.relative_to(pack_root)`) — it structurally cannot reach a
  sibling pack's graph.
- When a pack's ontology *does* reference another pack's typed individual, the
  real lint `check_cross_pack_references.py` flags it as `CROSS_PACK_REFERENCE_
  UNQUALIFIED` — a violation, not a supported pattern — with the documented fix
  being a **local synthetic stub**, not a real cross-pack graph union (worked
  example: `packs/standing-ladder-pack/pack.toml:22-28`).
- `pack-compatibility-pack`'s `pc:dependsOnComponent` graph exists and *could*
  model pack-to-pack edges by its own class comment, but every real individual
  populated today (`pc:GgenRuntimeRequirement`, `pc:ReactorRequirement`,
  `pc:SparkRequirement`) names an **external** runtime component, never another
  marketplace pack — and its only two consumers (`check_pack_compatibility.py`,
  `pack_dependency_order.py`) are a semver-bound checker and a topo-sort, neither
  of which unions two packs' RDF graphs.

```math
\boxed{
\text{SemanticCompose}(P_1, P_2) : \texttt{UNSUPPORTED\_CAPABILITY}
\quad\text{(specified below, not implemented anywhere in this ecosystem today)}
}
```

This RFC specifies, as future work (§19), the abstract shape a real semantic
composition mechanism would need (an explicit, admitted `imports`/`requires`
declaration at the ontology level, independently admitted, with its own conflict
and cycle law) — but does **not** claim any such mechanism exists, and does not
build one in this pass. See R14 (§12) for the normative honesty requirement this
gap implies: a registry MUST NOT represent two packs as semantically composed
unless a real mechanism actually performs the union.

## 10.3 Legal vs. illegal pack morphisms — real REFUSED classes

```text
REFUSED_IDENTITY        — directory/filename identity mismatch
                           (marketplace.py: PACK_DIRECTORY_IDENTITY)
REFUSED_STRUCTURE        — manifest missing/invalid, bad file-type in templates/ or
                           gates/, symlink present
                           (marketplace.py: MANIFEST_MISSING, MANIFEST_INVALID,
                           MANIFEST_PACK_TABLE, PACK_NAME, PACK_VERSION_SEMVER,
                           PACK_DESCRIPTION, TEMPLATE_EXTENSION,
                           GATE_SOURCE_EXTENSION, PACK_SYMLINK)
REFUSED_SEMANTIC          — grounding graph required by profile but absent
                           (marketplace.py: ONTOLOGY_SOURCE_MISSING)
REFUSED_COMPOSITION       — declared [[packs]] reference does not resolve, or the
                           composed pack is itself not admitted
                           (specified by this RFC; no single real error string
                           confirmed for the general case — see §15, item 6)
REFUSED_REPLAY            — second manufacture pass diverges byte-for-byte from
                           the first
                           (qualify_packs.py: GGEN_PACK_NONDETERMINISTIC_REPLAY)
REFUSED_PROVENANCE        — qualification itself mutated the admitted pack source
                           (qualify_packs.py: GGEN_PACK_SOURCE_MUTATED)
REFUSED_QUALIFICATION_RUN — the sync pipeline itself failed inside the
                           qualification capsule
                           (qualify_packs.py: GGEN_PACK_SYNC_FAILED,
                           GGEN_PACK_PROBE_MISSING,
                           GGEN_PACK_GENERATED_BUILD_FAILED,
                           GGEN_PACK_GENERATED_TEST_FAILED)
BLOCKED_TRUST_TIER        — pack's tier is explicitly Blocked
                           (install.rs: TrustTier::Blocked check, line ~1142)
UNSUPPORTED_CAPABILITY    — the requested operation names a real capability this
                           RFC defines but no admitted implementation satisfies
                           today (e.g. semantic-graph composition, §10.2)
```

The first eight are grounded in real, currently-emitted strings from at least one
real implementation; `REFUSED_COMPOSITION` is this RFC's own specification for a
gap where the real behavior was not confirmed (§15, item 6) — named honestly as
specified-not-confirmed, not as an observed string.

# 11. Fence — Law vs. Court

This RFC is **law**: the tuple `P` (§5), the admission gates as they really exist
(§9), and the composition algebra (§10). It is deliberately **not** a **court**: it
does not define, and this pass does not build, a qualification corpus, a
conformance-test harness, test-ID namespaces, or CI wiring beyond what already
exists in `qualify_packs.py`. The real, running qualification script is cited
throughout (§7.5, §10) as grounding for what a *future* court-defining document
should hold itself to — not as something this document extends or modifies. See
§19 for the explicit deferral of that work to `RFC-GGEN-002` (or a similarly
numbered, not-yet-written document).

# 12. Normative Requirements

Each requirement states the MUST/SHOULD, then a compact falsifier block:
**Invariant**, **Subject**, **Stimulus**, **Boundary**, **Forbidden**, **Evidence
attempted**, **Invalid pass**.

## R1 — Identity Independently Re-derivable (MUST)

A pack's declared identity MUST be independently re-derivable from its location in
a registry, without trusting the manifest's own self-report alone.

- **Invariant:** `location(P) \Rightarrow I(P)` is checkable without parsing `P`'s
  manifest content.
- **Subject:** any admitted pack in a registry claiming I-conformance.
- **Stimulus:** rename a pack's directory without updating its manifest name.
- **Boundary:** the registry's admission law.
- **Forbidden:** admission succeeds with the stale, now-wrong name.
- **Evidence attempted:** the check must actually compare directory basename to
  manifest name (grounded: `PACK_DIRECTORY_IDENTITY`, `marketplace.py`).
- **Invalid pass:** admission refuses for an unrelated reason (e.g. a coincidental
  parse error) without ever exercising the identity comparison.

## R2 — Manifest Presence and Parseability (MUST)

- **Invariant:** every admitted pack root has a parseable manifest naming at
  minimum `{name, version, description}`.
- **Subject:** any candidate pack tree.
- **Stimulus:** delete or syntactically corrupt the manifest.
- **Boundary:** admission (Gate 1, §9).
- **Forbidden:** silent exclusion from a catalog with no observable refusal record.
- **Evidence attempted:** `MANIFEST_MISSING`/`MANIFEST_INVALID` refusal codes
  actually fire (grounded: `marketplace.py`).
- **Invalid pass:** the pack disappears from a listing with no logged reason.

## R3 — Version Identity Is Real SemVer (MUST)

- **Invariant:** `version` is a valid SemVer 2.0.0 string.
- **Subject:** any admitted pack's `version` field.
- **Stimulus:** set `version = "1.0"` (two components, not three).
- **Boundary:** admission.
- **Forbidden:** acceptance by a partial or non-standard grammar.
- **Evidence attempted:** the check is run against the real string, not skipped.
- **Invalid pass:** acceptance by a hand-rolled 3-part-splittable check that is
  *not* the real SemVer grammar — **this is a currently real, confirmed
  nonconformance**: Gate 2 (§9)'s `is_valid_semver`
  (`packs_registry/validate.rs:125-133`) is a hand-rolled
  splits-into-3-u32-parseable-parts check, not the real `semver` crate, despite
  `semver = "1.0"` being a genuine dependency of the same crate
  (`Cargo.toml:54`). This RFC records this as a known gap in Gate 2 specifically
  (Gate 1's real regex, `marketplace.py:31-35`, is closer to full SemVer 2.0.0
  shape but was not exhaustively tested against build-metadata edge cases either
  — see §15, item 3).

## R4 — Grounding Graph Required Where Semantic Authority Is Claimed (SHOULD)

- **Invariant:** a projection- or semantic-profile pack SHOULD carry ≥1 admitted
  RDF document.
- **Subject:** a pack whose profile (§6.4) is `projection` or `semantic`.
- **Stimulus:** admit a projection-profile pack (has `templates/`, no `ggen.toml`)
  with zero `.ttl` files anywhere.
- **Boundary:** admission.
- **Forbidden:** silent acceptance as a "semantic" pack with no semantic content.
- **Evidence attempted:** `ONTOLOGY_SOURCE_MISSING` fires (Gate 1 does this today).
- **Invalid pass:** the pack is accepted by a *different* registry gate (Gate 2,
  §9) that never checks G at all — **this is the honest, real, present-day gap**:
  a schema-(1) pack installed via `ggen pack add` today can have zero grounding
  graph and still install successfully, because Gate 3's trust-tier check does not
  examine G either. This requirement is SHOULD, not MUST, specifically because it
  is not universally enforced today across all three real gates — the RFC records
  the target state honestly without claiming it is already reached.

## R5 — Structural File-Type Constraints (MUST)

- **Invariant:** `templates/` (if present) contains only the pack's declared
  template suffixes; `gates/` (if present) only recognized query/verifier suffixes.
- **Subject:** the `templates/` and `gates/` directories of any candidate pack tree.
- **Stimulus:** drop a `.py` file into `templates/`.
- **Boundary:** admission (Gate 1, §9).
- **Forbidden:** acceptance.
- **Evidence attempted:** `TEMPLATE_EXTENSION` fires (grounded: `marketplace.py`).
- **Invalid pass:** the check inspects only the first file found, not every file.

## R6 — No Symlinks in an Admitted Pack Tree (MUST)

- **Invariant:** no file under an admitted pack root is a symlink.
- **Subject:** any file under a candidate pack tree.
- **Stimulus:** symlink a file inside the pack tree to a target *outside* the pack
  root whose content, if followed, would itself pass every other check.
- **Boundary:** admission (Gate 1, §9).
- **Forbidden:** acceptance.
- **Evidence attempted:** `PACK_SYMLINK` fires on the link's *existence*, not its
  target's content (grounded: `marketplace.py`) — the falsifier is specifically
  constructed so a content-only check would be fooled and a link-aware check would
  not, isolating which property is actually being tested.
- **Invalid pass:** the check only fires when the symlink target is itself invalid,
  proving it checks content, not link-ness.

## R7 — Determinism Under Re-Manufacture (MUST)

- **Invariant:** identical inputs re-run through the generation pipeline produce
  byte-identical outputs.
- **Subject:** any pack's projection (Π).
- **Stimulus:** introduce a non-deterministic element into a template (unordered
  map iteration surfacing in rendered output, or a wall-clock timestamp).
- **Boundary:** qualification (Q), pass 1 vs. pass 2.
- **Forbidden:** the second pass silently diverges without detection.
- **Evidence attempted:** `snapshot_tree`'s SHA-256-per-file comparison actually
  runs on both passes and the digests are actually compared (grounded:
  `qualify_packs.py:555-685`, and independently corroborated by five real, passing
  determinism tests in `ggen-engine` — `projection_determinism_test.rs:46-99`,
  `sync_e2e.rs:38-89`, `multi_template_determinism.rs:96-181`,
  `cross_pack_matrix.rs:164-206`, `receipt_signing_evidence_test.rs:69-107`).
- **Invalid pass:** the comparison checks file *existence/count* only, not content
  digest — the real implementation is confirmed to do byte-for-byte digest
  comparison, ruling this failure mode out today.

## R8 — Qualification Must Not Mutate Source (MUST)

- **Invariant:** running qualification does not alter the pack's own admitted
  source tree.
- **Subject:** any pack undergoing qualification (Q, §7.5).
- **Stimulus:** have the qualification process write a stray file directly into
  the pack's source directory instead of the isolated capsule.
- **Boundary:** qualification, before/after source fingerprint.
- **Forbidden:** the mutation goes undetected.
- **Evidence attempted:** `pack_source_fingerprint` is re-computed after
  qualification and compared to the pre-qualification fingerprint (grounded:
  `qualify_packs.py:108-130,555-685`, refusal `GGEN_PACK_SOURCE_MUTATED`).
- **Invalid pass:** the fingerprint excludes a directory the mutation targets —
  the real, disclosed exclusion list is `.git/.ggen/.ggen-v2/.cache/
  .qualification-home/target`; this RFC records that list as the current, honest
  scope of R8, not a hidden gap, and requires (as a SHOULD) that any expansion of
  legitimately-mutable directories be disclosed in the same place.

## R9 — Qualification Isolation (SHOULD)

- **Invariant:** qualifying one pack does not depend on another, undeclared pack's
  ambient presence.
- **Subject:** a project-profile pack undergoing qualification (Q) with a declared
  `[[packs]]` composition.
- **Stimulus:** qualify a project-profile pack in an environment containing an
  extra, undeclared sibling pack; then again in an environment without it.
- **Boundary:** qualification capsule construction (`copy_composed_packs`).
- **Forbidden:** the two runs disagree (a "worked on my machine" false pass).
- **Evidence attempted:** the qualification capsule copies only the pack itself
  plus explicitly `[packs]`-declared siblings (grounded:
  `copy_composed_packs()`, `qualify_packs.py:356-416`).
- **Invalid pass:** qualification succeeds only because the undeclared sibling
  happened to be present in the ambient filesystem, not because it was genuinely
  unneeded.

## R10 — Active-Scope List Well-Formedness (MUST)

- **Invariant:** a curated "active" pack list is non-empty, deduplicated, and
  names only packs present in the underlying corpus.
- **Subject:** `marketplace.active.toml`'s `[active].packs` array.
- **Stimulus:** add a duplicate entry, or an unknown pack-id, to
  `marketplace.active.toml`'s `packs` array.
- **Boundary:** active-scope resolution (`select_packs()`).
- **Forbidden:** the malformed list is accepted.
- **Evidence attempted:** `select_packs()`'s ordering/dedup/existence checks
  actually run against the real corpus (grounded: `marketplace_scope.py:30-60`).
- **Invalid pass:** refusal fires only for an unrelated reason (e.g. a TOML
  parse error) without genuinely exercising dedup or existence checking.

## R11 — Composition Path Resolution Is Bounded (MUST)

- **Invariant:** a declared cross-pack path reference resolves without leaving the
  registry's defined boundary, admits its target independently, and introduces no
  composition cycle.
- **Subject:** a pack's `[[packs]]` composition reference, or a qualification
  `extra_ontologies` path.
- **Stimulus:** declare a `[packs]` path (or a qualification `extra_ontologies`
  path) that escapes the pack root (e.g. `"../../../etc"`).
- **Boundary:** composition path resolution (generation-time `[[packs]]`
  resolution, or qualification capsule construction).
- **Forbidden:** the escape resolves successfully.
- **Evidence attempted:** an escape-check runs (confirmed real for
  `extra_ontologies`, `qualify_packs.py:214-227`, `source.relative_to(pack_root)`).
- **Invalid pass:** the escape-check is confirmed for only ONE of the two real
  path-accepting mechanisms — this RFC records, as an honest open question (§15,
  item 6), that `ggen.toml [[packs]]` path resolution's own escape behavior was
  **not directly confirmed** in the grounding research, and that whether a
  composed pack is independently re-admitted at generation time is likewise
  unconfirmed. R11 is stated as a MUST for the law; its present-day enforcement is
  only partially verified.

## R12 — Trust-Tier Floor Must Be Disclosed (MUST)

- **Invariant:** a pack admitted without positive signature/checksum verification
  is recorded at a disclosed, non-default trust tier — never silently equated to a
  signed pack.
- **Subject:** any pack installed via a local/unsigned admission path.
- **Stimulus:** install a local, unsigned pack via the CLI's actual default path.
- **Boundary:** install-time trust-tier evaluation (Gate 3, §9).
- **Forbidden:** the resulting receipt/lockfile is indistinguishable from a signed
  pack's.
- **Evidence attempted:** `TrustTier::Experimental` is actually recorded (grounded:
  `install.rs:1699-1784`, floor lines 1711,1775).
- **Invalid pass:** the lockfile (`.ggen/packs.lock`, `LockedPack`,
  `lockfile.rs:116-131`) omits trust tier entirely — this RFC notes the real
  `LockedPack` struct as read in the grounding research does not carry an explicit
  trust-tier field among the fields confirmed (`version, source, integrity,
  installed_at, dependencies`); recording trust tier durably is therefore itself a
  gap this requirement names, not assumed satisfied.

## R13 — Portfolio Classification Must Not Affect Behavior (SHOULD, hardening to MUST going forward)

- **Invariant:** a pack's organizational classification label never changes
  admission, qualification, or generation behavior.
- **Subject:** any pack carrying (or lacking) a `pack_class` classification label.
- **Stimulus:** assign two packs conflicting or absent classification labels.
- **Boundary:** admission, qualification, and generation, collectively.
- **Forbidden:** the two packs admit, qualify, or generate differently *because
  of* the label.
- **Evidence attempted:** no real pipeline stage reads `PACK_CLASSES` today
  (grounded: `pack-classes.md:94-102`'s own explicit statement, and 309 of 318
  real packs carry `pack_class: null` by design).
- **Invalid pass:** a future refactor silently begins reading the label without
  this requirement's SHOULD-hardened-to-MUST catching it in review.

## R14 — Cross-Pack Semantic Composition Must Not Be Fabricated (MUST)

- **Invariant:** a registry MUST NOT represent two packs as semantically composed
  at the RDF-graph level unless a real, admitted mechanism actually unions their
  graphs.
- **Subject:** a registry or runtime reporting the result of a cross-pack SPARQL
  query.
- **Stimulus:** attempt a SPARQL query in pack A that assumes pack B's individuals
  are silently visible, with no explicit composition declared.
- **Boundary:** query execution / result reporting (not admission).
- **Forbidden:** the query returns zero rows and this is reported as a **pass**
  rather than surfacing the missing composition.
- **Evidence attempted:** the real, deliberate per-pack isolation (§10.2,
  `write_semantic_consumer`/`write_projection_consumer`) is confirmed to union
  only a pack's own graph plus its own fixtures — cross-pack references are
  caught by a real lint (`check_cross_pack_references.py`), not silently ignored.
- **Invalid pass:** a query silently returns zero rows and this is reported as
  "PASS" — this is precisely the failure mode R14 exists to name: the correct
  standing for an attempted-but-unsupported cross-pack query is
  `UNSUPPORTED_CAPABILITY` (§10.3), never a false-positive PASS.

# 13. Extension Model — Capability Contracts, Not Vendor Enumeration

This RFC never writes a closed enum like `rdf_store = "oxigraph" | "..."` for
anything genuinely pluggable. Each contract below names the REFERENCE
implementation honestly, because it is the only one, or one of only a few, real
implementations found — without closing the door on a different one.

## 13.1 Query capability contract

**Contract:** given a grounding graph `G` and a declared query, return a
deterministic, order-stable result set over `G`'s admitted triples/quads.
**Reference implementation:** `oxigraph` (`0.5.8`/`0.5.9`), loading `RdfFormat::
Turtle` and, on one replay path, `RdfFormat::NQuads` (§7.2). SHACL/ShEx validation
is a *further*, engine-conditional capability (§7.2) — a conformant query engine is
NOT required to also provide SHACL validation; a pack or generation rule that
depends on SHACL MUST declare that dependency explicitly (this RFC does not
currently find a declared-dependency mechanism for engine capabilities and records
this as future work, §19).

## 13.2 Render capability contract

**Contract:** given a query result and a template, deterministically produce
output bytes, with no ambient non-determinism (wall-clock time, unordered map
iteration, process/thread identifiers) leaking into the render.
**Reference implementations, plural, both real today:** Tera (`1.20.0`, Rust
pipeline, `.tmpl`/`.tera` suffix) and EEx (Elixir `ggen_igniter` pipeline,
`.eex` suffix). Neither is privileged by this RFC; a pack's `templates/` directory
declares which suffix family it targets, and a conformant runtime satisfies the
contract for whichever suffix it consumes.

## 13.3 Evidence/digest capability contract

**Contract:** a pack's identity MUST be reproducibly bindable to a content digest
over its admitted files, computed deterministically (stable file ordering, no
embedded timestamps in the digested bytes).
**Reference implementation:** SHA-256 over a canonical sorted-path/content
concatenation (`fingerprint_paths`, `marketplace.py:167-177`) is the REFERENCE
algorithm named by this RFC — not the only legal one. `ggen.lock`'s real use of
BLAKE3 for its own content-hash field (§7.7) is direct, in-ecosystem evidence that
a different digest algorithm already coexists validly for a different evidence
surface; this RFC does not mandate unifying them in this pass (see §14).

## 13.4 Admission-law capability contract

**Contract:** a registry's admission law MUST be a pure function of a candidate
pack's own file tree (no network access, no ambient environment beyond what is
explicitly declared), MUST be re-runnable by an independent party without special
privilege, and MUST produce one of {admitted, one of the REFUSED classes in
§10.3}. **Reference implementations:** the three real gates named in §9 — none of
which alone satisfies the full contract this RFC specifies (§9's closing
paragraph); this is named as an open target, not a claim that Gate 1, 2, or 3
alone is already fully conformant.

# 14. What Is Reference-Implementation Detail, Not Invariant Core

Naming this explicitly so a future full rewrite of any of the three real
repositories knows what it is free to change without breaking conformance to this
RFC:

```text
NOT part of the invariant core (may change per implementation):
  - Rust as the CLI's implementation language; Elixir as ggen_igniter's.
  - oxigraph specifically, vs. any other RDF store satisfying §13.1.
  - Tera specifically, vs. EEx or any other renderer satisfying §13.2.
  - SHA-256 specifically, vs. BLAKE3 or any other digest satisfying §13.3.
  - The clap-noun-verb CLI framework and its specific verb/noun surface.
  - The exact 5-second/120-second qualification timing bounds
    (qualify_packs.py's real defaults) — implementation tuning, not law.
  - marketplace.py's specific REFUSED_* string spellings — this RFC's §10.3
    names an abstract refusal-class vocabulary a conformant implementation
    MAY spell differently, provided the underlying invariant is enforced.

IS part of the invariant core (MUST survive a full rewrite):
  - The tuple P = (I, G, D, Pi, A, Q, E, L), §5.
  - Pack identity != capability identity != semantic authority, §6.
  - Profile is filesystem-shape-derived, never a self-declared field, §6.4.
  - Determinism under re-manufacture (R7) and non-mutation of source under
    qualification (R8).
  - Cross-pack semantic composition requires an explicit, admitted mechanism;
    it is never assumed or fabricated (R14, §10.2).
  - A trust-tier floor for unsigned/unverified admission MUST be disclosed,
    never silently promoted (R12).
```

# 15. Real, Honest Open Questions Carried Forward From Grounding Research

Recorded here rather than silently assumed resolved, per this document's own
evidence discipline:

1. `.ggen/keys/{signing.key,verifying.key}` exist on disk; their consuming code
   path was not located. This RFC does not assert a signing mechanism beyond
   §7.7's confirmed digest schemes.
2. Whether `PackDependency`/`.ggen/packs.lock` dependency lists are ever walked
   transitively (a real resolver, vs. just recorded) was not confirmed —
   `packs_registry/dependency_graph.rs` exists but was not opened.
3. Gate 1's real SEMVER regex (`marketplace.py:31-35`) is standard-shaped but was
   not exhaustively tested against build-metadata (`+build.1`) edge cases in the
   real corpus.
4. `GgenIgniter.SchemaDispatch` (the classifier choosing between the
   `FrontmatterConfig` and `ProjectConfig` schema variants in `ggen_igniter`) was
   not read directly; its role is inferred from callers' references to it.
5. No formal, machine-checked version-compatibility contract was found between
   `ggen_igniter` (v26.9.15) and the Rust `ggen` CLI (workspace version 26.8.24 at
   research time) — the only linkage found is an informal, date-stamped
   vendor-copy comment on two NIF source files. This RFC's §13 capability
   contracts are written to be robust to this drift by not depending on version
   numbers, but the drift itself remains a real, unaddressed operational risk this
   document does not resolve.
6. Whether `ggen.toml`'s `[[packs]]` path-resolution code path (a) independently
   re-admits the referenced pack, and (b) escape-checks the path the same way
   `qualify_packs.py`'s `extra_ontologies` does, was **not directly confirmed** —
   named explicitly in R11 (§12) and §10.1 rather than assumed either way.
7. Two independently-defined `ggen.toml` root schemas coexist in the Rust
   codebase — `ggen_config::manifest::types::GgenManifest` (this RFC's primary
   citation source) and a second, structurally different `ggen_engine::config::
   GgenConfig`, selected at runtime by inspecting raw TOML text before either
   typed parse runs, with — in the grounding research's own words — "intentionally
   no automated cross-schema equivalence guard between the two"
   (`manifest/types.rs:159-170`). This RFC's `D` (§7.4) and `[[packs]]` citations
   (§10.1) are grounded in the first schema; a pack manifest parsed under the
   second schema may resolve `[[packs]]` through the different, untagged
   `Path{path,extra_ontologies,lock} | Git{git,version}` enum instead of the flat
   struct shape quoted in §10.1 — this RFC does not claim the two are equivalent,
   and neither does the code it cites.

# 16. Reference Implementations

## 16.1 Real sample manifest — schema (1), CLI-facing registry

Verbatim, `/Users/sac/ggen/marketplace/packs/mcp-rust.toml`:

```toml
[pack]
id = "mcp-rust"
name = "MCP Rust"
version = "1.0.0"
description = "Model Context Protocol server in Rust with Axum"
category = "integration"
author = "ggen"
repository = "https://github.com/seanchatmangpt/ggen"
license = "MIT"
production_ready = true

packages = [
    "rmcp",
    "axum",
    "tokio",
]
```

## 16.2 Real sample manifest — schema (2), ggen-marketplace corpus (G-bearing)

Verbatim, `/Users/sac/ggen-marketplace/packs/pack-maturity-pack/pack.toml`:

```toml
[pack]
name = "pack-maturity-pack"
version = "0.2.0"
description = """
Generates cross-cutting Level-5 promotion infrastructure for any composing
consumer without inventing domain semantics the consumer has not supplied.
...
"""
```

## 16.3 Real composition syntax

Verbatim, `/Users/sac/ggen-marketplace/packs/clap-noun-verb-zeroconfig-pack/
ggen.toml:13-19`:

```toml
[packs]
clap-noun-verb-schema-pack = { path = "../clap-noun-verb-schema-pack" }
clap-noun-verb-crate-pack = { path = "../clap-noun-verb-crate-pack" }
clap-noun-verb-routing-pack = { path = "../clap-noun-verb-routing-pack" }
clap-noun-verb-behavior-pack = { path = "../clap-noun-verb-behavior-pack" }
clap-noun-verb-boundary-pack = { path = "../clap-noun-verb-boundary-pack" }
clap-noun-verb-verification-pack = { path = "../clap-noun-verb-verification-pack" }
```

## 16.4 Real CLI verb surface (Rust)

```text
ggen pack add <pack_name> [--force]
ggen pack remove <pack_name>
ggen pack list [--verbose] [--category <cat>]
ggen pack show <pack_id>
ggen pack search <query> [--limit <n>]
ggen pack related <seed> [--by-category] [--limit <n>]
ggen pack query <sparql> [--pack-id <id>]
ggen pack doctor
ggen pack new <pack_name> --description <desc> --namespace <ns> [--version <v>]

ggen packs install <pack_id>
ggen packs list
ggen packs validate <pack_id>
ggen packs show <pack_id>
```

No `ggen pack qualify` (or any "qualify" verb) exists in the Rust CLI today —
confirmed by an exhaustive grep of `crates/ggen-cli/src` returning zero hits.
Qualification (Q) is entirely `ggen-marketplace`-repo-owned (§7.5).

## 16.5 Real Elixir reference (ggen_igniter, partial reference implementation)

`ggen_igniter` is a genuine, independent, from-scratch **reimplementation** of the
Rust pipeline's shape, not a wrapper that shells out to the real `ggen` binary for
its core work — its own README states this explicitly. It satisfies §13.1's query
contract via a Rustler NIF vendoring the real `ggen-graph-wasm` crate's oxigraph
bindings (with an honest, dated provenance header, not a live path dependency —
`native/ggen_graph_nif/src/oxigraph_engine.rs:1-5`), and §13.2's render contract via
EEx rather than Tera. A separate, real `System.cmd("ggen", ["sync","run"], ...)`
shellout to the actual external `ggen` binary does exist
(`lib/ggen_igniter/sync_shellout.ex:56`), but only on a verification/comparison
path (`GgenIgniter.SyncVerify`) and `mix ggen_igniter.fortune5_ready` — **not** on
the main `mix ggen_igniter.sync` pipeline. This RFC names `ggen_igniter` a
**partial reference implementation**: it satisfies the query and render capability
contracts independently, but its admission law (A) and qualification contract (Q)
were not confirmed to mirror Gates 1-3 or `qualify_packs.py` — its own
`mix ggen_igniter.doctor` and `.plan`/`.verify`/`.replay` tasks implement a
parallel, not-yet-cross-checked-against-this-RFC set of checks.

# 17. The Independent-Implementer Test

This RFC's own conformance bar is stated directly, not left implicit: **two teams
who have never spoken, given only this document plus the real, currently-admitted
`ggen-marketplace` pack corpus (`/Users/sac/ggen-marketplace/packs/`), should
independently arrive at the same answers to three questions for any given pack in
that corpus**:

1. What is this pack's identity `I`, and at what filesystem location is it bound?
2. What is this pack's profile (§6.4), and does it carry a grounding graph `G`?
3. If this pack declares a `[[packs]]` composition, which sibling packs does it
   depend on, and would a change to any of them require re-qualifying this pack?

Disagreement on any of these three, given the same real corpus and this document
alone, is a defect in this RFC, not in either team's reading of it. Section §5
through §10 are held to this bar directly; §15's open questions are the places
this document already knows it might currently fail the bar, named so a future
revision can close them rather than leaving them to be independently
(re)discovered.

# 18. Exclusions

This RFC explicitly does **NOT** standardize:

- **A specific RDF store.** `oxigraph` is named as the reference implementation
  (§13.1) because it is the only one found in the grounding research; a
  conformant alternative satisfying the query capability contract is not
  precluded.
- **A specific template/render engine.** Both Tera and EEx are real, coexisting
  reference implementations (§13.2); neither is privileged.
- **A specific digest/hash algorithm.** SHA-256 is named as reference (§13.3);
  BLAKE3 already coexists validly in the same ecosystem (`ggen.lock`) for a
  different evidence surface.
- **A specific programming language for any reference implementation.** Rust and
  Elixir both currently satisfy real subsets of this RFC's contracts; neither
  language is required by this document.
- **A transport or wire protocol** for fetching packs (`github:`, `hex:`, local
  path, and a network registry all appear in real code; this RFC specifies pack
  *identity and semantics*, not how bytes are fetched).
- **The qualification court itself** — test corpus, CI wiring, coverage targets,
  test-ID namespace. See §11 and §19.
- **Semver-range dependency resolution semantics.** `D` (§7.4, §15 item 2) is
  named as a real, currently-unresolved gap this RFC does not attempt to close by
  specification alone; a future document should address it once the real
  resolver's existence (or absence) is confirmed.
- **A cross-pack semantic (RDF-graph-level) composition runtime.** Named
  explicitly as UNSUPPORTED_CAPABILITY today (§10.2); its abstract shape is
  sketched as future work (§19) but not specified in normative detail here,
  because no real implementation exists yet to ground a normative specification
  against — inventing one now would violate this RFC's own evidence discipline.
- **A signing/PKI scheme.** `.ggen/keys/` exists but its consuming logic was not
  located (§15, item 1); this RFC does not specify signing semantics it cannot
  ground.

# 19. Future Work

Named explicitly, not built in this pass, consistent with the task constraint that
produced this document:

1. **RFC-GGEN-002 (or similarly numbered) — Qualification Court.** A companion
   document specifying the test-ID namespace, falsifier corpus, and CI wiring for
   Q (§7.5, §11), grounded in `qualify_packs.py`'s real, already-running
   manufacture-twice-compare mechanism, in the same relationship RFC-SA2A-002
   ("Chicago") bears to RFC-SA2A-001 in the precedent examined for house style
   (§8) — a court built *from* this law, not merged into it.
2. **Cross-pack semantic composition runtime.** A real implementation (and a
   following normative specification, once one exists to ground it) of an
   explicit, admitted `imports`/`requires` mechanism at the RDF-graph level,
   closing the gap named in §10.2 and R14.
3. **Transitive dependency resolution over `D`.** Confirming, then either
   formalizing or replacing, the real (or absent) resolver behind
   `PackDependency`/`.ggen/packs.lock` (§15, item 2).
4. **Unified admission law.** A single admission function whose checks are at
   least the union of Gates 1-3 (§9), closing the gap where Gate 2 does not check
   `G` (R4) and Gate 2's semver check is non-conformant (R3).
5. **Version-compatibility contract between `ggen`, `ggen-marketplace`, and
   `ggen_igniter`.** Closing §15 item 5's confirmed absence of any machine-checked
   cross-project compatibility statement.
6. **Cross-schema equivalence guard** between `ggen_config::manifest::types::
   GgenManifest` and `ggen_engine::config::GgenConfig` (§15, item 7), which the
   grounding research found the codebase's own comments admit do not currently
   have one.

None of items 1-6 requires, or was performed as part of, this RFC. This document's
own scope ends at the law; the court, the runtime gap-fill, and the resolver
confirmation are named as real, addressable next steps for whoever picks them up
next — human or agent, inside or outside this session.

---

# Appendix A — Compact Algebra

```math
\boxed{P = (I, G, D, \Pi, A, Q, E, L)}
```
```math
\boxed{\text{profile}(P) = \text{project if ggen.toml present, else projection if templates}\neq\emptyset\text{, else semantic}}
```
```math
\boxed{P_1 \oplus P_2 \text{ legal} \iff \text{Resolvable} \land \text{Admitted}(P_2,A) \land \neg\text{Cyclic}}
```
```math
\boxed{\text{SemanticCompose}(P_1,P_2) : \texttt{UNSUPPORTED\_CAPABILITY}}
```
```math
\boxed{\text{Standing}(P) \Rightarrow \text{Identity}(P) \land \text{Structure}(P) \land (\text{Semantic}(P) \lor G=\emptyset\text{ declared}) \land \text{Evidence}(P)}
```

# Appendix B — Real Schema Citation Index

```text
Schema (1) CLI registry Pack/PackFile:
  crates/ggen-marketplace/src/packs_registry/types.rs:1-103

Schema (1) loader (packs-dir resolution, load/list/show):
  crates/ggen-marketplace/src/packs_registry/metadata.rs:17-149

Schema (2) ggen-marketplace corpus admission:
  scripts/marketplace.py:95-138 (Pack dataclass, profile property)
  scripts/marketplace.py:232-327 (inspect_marketplace)
  scripts/marketplace.py:59-70   (PACK_CLASSES)
  scripts/marketplace.py:159-197 (digest mechanisms)

Schema (3) ggen repo-root minimal marker, non-CLI-read:
  /Users/sac/ggen/packs/mfact-pack/pack.toml
  scripts/audit/sync_pack_inventory.py:66-77 (only real reader)

ggen.toml manifest (GgenManifest, [[packs]], GenerationRule):
  crates/ggen-config/src/manifest/types.rs:1-771
  (schema-fork disclosure: lines 159-170)

Qualification (manufacture-twice-compare):
  scripts/qualify_packs.py:108-130 (fingerprint/snapshot)
  scripts/qualify_packs.py:301-343 (per-pack-only consumer union)
  scripts/qualify_packs.py:356-416 (copy_composed_packs)
  scripts/qualify_packs.py:555-685 (qualify_pack core loop)

Trust tier / admission divergence:
  crates/ggen-marketplace/src/marketplace/install.rs:372-460,543-598,
    696-706,1687-1784

Lockfile:
  crates/ggen-marketplace/src/packs/lockfile.rs:93-161

Active scope:
  marketplace.active.toml:1-24
  scripts/marketplace_scope.py:30-60

ggen_igniter parallel pipeline:
  lib/mix/tasks/ggen_igniter.sync.ex:1-360
  lib/ggen_igniter/sync_shellout.ex:1-64
  native/ggen_graph_nif/src/oxigraph_engine.rs:1-5
  lib/ggen_igniter/pack.ex:1-150
  lib/ggen_igniter/project_config.ex:1-150
```

# Appendix C — Refusal / Error Class Index

See §10.3 for the full table and grounding.

# Appendix D — Non-Goals

- This RFC does not certify any specific real pack in the `ggen-marketplace`
  corpus as conformant; it specifies what conformance would mean.
- This RFC does not modify, and was authored under an explicit constraint not to
  modify, `marketplace.active.toml`, `scripts/marketplace.py`, any file under
  `packs/`, or any file in `/Users/sac/ggen` or `/Users/sac/ggen_igniter`.
- This RFC does not introduce a new admission gate, superseding Gates 1-3 (§9); it
  names their union as a future target (§19, item 4).

# Appendix E — Evolution Rule

A future revision of this document MUST restate any requirement it changes with
its own falsifier (§3), MUST NOT silently drop a requirement without stating why
in a dated changelog entry, and MUST re-verify every file:line citation in
Appendix B against the then-current state of the three grounding repositories
before republishing — citations drift, and a stale citation is worse than none,
because it misrepresents confidence.

---

# End of RFC-GGEN-001 v26.9.17
