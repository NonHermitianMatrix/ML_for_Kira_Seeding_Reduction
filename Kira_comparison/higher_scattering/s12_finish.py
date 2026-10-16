"""Finish analysis, document the evidence, and build the paper and notes."""
import subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
    for name in ['s01_pilot.py','s07_analyze.py','s08_write_report.py','s09_validate.py','s13_document.py']:
        subprocess.run([sys.executable,str(HERE/name)],cwd=ROOT,check=True)
    subprocess.run(['make','-C','report'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'report/s01_check_paper.py'],cwd=ROOT,check=True)
    print('DOCUMENTS_BUILT_AND_CHECKED',flush=True)
if __name__=='__main__':main()
