# Committed qualification run logs

Real, captured stdout+stderr from `bash qualification/orthogonal_scan.sh`, run
against this pack's actual fixtures with the real installed tools
(`ggen` 26.8.18, `kubeconform`, `trivy`, `kyverno`, `kubescape`) -- not a
narrated summary. This directory exists specifically to close a gap flagged
by an adversarial review: the commit history for this scanner layer described
results in prose but committed no log file corroborating them.

## `orthogonal_scan-2026-09-10T230754Z.log`

Captured 2026-09-10T23:07:54Z (session `session_01QfTng1WQdACXYYiJmePVpa`),
exit code 0. Headline numbers, cross-checked against this file's own content:

- `ggen sync run --format json` -- 6 real renders (4 positive fixtures + 2
  known-gap negative controls), each producing `pipeline.files_generated=1`.
- `kubeconform -strict`: `valid=8, invalid=0, errors=0`.
- `trivy config`: `privileged-container-KNOWN_GAP` fires AVD-KSV-0017
  (privileged) + AVD-KSV-0014; `mutable-image-tag-KNOWN_GAP` fires
  AVD-KSV-0014; every fixture also independently fires AVD-KSV-0014
  (`readOnlyRootFilesystem`), a real finding not called out in the original
  commit message's summary of this run.
- `kyverno apply`: `pass: 16, fail: 8` -- failures land on
  `mutable-image-demo` (3 rules), `privileged-demo` (4 rules), and `xaas`
  (1 rule, digest-only, as expected since xaas never claimed
  high-assurance).
- `kubescape scan framework NSA,cis-v1.10.0`: aggregate compliance
  `NSA=79.17`, `cis-v1.10.0=79.29`, 36/52 controls passed.
- Cosign: not run, real reason logged inline (no built/pushed image exists
  for this pack to sign).

This is a fresh, independent re-run captured this session, not a re-paste of
the original commit's narrative -- the exact numbers differ in minor ways
(e.g. AVD-KSV-0014 now also fires on `high-assurance-workload.yaml`'s
sibling fixtures per this run's trivy summary table) because tool databases
and this pack's fixtures have both moved since 7d0d8444b. Treat this file,
not the commit message, as the source of truth for "what did the last real
run actually show."

`python3 scripts/marketplace.py validate` was also re-run this session and
reproduced the same aggregate counts the original commit claimed:
`packs=299 manifests=299 ontologies=450 templates=1799 native_gates=1458
verifier_gates=37`.
