# Tutorial: plan an engagement as a standing ledger

You will turn a conventional "30-day implementation plan" into a standing ledger, separating what can be manufactured immediately from what must wait on people, access, and evidence. The example is deliberately generic; substitute your own subject. Background: [Why manufacture time and standing time are different clocks](../explanation/manufacture-time-vs-standing-time.md).

## 1. Start from the conventional plan

Suppose the plan reads: discovery → design → implementation → integration → validation over thirty days. Write each phase's real deliverable next to it. You will find most "implementation" deliverables are capabilities a pack already provides or composes.

## 2. Apply REUSE → COMPOSE → EXTEND → INVENT

For each deliverable, search `packs/` first. Mark it `reuse`, `compose`, `extend`, or `invent`. Only `invent` and `extend` are genuinely new construction. Write the residual down; it is usually much smaller than the plan assumed.

## 3. Turn deliverables into ledger rows

Use the [row contract](../reference/engagement-standing-ledger.md#row-contract). For every row, fill in `blocker`. If you cannot name what stands between the row and its witness, the plan is not ready, however fast construction is.

## 4. Place rows on the calendar by blocker, not by effort

Rows whose blocker is `none` (rows 1–3 of the canonical sequence) go first. Rows blocked on `authority`, `evidence`, or `external-dependency` are scheduled when the owning person can act, not when an engineer could type the code. Anything requiring `DO` stays `BLOCKED:<reason>` until its separately admitted path has authority.

## 5. Measure what you can

Run [the timing procedure](../how-to/measure-manufacture-time.md) on the packs involved, so the "manufacture early" claim is backed by a measurement rather than asserted.

## 6. State the plan in standing terms

A faithful summary reads: "Constructed artifacts exist at the start with standing `UNKNOWN`; the remaining calendar moves each boundary toward `ALIVE`, and the listed blockers are the dependencies for doing so." It must not read "the software is done."
