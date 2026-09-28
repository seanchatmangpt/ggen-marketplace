# Explanation: security and authority

A pack is semantic data plus executable manufacturing logic. Convenience must not erase authority boundaries.

## Preserve

The marketplace preserves a strict distinction between:

```text
SELECT — choose/derive a reversible option
CONSTRUCT — manufacture an artifact or intent
DO — cause consequential external change
```

Most marketplace packs own SELECT and/or CONSTRUCT. They do not receive ambient DO authority because they can emit a powerful artifact.

## Fence

Marketplace CI validates source with read-only authority and must not commit corrections back into a PR branch. Symlinks are refused so reviewed pack source cannot escape through path aliasing. Configuration/runtime identity is admitted before qualification. Gates may refuse manufacture requests but do not become external security guarantees simply by existing.

The central authority fence is:

```text
raw input / RDF / planner output / generated file / proof / hook
                    ≠
                 DO authority
```

Hooks may manufacture intents. Generated Terraform may describe infrastructure. Generated GitHub Actions may describe automation. MCP/API payloads may describe requests. None receives external execution authority from marketplace admission or ggen manufacture alone.

## BRCE boundary

Where the wider consumer system uses BRCE, consequential DO remains behind that separately admitted path with zero unreceipted actuation. The marketplace can distribute semantics/templates/policies for that path, but distribution does not grant the credentials, policy decision, or runtime authority needed to actuate.

## Level-5 authority dimension

The authority-fence column of Level 5 requires more than writing "safe" in documentation. The pack/consumer contract should make explicit:

- which surfaces are SELECT-only;
- which surfaces construct artifacts/intents;
- what component, if any, owns DO;
- the admission condition for DO;
- what receipt binds the consequence;
- what rollback/replay semantics exist;
- what authority remains blocked/unsupported in qualification environments.

A Level-5 tutorial/how-to that reaches a consequential action must name the authority ceiling and rollback. If the required authority is not available, the correct state is `BLOCKED:<reason>`, not a mocked ALIVE claim.

## Composition authority

Consolidating packs must not widen authority by union. Two modules that each stop at CONSTRUCT do not automatically create a DO-capable umbrella. When composed modules have different authority owners, keep those ownership boundaries explicit.

Authority joins are a first-class consolidation falsifier: if class closure makes an irreversible transition possible that neither predecessor admitted, the consolidation must be refused or narrowed.

## Receipts

A receipt binds evidence about identity, authority, consequence, execution, and replay. It does not itself make the consequence correct; it makes the claim inspectable and falsifiable.

Evidence/attestation packs similarly do not acquire the authority of the systems they observe.

## Operational rule

For every pack and every documented procedure, ask:

```text
What can this source select?
What can it construct?
What can it actually actuate?
Who admits that transition?
What receipt proves it happened?
How is it replayed or rolled back?
```

If those questions have no admitted answers, Level-5 promotion stops at the last proven reversible boundary.
