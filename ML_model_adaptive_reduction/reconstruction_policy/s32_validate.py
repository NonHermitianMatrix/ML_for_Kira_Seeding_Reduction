"""Validate the frozen comparison, preserved methods, documents, and storage."""
from s00_reconstruction_common import *
import re

def main():
 p=read(HERE/'test_protocol.json.gz');s=read(HERE/'summary.json')
 assert s['complete'] and s['protocol_sha256']==sha(HERE/'test_protocol.json.gz')
 assert len(p['cases'])==75 and len([c for c in p['cases'] if c['test_group']=='native'])==22
 assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items())
 assert all(sha(HERE/'trained_model'/n)==v for n,v in p['model_sha256'].items())
 assert sha(TOOLS/'kira')==p['binary_sha256']
 assert sha(ROOT/'.tools/kira-sector-wide/kira')==p['preceding_binary_sha256']
 assert read(HERE/'entry_checks.json')['complete']
 assert read(HERE/'kinematic_checks.json')['complete']
 model=read(HERE/'trained_model/policy.json')
 for n,v in model['source_sha256'].items():
  if sha(HERE/n)==v:continue
  assert n=='s14_train.py' and sha(HERE/'training_source'/n)==v
  current=(HERE/n).read_text();original=(HERE/'training_source'/n).read_text()
  assert current.replace("assert all(np.allclose(r['features'],features(c),rtol=0,atol=1e-12) for r in records.values()),c['id']","assert all(r['features']==features(c) for r in records.values()),c['id']")==original
 assert read(HERE/'entry_checks.json')['maximum_prediction_difference']<1e-12
 rp=read(HERE/'retained_protocol.json.gz');rs=read(HERE/'retained_summary.json')
 assert rs['complete'] and rs['protocol_sha256']==sha(HERE/'retained_protocol.json.gz')
 assert rp['parent_protocol_sha256']==sha(HERE/'test_protocol.json.gz')
 assert all(sha(HERE/n)==v for n,v in rp['sources'].items())
 assert all(sha(HERE/'trained_model'/n)==v for n,v in rp['models'].items())
 for c in p['cases']:
  r=read(HERE/'model_test'/(c['id']+'.json.gz'))
  assert all(len(r['times'][m])==len(r['success'][m])==3 for m in p['methods'])
  for m in p['methods']:assert all(v>=0 for v in r['times'][m])
  assert not r['results']['fixed'].get('reconstruction_decision',{}).get('model_used',False)
 for group in ['vacuum_products','connected_vacuum']:
  assert {r['loops'] for r in s['rows'] if r['group']==group}==set(range(1,14))
 assert not list((HERE/'requests').glob('*.json*'))
 # Preserve the previous exact routines and seed weights used by both controls.
 preserved=[]
 for folder in ['direct_analytic','lightlike_reduction','tensor_reduction','vacuum_learning']:
  base=ROOT/'ML_model_adaptive_reduction'/folder
  preserved.extend(base.glob('s*.py'))
  if (base/'trained_model/policy.json').exists():preserved.append(base/'trained_model/policy.json')
 names=[str(f.relative_to(ROOT)) for f in preserved]
 old={}
 for entry in subprocess.check_output(['git','ls-tree','-r','-z',PREVIOUS_COMMIT,'--',*names],cwd=ROOT).split(b'\0'):
  if entry:
   meta,name=entry.split(b'\t',1);old[name.decode()]=meta.split()[2].decode()
 for f,name in zip(preserved,names):
  raw=f.read_bytes();assert old[name]==hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),name
 for f in HERE.glob('s*.py'):compile(f.read_text(),str(f),'exec')
 subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True)
 subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],check=True)
 for name in ['report','notes']:
  log=(ROOT/'report'/(name+'.log')).read_text()
  assert 'Overfull' not in log and 'undefined' not in log.lower(),name
  assert (ROOT/'report'/(name+'.pdf')).stat().st_size<32*1024**2
  bib=(ROOT/'report'/(name+'.blg')).read_text()
  assert not re.search(r'error message|Repeated entry|I couldn.t|Warning--',bib,re.I),name
 plan=read(HERE/'resource_plan.json')
 assert plan['publish_peak_upper_bytes']<10_000_000_000
 assert allocated(HERE)<STUDY_LIMIT and allocated(TOOLS)<RETAINED_TOOLS_LIMIT
 assert allocated(STAGE)<4*1024**2
 v=dict(complete=True,previous_exact_and_models_unchanged=True,preserved_files=len(preserved),summary_sha256=sha(HERE/'summary.json'),protocol_sha256=sha(HERE/'test_protocol.json.gz'),retained_summary_sha256=sha(HERE/'retained_summary.json'),retained_protocol_sha256=sha(HERE/'retained_protocol.json.gz'),entry_checks_sha256=sha(HERE/'entry_checks.json'),model_sha256=p['model_sha256'],source_sha256={f.name:sha(f) for f in HERE.glob('s*.py')},report_source_sha256={f.name:sha(f) for f in (ROOT/'report').glob('*') if f.suffix in ['.tex','.bib']},pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},resource_plan_sha256=sha(HERE/'resource_plan.json'),study_allocated_bytes=allocated(HERE),tools_allocated_bytes=allocated(TOOLS),stage_allocated_bytes=allocated(STAGE),final_entry_point='s15_deploy.py',exact_coefficient_checks=s['checks'],completed=s['all']['new_completed'],reference_failures=s['reference_failures'])
 write(HERE/'validation.json',v)
 (ROOT/'report/reconstruction_validation.json').write_text(json.dumps(v,indent=2)+'\n')
 print(json.dumps({k:v for k,v in v.items() if 'source_sha256' not in k}),flush=True)
if __name__=='__main__':main()
