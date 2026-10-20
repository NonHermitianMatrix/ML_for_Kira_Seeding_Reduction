"""Validate final evidence, preserve the baseline, and render the paper and notes."""
from s00_triangle_common import *
import re

def main():
 p=read(HERE/'test_protocol.json.gz');s=read(HERE/'summary.json');assert s['complete'] and sha(HERE/'test_protocol.json.gz')==s['protocol_sha256'];assert sha(HERE/'trained_model/policy.json')==p['model_sha256'];assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items())
 final=read(HERE/'monitor_summary.json');assert final['complete'];mp=read(HERE/'monitor_protocol.json');assert all(sha(HERE/n)==h for n,h in mp['source_sha256'].items());assert read(HERE/'serial_complete.json')['complete'];sp=read(HERE/'serial_protocol.json');assert all(sha(HERE/n)==h for n,h in sp['source_sha256'].items());assert read(HERE/'scanner_checks.json')['complete'];assert not read(HERE/'equation_validation_summary.json')['admitted']
 assert read(HERE/'formula_checks.json')['source_sha256']==sha(HERE/'s01_triangle.py')
 assert not list((HERE/'requests').glob('*.json*'));assert len(p['cases'])==40 and len(p['regression'])==53
 # Keep the preceding production files and models unchanged.
 names=[]
 for base in ['reconstruction_policy','direct_analytic','lightlike_reduction','tensor_reduction','vacuum_learning']:
  q=ROOT/'ML_model_adaptive_reduction'/base
  names.extend(str(f.relative_to(ROOT)) for f in q.glob('s*.py'))
  names.extend(str(f.relative_to(ROOT)) for f in (q/'trained_model').glob('*.json'))
 old={}
 for entry in subprocess.check_output(['git','ls-tree','-r','-z',p['baseline_commit'],'--',*names]).split(b'\0'):
  if entry:
   meta,name=entry.split(b'\t',1);old[name.decode()]=meta.split()[2].decode()
 for name in names:
  raw=(ROOT/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==old[name],name
 for f in HERE.glob('s*.py'):compile(f.read_text(),str(f),'exec')
 subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True)
 subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],check=True)
 for name in ['report','notes']:
  log=(ROOT/'report'/(name+'.log')).read_text();assert not re.search(r'Overfull|undefined|^! ',log,re.M|re.I),name
  assert (ROOT/'report'/(name+'.pdf')).stat().st_size<32*1024**2
  bib=(ROOT/'report'/(name+'.blg')).read_text();assert not re.search(r'error message|Repeated entry|I couldn.t|Warning--',bib,re.I),name
 used=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file());assert used<20*1024**2
 plan=read(HERE/'resource_plan.json');peak=plan['persistent_upper_bytes']+plan['new_study_cap_bytes']+plan['publication_peak_reserve_bytes'];assert peak<10_000_000_000
 r=dict(complete=True,preserved_previous_sources=len(names),protocol_sha256=sha(HERE/'test_protocol.json.gz'),summary_sha256=sha(HERE/'summary.json'),model_sha256=p['model_sha256'],source_sha256={f.name:sha(f) for f in HERE.glob('s*.py')},pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},study_bytes=used,combined_peak_upper_bytes=peak,single_entry='s32_deploy.py',batch_entry='s33_batch.py',checks=s['checks']+final['checks'],final_summary_sha256=sha(HERE/'monitor_summary.json'))
 write(HERE/'validation.json',r);(ROOT/'report/triangle_validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
if __name__=='__main__':main()
