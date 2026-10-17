"""Complete analysis and document checks after the scientific jobs finish."""
import subprocess,sys
from s00_protocol import HERE,ROOT,read,write
for name in ['completion_0.json','completion_1.json','analytic_completion.json','scale_completion.json']:assert read(HERE/name)['complete']
for name in ['s06_analyze.py','s07_document.py']:
 subprocess.run([sys.executable,str(HERE/name)],check=True)
subprocess.run(['make','all'],cwd=ROOT/'report',check=True,timeout=420)
subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],check=True,timeout=180)
subprocess.run([sys.executable,str(HERE/'s08_finish.py')],check=True,timeout=180)
write(HERE/'completion.json',dict(complete=True,analysis_complete=True,pdfs_built=True,paper_checks_passed=True))
print('Analysis and PDF checks complete',flush=True)
