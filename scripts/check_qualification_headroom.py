#!/usr/bin/env python3
"""Refuse regression of bounded real-ggen qualification headroom."""
from pathlib import Path
import re

workflow = Path('.github/workflows/ci.yml').read_text()
match = re.search(r'--timeout-seconds\s+(\d+)', workflow)
if not match:
    raise SystemExit('REFUSED:QUALIFICATION_TIMEOUT_MISSING')
seconds = int(match.group(1))
if seconds < 30:
    raise SystemExit(f'REFUSED:QUALIFICATION_TIMEOUT_HEADROOM:{seconds}<30')
if 'timeout-minutes: 8' not in workflow:
    raise SystemExit('REFUSED:QUALIFICATION_JOB_BOUND_MISSING')
print(f'qualification-headroom: per-pack={seconds}s job=8m bounded')
