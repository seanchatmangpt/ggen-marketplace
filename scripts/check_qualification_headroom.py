#!/usr/bin/env python3
"""Refuse split-brain in bounded real-ggen qualification headroom."""
from pathlib import Path
import re

workflow = Path('.github/workflows/ci.yml').read_text()
runner = Path('scripts/qualify_packs_r18.py').read_text()

workflow_timeout = re.search(r'--timeout-seconds\s+(\d+)', workflow)
workflow_workers = re.search(r'--workers\s+(\d+)', workflow)
runner_timeout = re.search(r'MAX_TIMEOUT_SECONDS\s*=\s*([0-9.]+)', runner)
runner_workers = re.search(r'MAX_WORKERS\s*=\s*(\d+)', runner)
if not workflow_timeout:
    raise SystemExit('REFUSED:QUALIFICATION_TIMEOUT_MISSING')
if not workflow_workers:
    raise SystemExit('REFUSED:QUALIFICATION_WORKERS_MISSING')
if not runner_timeout:
    raise SystemExit('REFUSED:QUALIFICATION_RUNNER_BOUND_MISSING')
if not runner_workers:
    raise SystemExit('REFUSED:QUALIFICATION_RUNNER_WORKER_BOUND_MISSING')

workflow_seconds = int(workflow_timeout.group(1))
workflow_worker_count = int(workflow_workers.group(1))
runner_seconds = int(float(runner_timeout.group(1)))
runner_worker_count = int(runner_workers.group(1))

if workflow_seconds <= 0 or workflow_seconds > runner_seconds:
    raise SystemExit(
        f'REFUSED:QUALIFICATION_TIMEOUT_SPLIT_BRAIN:workflow={workflow_seconds}:runner={runner_seconds}'
    )
if workflow_worker_count <= 0 or workflow_worker_count > runner_worker_count:
    raise SystemExit(
        f'REFUSED:QUALIFICATION_WORKER_SPLIT_BRAIN:workflow={workflow_worker_count}:runner={runner_worker_count}'
    )
if workflow_worker_count > 4:
    raise SystemExit(f'REFUSED:QUALIFICATION_PRESSURE_BOUND:workers={workflow_worker_count}>4')
if 'timeout-minutes: 8' not in workflow:
    raise SystemExit('REFUSED:QUALIFICATION_JOB_BOUND_MISSING')

print(
    f'qualification-headroom: per-pack={workflow_seconds}s '
    f'workers={workflow_worker_count} runner-max={runner_seconds}s '
    f'runner-workers={runner_worker_count} job=8m bounded'
)
