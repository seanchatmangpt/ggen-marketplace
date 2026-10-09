# RETIRED: UNSCOPE-castle-goal-2026-10-08-22-22-51 (round-1 duplicate)

- **Typed standing**: RETIRED(superseded-duplicate) — broken_term: n/a (not a refusal; a re-seal duplicate)
- **Record**: `UNSCOPE-castle-goal-2026-10-08T22:22:51.sj-record.json` (moved here from `seal/` 2026-10-08)
- **Superseded by**: `UNSCOPE-castle-goal-2026-10-08T22:22:51@round2.sj-record.json` (same ledger row, same subject_sha `6692936f6ea8257d814995437f2b5c9cb54ff128`, identical standing `REFUSED(no_workgraph...)`, chain head `1190a4f8f981f9ca16b95d259801126d58e6c95843b3ce9212b4b3157d9d7839`)
- **Why retired**: the round-1 record was a byte-different duplicate seal of the same ledger row
  (carried the mislabeled repo `castle-goal`; the round2 re-seal names repo `castle`). It sat on
  disk outside CHAIN-HEAD.txt / standing-table.tsv / OSXCLNR-SEAL-HEADS.txt. Moving it out of the
  seal root makes disk == chain tables (78 records, 78 chain rows).
- **Why not re-sealed**: the ledger has exactly one row for ts 22:22:51; sealing it twice would
  mint a second campaign. The round2 record is the canonical terminal seal for this row.
- **Backlog ref**: M14 finding, backlog [101].
