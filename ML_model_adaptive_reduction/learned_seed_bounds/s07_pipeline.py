"""Run fitting and reserved tests in separate Python processes."""
import subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
for stage in ['s05_train.py','s06_test.py','s10_secondary.py']:
 subprocess.run([sys.executable,str(HERE/stage)],check=True)
