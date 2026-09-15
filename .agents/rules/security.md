# Security, Path Safety, and Secret Rules

## 1. Path Safety & Absolute Boundaries

- **No Symlinks**: Symlinks are strictly prohibited under `packs/`. Packs must remain completely self-contained and path-safe.
- **Path Traversal Protection**: Directory traversal (`../`) outside pack boundaries is refused during validation and archive synthesis.
- **No Generated Namespaces**: Never introduce `generated/` as a source namespace for marketplace metadata.

## 2. Secrets & Token Hygiene

- Never rely solely on `.gitignore` for secret safety.
- Privilege Separation: Never place service-role, administrative, or deployment credentials in client-bundled environments or source files.
- Audit public variable semantics across frameworks (e.g. `EXPO_PUBLIC_*` exposes values to clients).
- Zero Exposure: Never print or echo secret tokens, access keys, or credentials in script logs or stdout/stderr.
