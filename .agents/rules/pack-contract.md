# Pack Contract and Manufacturing Rules

## 1. Pack Identity and Manifest Strictness

- Directory name under `packs/<name>` must match `[pack].name` exactly.
- Pack deserialization enforces `deny-unknown-fields`.
- The `[pack]` table admits **only**:
  - `name`: string
  - `version`: valid SemVer string
  - `description`: non-empty string
- Extra metadata belongs in RDF turtle graphs or separate extension fixtures, not in `pack.toml`.

## 2. Structural Pack Profiles

Profiles are derived structurally by `scripts/marketplace.py`:
- `project`: Contains `ggen.toml` at the pack root (self-contained ggen project).
- `projection`: Contains `.tmpl` or `.tera` template files (projects RDF facts into consumer code).
- `semantic`: Pure RDF facts, schemas, and gates without consumer templates.

## 3. Manufacture Before Hand-Writing

Before creating new packs, schemas, or boilerplate:
$$\text{REUSE} \rightarrow \text{COMPOSE} \rightarrow \text{EXTEND} \rightarrow \text{INVENT}$$

- Check existing packs in `packs/` and `ggen_igniter` before introducing hand-crafted representations.
- Consumer outputs are downstream consequences—never commit generated files into pack source directories.
