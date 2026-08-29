#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys
root=Path(__file__).parent
target=Path(sys.argv[1])
gates=[p for p in sorted(root.glob('check_*.py')) if p.name != Path(__file__).name]
if not gates:
    raise SystemExit('REFUSED:NO_GATES')
for gate in gates:
    subprocess.run([sys.executable, str(gate), str(target)], check=True)
print(f'ADMITTED:{len(gates)}')
