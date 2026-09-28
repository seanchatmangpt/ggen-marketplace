#!/usr/bin/env bash
# T03 invalid corpus — the null engine (vacuity probe, ticket acceptance #1).
#
# The strongest possible "silently did nothing": echoes nothing on any
# stream, ignores every argument, exits 0. A refusal assertion that could
# exit 0 against THIS stub would be vacuous — unable to distinguish a real
# typed refusal from no engine at all (RFC-GPACK-001 v26.9.17 §77:
# PASS = AttemptObserved AND ForbiddenOutcomeAbsent AND RequiredOutcomeObserved).
#
# Law: every assert/run.sh in this corpus MUST exit non-zero against this
# stub. run-null-falsifier.sh proves it for all 11 fixtures in one command;
# tests/test_gpack_negative_corpus.py keeps that proof permanent.
exit 0
