# divergent-notes

Standing: UNVERIFIED

Violation-to-gate map for `divergent-machine.json`
(pairs with `positive-machine.json` under the M1 cs2-conformance-pack
seal standard: every gate needs a positive fixture that qualifies and a
divergent fixture the gate must REJECT).

## Violation-to-gate map

| id | planted violation | where | gate(s) that must REJECT | reject mechanism |
|----|-------------------|-------|--------------------------|------------------|
| V-DIV-1 | unlawful `parallel` node | `machine.createMachine.type` | 030 conformance, construct_gate | pack law requires flat guarded machines; a parallel root is outside the lawful shape |
| V-DIV-2 | missing `initial` | `machine.createMachine.initial` | 030 conformance, 040 smoke run | a root without `initial` cannot be instantiated; conformance law requires it present at every level |
| V-DIV-3 | relative cross-level target | `states.idle.states.idle.on.SUBMIT.target` = `../counting` | 030 conformance, 040 smoke run | targets must be state-local or root-absolute (`#machine-id.state`); relative traversal across levels is unlawful |
| V-DIV-4 | stray `*/` in comment | `machine.comment_field` | 020 compile-shape scan | unbalanced comment tokens fail the compile-shape scan before any projection |
| V-DIV-5 | as-const shared config ref | `machine.setup.shared_config.$ref` = `./common.states.json` | 010 ttl triple counts, 020 compile-shape scan, 030 conformance, construct_gate | setup must be inline; a shared as-const ref leaves dangling binding triples (010 count mismatch), breaks the inline-setup law (construct_gate), and is a non-inlined config source (020/030) |

Gate coverage: all five gates (010, 020, 030, 040, construct_gate) have at
least one planted violation naming them; the positive fixture expects PASS on
all five. See Also: `positive-machine.json` (`expected_gates`).
