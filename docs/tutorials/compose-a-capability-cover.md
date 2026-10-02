# Tutorial: compose a capability cover

In this tutorial you will ask the composition solver what it can cover from the seed basis, then watch it refuse an overrun. It takes about fifteen minutes. You need a checkout on a branch (not `main`) and a ggen binary; without one, stop after step 2 and read the gate results only. Everything here is synthetic demo input. Nothing generated is ALIVE. Exact contracts are in [Composition solver contract](../reference/composition-solver-contract.md).

## 1. Copy the pack somewhere disposable

Copy `packs/composition-solver-pack` to a scratch directory and copy `fixtures/demo-requirements.ttl` over `ontology/requirements.ttl`. Never run sync inside `packs/`; generated files are consequences, not source.

## 2. Run the gate court

Run `python3 qualification/verify.py` in the pack. Four gates each refuse their fail witness and admit their pass witness, and the court reports `ALIVE` for that bounded boundary only.

## 3. Manufacture

Run `ggen sync run` in the scratch copy. Open `generated/composition-solver/coverage.json`. REQ-1 is `COVERED`, REQ-2 is `BLOCKED_AUTHORITY` and REQ-3 is `UNCOVERED`. Open `selected-atoms.json`: four atoms stand behind REQ-1 and none is a DO atom.

Notice what the three rows teach. One requirement is derivable, one is reachable only through an actuation atom the solver will never select, and one has no provider at all. The last two are the residual, the only part that would become sJira work.

## 4. Break the bound on purpose

Add an atom that requires `residual-feedback-routed` and provides a new proposition, and a requirement that needs it. Run sync again. It is refused with `FM-LAW-018` naming your atom. The cover is deeper than the unrolled stages, and the solver refuses instead of calling a deep requirement uncovered.

## 5. Replay

Restore the demo input and run sync twice. The second run reports the outputs unchanged, and the bytes match a fresh copy. For tasks continue with [Add a capability atom to the solver basis](../how-to/add-a-capability-atom.md).
