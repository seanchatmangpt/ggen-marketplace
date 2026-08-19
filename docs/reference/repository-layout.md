# Reference: repository layout

| Path | Contract |
|---|---|
| `marketplace.toml` | Marketplace operational law: source authority, qualification bounds, admitted ggen release identity, platform asset digests, and other centralized execution configuration. Must be admitted before qualification. |
| `packs/` | Canonical admitted reusable pack corpus. |
| `packs/<name>/pack.toml` | Required pack identity (`name`, SemVer `version`, non-empty `description`). |
| `packs/<name>/*.ttl` | Root RDF semantic sources, including conventional `ontology.ttl`. |
| `packs/<name>/ontology/**/*.ttl` | Optional split RDF source tree. |
| `packs/<name>/templates/` | Optional `.tmpl` / `.tera` projection templates. |
| `packs/<name>/gates/` | Optional `.rq` native gates and `.py` bounded verifier gates. |
| `packs/<name>/qualification/` | Optional pack-owned positive qualification fixtures/project overlays. Synthetic admitted inputs, not external observations. |
| `packs/<name>/qualification.toml` | Optional bounded pack-local qualification contract when supported. |
| `packs/<name>/ggen.toml` | Marks a self-contained project-profile pack. |
| `packs/pack-maturity-pack/` | Reusable deterministic-regeneration, receipt, and Level-5 Diátaxis infrastructure. Does not own composing domain semantics. |
| `scripts/admit-config.sh` | Admits raw `marketplace.toml` into executable qualification configuration. |
| `scripts/marketplace.py` | Local-first structural/source admission, derived catalog, and corpus fingerprint. |
| `scripts/qualify_packs.py` | Real-ggen bounded all-pack manufacture/replay qualification court. |
| `scripts/qualify-marketplace.sh` | Repository qualification wrapper over admitted configuration. |
| `docs/book.ttl` | Canonical mdBook navigation/control semantic source. |
| `docs/SUMMARY.md` | Generated mdBook navigation consequence; not an editing surface. |
| `docs/tutorials/` | Learning-oriented Diátaxis quadrant, including Level-5 promotion tutorial. |
| `docs/how-to/` | Task-oriented Diátaxis quadrant, including promotion and family consolidation procedures. |
| `docs/reference/` | Exact contract/reference quadrant, including pack classes and the 5 × 7 maturity contract. |
| `docs/explanation/` | Architecture/rationale quadrant, including Level-5 Diátaxis and class-closure explanations. |
| `docs/thesis/` | Research monograph and appendices; explanatory/research corpus, not a parallel operational authority plane. |
| `.github/workflows/ci.yml` | Read-only orchestration around repository acceptance/qualification. |
| `.github/workflows/pages.yml` | Exact-subject ggen manufacture of mdBook control surfaces followed by mdBook build/deploy. |
| `.ggen-packs-source-sha` | Historical initial source-commit receipt; provenance, not moving canonical authority. |

Packaging profiles (`projection`, `semantic`, `project`) describe pack shape. Semantic [pack classes](pack-classes.md) describe composition responsibility. [Level-5 maturity](level5-maturity-contract.md) is a separate standing contract over seven dimensions plus Diátaxis closure.
