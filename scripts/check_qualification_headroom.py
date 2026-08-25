#!/usr/bin/env python3
"""Refuse regression or split-brain in bounded real-ggen qualification headroom."""
from pathlib import Path
import re

workflow = Path('.github/workflows/ci.yml').read_text()
runner = Path('scripts/qualify_packs_r18.py').read_text()

workflow_match = re.search(r'--timeout-seconds\s+(\d+)', workflow)
runner_match = re.search(r'MAX_TIMEOUT_SECONDS\s*=\s*([0-9.]+)', runner)
if not workflow_match:
    raise SystemExit('REFUSED:QUALIFICATION_TIMEOUT_MISSING')
if not runner_match:
    raise SystemExit('REFUSED:QUALIFICATION_RUNNER_BOUND_MISSING')
workflow_seconds = int(workflow_match.group(1))
runner_seconds = int(float(runner_match.group(1)))
if workflow_seconds < 30:
    raise SystemExit(f'REFUSED:QUALIFICATION_TIMEOUT_HEADROOM:{workflow_seconds}<30')
if runner_seconds < workflow_seconds:
    raise SystemExit(
        f'REFUSED:QUALIFICATION_TIMEOUT_SPLIT_BRAIN:workflow={workflow_seconds}:runner={runner_seconds}'
    )
if 'timeout-minutes: 8' not in workflow:
    raise SystemExit('REFUSED:QUALIFICATION_JOB_BOUND_MISSING')
print(
    f'qualification-headroom: per-pack={workflow_seconds}s '
    f'runner-max={runner_seconds}s job=8m bounded'
)
