"""Check the completed first study's documents while portfolio tests continue."""
import os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
os.environ['MPLCONFIGDIR']=str(ROOT/'.tools/matplotlib-cache')
os.environ['XDG_CACHE_HOME']=str(ROOT/'.tools/cache')
for name in ['s06_analyze.py','s07_report.py','s10_document.py']:
    subprocess.run([sys.executable,str(HERE/name)],cwd=ROOT,check=True)
subprocess.run(['make','-B','all'],cwd=ROOT/'report',check=True)
subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],cwd=ROOT,check=True)
