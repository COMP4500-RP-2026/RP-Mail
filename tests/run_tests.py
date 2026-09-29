"""Run isolated local checks; no real email or RP+ requests."""
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
for test in sorted((root/'tests').glob('test_*.py')):
    print(f'Running {test.name}',flush=True)
    subprocess.run([sys.executable,str(test)],cwd=root,check=True)
print('All checks passed.')
