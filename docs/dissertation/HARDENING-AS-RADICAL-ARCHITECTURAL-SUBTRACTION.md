# Hardening as Radical Architectural Subtraction: seL4 Doctrine for the ggen Fabric

> **Provenance.** Verbatim landing of the operator doctrine message of 2026-10-08
> (lane `sel4-doctrine`, wave v26.10.8). No editorial modification of doctrine
> content; this header is the only added text. Companion operationalization:
> `docs/sjira/v26.10.8/TCB-INVENTORY.md` (real file:line + LOC footprints, read
> from disk on 2026-10-08).

## 0. Thesis

Hardening is subtraction, not addition. Every control we add to defend a system
is a component that must itself be defended. The only path to a TCB you can
actually verify is to delete machinery until what remains is small enough to
prove, then stop. seL4 is the existence proof: a general-purpose kernel with a
formally verified implementation, achieved not by verifying more, but by having
less to verify. The ggen fabric inherits this doctrine: the kernel crates are
the seL4 kernel; the graphlaw Datalog fixpoint, the wire parser, and the
affidavit verify stub are the kernel's fastpath — the code whose correctness is
assumed by everything above it.

## 1. Lesson 1 — Capability quotas: authority must be finite

In seL4, authority is a capability with a finite space. Every memory right,
every IPC endpoint, every IRQ control is an object whose authority is bounded,
recounted, and revocable. "Can this component do X?" is answered by enumerating
capabilities, not by reading policy text. In the ggen fabric, the same law
applies to the receipt stream and the actuation path: every actuation is
bounded by an admitted work order, every work order carries an authority
ceiling, and revocation is a real transition (typed refusal), not a flag flip.

**ggen mapping.** Authority ceilings are typed (`authorityClaim NONE`,
CONSTRUCT ceilings, BRCE as the only DO path). A component's authority is
finited by what the graph admits — never by what a prompt says.

## 2. Lesson 2 — Mechanism, not policy

seL4 ships mechanism only: IPC, capabilities, revoke/retype — the *how*, never
the *what*. Policy (what to run, who may talk to whom) lives outside the TCB.
The ggen kernel crates mirror this: praxis-core and praxis-graphlaw provide
admission machinery (stratification, fixpoint, chain recompute, staged
validation) and contain no cloud, IAM, or ledger-vendor policy — verified below
by grep, honestly, including the false-positive analysis.

**ggen mapping.** `praxis-core` + `praxis-graphlaw` are mechanism; the RDF
ontology + packs + projections are policy. Mixing them is the seL4 equivalent
of baking an AWS SDK into the kernel.

## 3. Lesson 3 — Proof-carrying compilation and Delta(G)=0

seL4's verification carries proof from the C source down through binary
verification; the theorem is about the artifact that runs. Delta(G)=0 is the
ggen fabric's version: a generated artifact is admitted only when the graph
that generated it and the graph in the deployed subject are byte-identical
(no drift between admitted specification G and actuated G'). Proof-carrying
compilation is the general law; Delta(G)=0 is its ggen instance. A receipt
whose replay cannot reproduce the artifact byte-for-byte is not a receipt; it
is a narrative.

**ggen mapping.** Generator plurality (C20) and out-of-subject receipts (C21)
are the open work orders that close this lesson for the fabric.

## 4. Lesson 4 — Non-interference / isolation between components

seL4 proves non-interference: information cannot flow between components that
hold no capability to communicate. In the fabric the analogous guarantee is
lane isolation and edge standing: a lane (or repo edge) that holds no authority
cannot perturb another lane's state — no `git stash` sweeping a sibling lane's
in-flight edits, no shared mutable compile root, one writer per checkout. The
measure of isolation is not documentation but the product of edge standings:
one edge breaking drops the product to zero.

**ggen mapping.** Same-checkout fan-out law: agents are lanes with disjoint
file ownership; the coordinator owns all git state transitions.

## 5. Lesson 5 — CDT revocation: revoke by retyping, not by trust

seL4's CDT (capability derivation tree) makes revocation a local, mechanical
operation: revoke a node and its derivation subtree loses authority by
structure, not by a distributed trust dance. In the fabric, revocation must be
structural: retiring a rule, a pack, or a lease retires its derived authority
by graph topology — `standing` lives in the receipt bound to identity, and a
stored standing that outlives its receipt is a category error. The pruner
(C23) is the fabric's CDT operator: retire entries whose witnessing firings no
longer exist.

**ggen mapping.** Standing vocabulary (primitive I) + harness pruner (C23) +
revocation as a typed refusal (not a flag).

## 6. Lesson 6 — The verification-budget law

seL4's real lesson is budgetary: the TCB is sized to the verification budget,
not the feature list. Every feature admitted into the kernel spends budget;
the doctrine is to spend it on the fastpath (IPC, capabilities) and starve
everything else. The ggen fabric's budget is spent on the three primitives
inventoried below — Datalog fixpoint, wire parser, verify stub — and the
standing law is: a new capability enters the TCB only with its own verification
receipt, or it does not enter.

**ggen mapping.** TCB inventory (`docs/sjira/v26.10.8/TCB-INVENTORY.md`) is
the budget ledger: each row a real file:line + LOC footprint, re-read from
disk at use time.

## 7. The seL4-vs-ggen analogy table

| seL4 concept | ggen fabric counterpart | Fabric locus |
|---|---|---|
| Kernel | Kernel crates (praxis-core, praxis-graphlaw) | `~/ggen/crates/praxis-*` |
| IPC fastpath | Graphlaw Datalog fixpoint + stratification | `~/ggen/crates/praxis-graphlaw/src/datalog.rs` |
| Capability object | Admitted work order w/ authority ceiling | ggen-marketplace shapes |
| Retype/revoke | Graph retirement / pruner (C23) | composition catalog C23 |
| Non-interference | Lane isolation, edge standing product | same-checkout fan-out law |
| Proof-carrying compilation | Delta(G)=0, byte-identical replay | portable receipts (primitive B) |
| Verification budget | TCB inventory rows, re-read at use time | `docs/sjira/v26.10.8/TCB-INVENTORY.md` |
| User-level policy | Ontology + packs + projections | ggen-marketplace packs |
| CDT (derivation tree) | Receipt-bound standing graph | receipt chain (`chain.rs`) |
| Formal model | RDF ontology as canonical graph | `~/.claude/dfcm/composition-space.ttl` |

## 8. Falsifiers

- The doctrine claims mechanism-not-policy for the kernel crates: falsified if
  the mechanism-not-policy grep in TCB-INVENTORY.md turns up a real (non-
  substring-false-positive) cloud/IAM/vendor-policy hit.
- The doctrine claims a verifiable fastpath: falsified if any inventoried
  footprint cannot be re-read from disk at the cited file:line.
- Verbatim landing: falsified by diff against the operator message source.
