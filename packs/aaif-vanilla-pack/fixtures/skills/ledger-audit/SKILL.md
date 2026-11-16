---
name: ledger-audit
description: Use when auditing session receipts or verifying landed claims against on-disk evidence.
---

# Ledger Audit

## Role

Audit session receipts against on-disk evidence. Assert standing only from files re-read at use time.

## Mechanical Gate

receipt-lint: every receipt carries a `Standing:` line immediately after its H1, using the closed vocabulary only.

## Courts

The ledger-audit court must flip on a receipt missing its Standing line (anti-vacuity). A court that cannot flip is FAIL.

## Legacy Defects

none registered

## Cut Date

2027-05-12
