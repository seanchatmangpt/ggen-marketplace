# Reference: engagement standing ledger

A ledger form for planning an engagement around standing transitions rather than implementation phases. Motivation: [Why manufacture time and standing time are different clocks](../explanation/manufacture-time-vs-standing-time.md). Walkthrough: [Plan an engagement as a standing ledger](../tutorials/standing-ledger-for-an-engagement.md).

## Row contract

Each ledger row names one boundary and is complete only when every field is filled:

| Field | Meaning |
|---|---|
| `boundary` | the exact thing whose standing is claimed (subject, environment, court) |
| `from` / `to` | standing before and target after, using `UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE`, `BLOCKED:<reason>`, `BUILD_BROKEN`, `UNSUPPORTED`, `REFUSED:*` |
| `witness` | the evidence that would move standing: receipt, replay, observation, decision |
| `blocker` | typed owner of what is missing: `requirements`, `authority`, `evidence`, `external-dependency`, or `consequence`; `none` only when the witness is producible inside the marketplace/ggen boundary |
| `authority` | `SELECT`, `CONSTRUCT`, or `DO`; any `DO` row names the separately admitted path (for example BRCE) |
| `subject` | exact identity the claim binds (repo/head/pack/configuration/toolchain/environment) |

## Canonical gate sequence

| # | Boundary | Target standing | Typical witness | Typical blocker |
|---|---|---|---|---|
| 1 | Reuse/compose/extend plan over existing capability | constructed (`UNKNOWN`) | pack selection, composition closure | `requirements` |
| 2 | Marketplace admission | `PARTIAL_ALIVE` | `marketplace.py validate`, admitted config | `none` |
| 3 | Bounded manufacture + replay | `PARTIAL_ALIVE` | qualification report, identical replay | `none` |
| 4 | Real consumer/runtime execution | `ALIVE` for that boundary | consumer-native run at the exact subject | `external-dependency` |
| 5 | Integration with the customer's real systems | `ALIVE` for that boundary | observation from the real system | `authority`, `external-dependency` |
| 6 | Load, failure, and compliance evidence | `ALIVE` for that boundary | measured runs, compliance decisions | `evidence`, `authority` |
| 7 | Consequential actuation | `BLOCKED:<reason>` until authority is granted | separately admitted `DO` path receipt | `authority`, `consequence` |

Rows 1–3 are the only ones whose witnesses can be produced without anyone outside the marketplace boundary. A plan may place them at the start; it may not place rows 4–7 there unless the named blockers are already cleared and evidenced.

## Rules

- A row advances only on exact-subject evidence; success at another SHA does not carry over.
- Never mark a row `ALIVE` from a mock, fixture, or generated existence. If required external authority is unavailable, the row is `BLOCKED:<reason>`.
- Manufacture time for rows 1–3 may be measured with [`manufacture_timing.py`](manufacture-timing-contract.md); it informs planning and never substitutes for a witness.
- The ledger is a plan and status surface. It carries no `DO` authority and is not a service-level commitment.
