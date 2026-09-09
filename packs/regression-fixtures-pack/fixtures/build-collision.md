# build-collision

**Failure class**: resource-contention

## Name

Two concurrently-dispatched agents request the same build resource (a shared
`target/` directory, a shared build-cache dir, a shared lockfile) at the same
time — one agent's build corrupts or blocks the other's, or both silently
race and one's artifacts get clobbered by the other's.

## Setup

1. Declare two agent assignments (e.g. two `fleet:Agent` individuals) that
   both name the identical `fleet:buildCacheDir` (or, at the filesystem
   level, both agents' working directories resolve to the same
   `CARGO_TARGET_DIR` / `node_modules` / build-cache path).
2. Dispatch both agents concurrently against independent worktrees but the
   shared cache path.
3. Let both run a build (`cargo build`, `npm install`, etc.) against the
   shared directory at overlapping times.

## Expected sensor/gate behavior

Exactly one agent must hold a lease on the shared resource; the other must
be refused that resource up front (never allowed to race against it) and
redirected to independent work rather than blocked indefinitely. This must
be caught at plan-admission time — before either agent's build actually
runs — by comparing declared resource paths for collisions, not discovered
only after a corrupted build.

## Existing gate citation

- `packs/agent-fleet-isolation-pack/gates/020_buildcache_collision.rq` — this
  is the real, already-shipped gate for exactly this fixture: it refuses the
  instant two `fleet:Agent` individuals declare the same `fleet:buildCacheDir`,
  citing both colliding agent names and the shared path in its output. This
  fixture's setup step 1 above is a literal instantiation of that gate's
  SELECT pattern.
- `packs/agent-fleet-isolation-pack/gates/010_worktree_collision.rq` — the
  sibling gate for the same failure family one level up (colliding
  `fleet:worktreePath` rather than `fleet:buildCacheDir`); relevant when the
  collision is on the working tree itself rather than only the build cache.

No new gate is invented here; `gates/020_buildcache_collision.rq` already
fully encodes this fixture's expected behavior, proven `0 rows` on the green
fixture and firing on the deliberately-broken one per that pack's own
README qualification section.
