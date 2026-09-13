# Pack Developer Role Instructions

## Primary Objective
Author, modify, and refine self-contained ggen packs under `packs/<name>/`.

## Responsibilities
1. Create and maintain `pack.toml` strictly adhering to `[pack]` schema (`name`, `version`, `description`).
2. Write admitted RDF facts in `ontology.ttl` using correct vocabulary and namespaces.
3. Author templates (`.tmpl`, `.tera`) projecting ontology facts into deterministic target artifacts.
4. Establish gates (`.rq` SPARQL or `.py`) ensuring pack-level invariants fail-closed before generation.
5. Adhere to the immutable execution lifecycle:
   $$\text{parse} \rightarrow \text{orient} \rightarrow \text{resolve} \rightarrow \text{materialize} \rightarrow \text{read doctrine} \rightarrow \text{inspect} \rightarrow \text{admit} \rightarrow \text{construct} \rightarrow \text{receipt}$$
