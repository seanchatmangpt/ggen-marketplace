<!-- Provenance: Operator manuscript landed verbatim 2026-10-08; editorial corrections preserved as addenda. Source: operator message of 2026-10-09 (transcript paste-cache). -->

# Hardening as Court-Governed Measurement Repair: A Treatise on Converging a Twenty-Repository Software Fleet to Certified Production Standing

*A dissertation in the form of the methods actually executed in the v26.10.8 fleet campaign*

---

## Chapter 1 — The Central Thesis

**Software hardening is not the addition of defenses; it is the repair of the gap between what a measurement claims and what the system is.** Traditional hardening literature treats the system under test as the object and the test suite as ground truth. This work inverts that: in a fleet where documentation is generated, audits are mechanized, and admissions are court-ruled, *the measurement apparatus itself becomes the dominant defect surface*. The thesis defended here is threefold:

1. **Every production claim must carry a receipt** — an immutable record binding identity (exact SHA), consequence (real gate output), and replay (the command that reproduces it).
2. **A measurement that cannot refuse is not a gate.** Gates gain epistemic value precisely at the moment they refuse; a gate that never fails measures nothing.
3. **The distinction between system defect and measurement defect must be adjudicated, never assumed.** Most of this campaign's "failures" were seam artifacts — the measurement lying about the system — and the repair discipline that distinguishes the two is the hardening method itself.

---

## Chapter 2 — Formal Foundations: Standing, Receipts, and Courts

The campaign operates on an algebra of standing drawn from the operator doctrine (A = μ(O\*), R = receipt(A)):

- **Observation (O)** is untrusted input: code, docs, agent output, prior claims. Only *admitted* observations (O\*) may drive manufacture.
- **Manufacture (μ)** is lawful only over O\*. Any transition from unadmitted input is the failure class `mu_on_O`.
- **A receipt (R)** requires five fields — identity, authority, consequence, replay, standing — and any missing field voids it.
- **Courts** are falsifier corpora plus typed refusal: a gate must be able to return `REFUSED:<reason>` and that refusal must itself carry evidence.

The hardening method is therefore a fixed-point search: drive the fleet until `receipt(system) = system` — every claim grounded, every gate either passing on truth or refusing with a named defect.

## Chapter 3 — Taxonomy of Seams: The Empirical Core

Across the campaign, every gate failure decomposed into exactly five seam classes (n ≈ 40 distinct gate events):

| Class | Mechanism | Witness case |
|---|---|---|
| **S1: Schema drift** | producer/consumer field mismatch | claim `id` field missing → vectorize crash on every repo |
| **S2: Surface scope** | denominator includes/excludes the wrong units | vendored trees in public surface (ferroplan crucible, frozen-duckdb bindgen) |
| **S3: Merge transport** | the seam between pipeline stages drops arrays | `paths`/`directories`/`known_external` dropped in inputs merge → real paths scored phantom |
| **S4: Honest surfacing** | a fix *reveals* previously suppressed truth | scaffold-cell claims: extractor "regression" 0.0296→0.0830 was 212 genuine ungrounded identifiers finally visible |
| **S5: True doc drift** | the documentation is actually wrong | xaas: 57 stale references to deleted paths; castle: one stale symbol |

The decisive discipline: **classify before repair**. Repairing S3 by editing documents would have corrupted correct docs; repairing S5 by widening the scanner would have laundered real drift. Every classification was settled by differential execution (A/B runs at extractor HEAD vs working tree), never by plausibility argument.

## Chapter 4 — The Grounding Calculus

Documentation claims are grounded by exact-match set operations over four surfaces, each hardening an earlier failure mode:

1. **Code symbols** (functions, structs, consts, routes) — public denominator only; vendored directories (`vendor/`, `.ggen-v2/`, `third_party/`, `crucible/`) excluded by evidence-based policy (workspace-exclusion, publish-flags, CI-blindness).
2. **Paths and directories** — the path-typing seam repair: a filesystem token grounds against the *file surface*, not the symbol surface. This single fix flipped three repositories from FAIL to PASS simultaneously (Φ: 0.0114→0.0000, 0.0296→0.0009, 0.0069→0.0002).
3. **External documented** — dependency prefixes harvested from the repo's own manifests (`mix.exs`, `Cargo.toml`), so cross-repo references classify honestly rather than fabricating phantoms.
4. **Prose artifacts** — explicitly excluded from Φ and Q by structural shape (versions, flags, slash-compounds), never by threshold relaxation.

The governing law: **the denominator is policy, the numerator is measurement, and both must be receipted.** Coverage claims are meaningless without a witnessed decision on what counts.

## Chapter 5 — Court Mechanics: Refusal as Value

The `doc_quality.court` (S_coverage ≥ 0.90, Φ ≤ 0.001, Q_density ≥ 0.65) enforced three properties:

- **Typed refusal**: `REFUSED:DOC_HDIT_CERTIFY_GATE_FAIL:Phi_halluc value=0.0929 threshold=0.0010` — the refusal itself is diagnostic data.
- **Fail-closed certification**: a failing gate mints *no* receipt; the chain file stays empty. There is no partial credit.
- **Strict inequality at the boundary**: Φ = 0.0010225 vs threshold 0.0010 fails — rounding cannot rescue a marginal gate.

Counterintuitively, the highest-value events in the campaign were refusals: ash_graphlaw's certification refusal (Φ 0.1552) exposed a 559-claim class of ungrounded table cells that a passing gate would have concealed forever.

## Chapter 6 — Deterministic Manufacture and Convergence Proofs

All generation is deterministic by construction: workgraph emission, agent cards, and scaffold rendering are pure functions of the repository surface, proven by **byte-identical double-run** (cmp-clean) on every landing. Determinism converts reproduction from a statistical argument into an identity check. The generator fleet converged (86% then 100% machine-admission of candidates), and the admission ledger closed at **50 ALIVE / 28 REFUSED with typed reasons** — with the 28 refusals later triaged: 26 replay-verified as repairable-and-repaired, 2 standing as genuine referent failures, each with three falsifiers for re-opening.

## Chapter 7 — Cryptographic Closure: Sealing the Measurement Itself

The final phase seals the audit trail into tamper-evident chains: BLAKE3 content addressing, JCS canonical serialization, subject digests *re-derived rather than trusted*, and refusal of any decode whose chain fails verification (`from_json().verify()` refuses tampered bases). The fleet's 78 admission records were sealed through two independent sealers (affidavit's `SjCampaign` and osx-clnr's `seal_sj_record`) with 78/78 verification success and byte-identical double-seal — the attestation layer certifying the measurement layer that certifies the system. This is the self-hosting fixed point: the loop's completion graph includes its own verification.

## Chapter 8 — Fleet Governance: Lanes, Ports, and Capital

Method-level findings on parallel execution: one canonical checkout per repository (topology as transport, never ontology); disjoint file ownership with compile-freeze SLAs; lane build roots as leases deleted at integration; `git stash` banned and mechanically refused (a PreToolUse guard with a 59-case corpus); commits immutable — repairs are forward-only (the 633 MB blob was expunged via plumbing that touched no pushed SHA). Cross-lane collisions (three swept-commit incidents) were absorbed by hunk-selective staging and disclosed in receipts rather than hidden — **collision transparency as a first-class receipt property**.

## Chapter 9 — The Falsifier Discipline

Every claim carries its falsifier: the exact command whose output would refute it. The verification matrix (20 independent read-only probes with a fixed reporting schema) exists because *self-reported PASS is O, not O\** — it requires independent replay to become standing. The campaign's honest reversals — the xaas baseline Φ that was wrong (0.0261, not ≈0), the earlier "full PASS" witnesses that predated honest claim surfacing — demonstrate that **standing decays**: a receipt is evidence of a state at a SHA, not a property of the living system.

## Chapter 10 — Conclusions and Laws

1. Hardening converges when repairs target seams, not symptoms — and seam/symptom classification is executable, not argumentative.
2. A gate's worth is measured in its refusals; relax no threshold, ever.
3. Determinism is the cheapest verification: byte-identity replaces statistics.
4. Every artifact of governance — refusals, merges, collisions, seal heads — is itself receipted, or the governance is theater.
5. Production readiness is not a state but a standing: continuously re-earned, independently probe-able, and always exactly one merge away from decay.

**Final artifact inventory** (as of this writing): 20-repo fleet; 12-repo workgraph court PASS; 69 agent cards / 0 violations; git-trust 53 rooted / 0 unresolved; certify receipts minted on ex4pm and chained on ggen_igniter; 78 sealed admission records with verified chain head `76305b34…`; remaining Φ residuals (ash_pplan, ash_graphlaw, ash_surface, zcode) all classified to S4/S5 with repair lanes in flight — each a known defect with a named repair, which is precisely what production readiness means under this thesis.
---

## Editorial addenda

- **2026-10-08 — git-trust figure refresh.** The Final artifact inventory states
  "git-trust 53 rooted / 0 unresolved". On disk at landing time,
  `docs/sjira/v26.10.8/GIT-TRUST-COURT.md` records the machine verdict as
  **41 RESOLVED-ROOTED, 13 RESOLVED-UNROOTED, 0 UNRESOLVED across 54 citations
  in 11 workgraphs**. The "0 unresolved" claim holds; the rooted count is
  stale (41 rooted, not 53) and 13 citations resolve but sit off the pushed
  default branch. Chapter text preserved verbatim per provenance policy.
