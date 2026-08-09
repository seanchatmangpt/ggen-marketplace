# Explanation: why a separate marketplace

Packs and the ggen runtime change for different reasons. Runtime code defines how manufacture works; packs encode reusable domain-specific manufacturing knowledge. Keeping the pack corpus in a dedicated repository reduces the pressure to ship runtime internals merely to publish or review a pack and makes the reusable surface discoverable as a product in its own right.

The separation also creates an explicit ownership boundary: this repository owns pack source and catalog documentation; ggen owns interpretation/execution. That boundary avoids copying the ggen runtime into the marketplace and avoids turning marketplace metadata into another implementation of ggen.

The extraction began with byte-identical source provenance, then added repository-local validation and documentation around the imported corpus. Extraction and modernization therefore remain distinguishable operations.
