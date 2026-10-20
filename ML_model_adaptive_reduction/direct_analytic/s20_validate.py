"""Validate frozen evidence, explicit analytic values, documents, and limits."""
from s00_direct_common import *
from s14_prepare import sha
import subprocess,re

def value_checks(p,folder='model_test'):
 import mpmath as mp
 mp.mp.dps=30;rho=mp.mpf('1.713');checks=0
 for c in p['cases']:
  if c['test_group']!='connected_vacuum':continue
  row=read(HERE/folder/(c['id']+'.json.gz'));r=row['results']['integrated']['blocks'][0]['result'];value=next(iter(r['master_values'].values()));L=len(c['definition']['loop_momenta']);P=2*L-1
  # Independent leaf-to-root Gamma evaluation at unit physical powers.
  transfer=[mp.mpf(0) for _ in range(L)];gamma=mp.mpf(1)
  for j in reversed(range(1,L)):
   parent=0 if c['shape']=='star' else j-1 if c['shape']=='chain' else (j-1)//2
   u=1+transfer[j];v=1;gamma*=mp.gamma(u+v-rho)*mp.gamma(rho-u)*mp.gamma(rho-v)/(mp.gamma(u)*mp.gamma(v)*mp.gamma(2*rho-u-v));transfer[parent]+=u+v-rho
  gamma*=mp.gamma(rho-transfer[0])*mp.gamma(transfer[0]+1-rho)/mp.gamma(rho)
  returned=mp.fprod(mp.gamma(a+b*rho) for a,b in value['gamma_numerator'])/mp.fprod(mp.gamma(a+b*rho) for a,b in value['gamma_denominator']);assert abs((returned-gamma)/gamma)<mp.mpf('1e-24');assert value['sign']==(-1)**P and value['mass_exponent']==[-P,L];checks+=1
 return checks

def main():
 p=read(HERE/'protocol.json.gz');s=read(HERE/'summary.json');m=read(HERE/'trained_model/policy.json');assert s['complete'] and len(p['cases'])==69 and len(p['extended_cases'])==26
 assert s['protocol_sha256']==sha(HERE/'protocol.json.gz') and all(sha(HERE/n)==h for n,h in p['source_sha256'].items());assert sha(HERE/'trained_model/policy.json')==p['model_sha256'];assert sha(PRIOR/'s05_runtime.py')==p['previous_entry_sha256'];assert read(HERE/'checks.json')['complete']
 for c in p['cases']+p['extended_cases']:
  r=read(HERE/'model_test'/(c['id']+'.json.gz'));assert r['reference_success'] and all(len(v)==3 for v in r['times'].values())
  if 'fixed' in r['results']:assert not r['results']['fixed'].get('model_used',False)
 for g in ['vacuum_products','connected_vacuum','extended_vacuum','scaleless_vacuum']:assert {r['loops'] for r in s['rows'] if r['group']==g}==set(range(1,14))
 assert not list((HERE/'requests').glob('*.json*'));gamma_checks=value_checks(p)
 for n in ['ML_model_adaptive_reduction/lightlike_reduction/s05_runtime.py','ML_model_adaptive_reduction/lightlike_reduction/trained_model/policy.json','ML_model_adaptive_reduction/tensor_reduction/s17_fast_tensor.py']:
  raw=(ROOT/n).read_bytes();import hashlib
  oid=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert subprocess.check_output(['git','ls-tree',p['prior_commit'],'--',n],cwd=ROOT,text=True).split()[2]==oid
 for f in HERE.glob('s*.py'):compile(f.read_text(),str(f),'exec')
 subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True);subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],check=True)
 for name in ['report','notes']:
  log=(ROOT/'report'/(name+'.log')).read_text();assert 'Overfull' not in log and 'undefined' not in log.lower(),name;assert (ROOT/'report'/(name+'.pdf')).stat().st_size<32*1024**2
  bib=(ROOT/'report'/(name+'.blg')).read_text();assert not re.search(r'error message|Repeated entry|I couldn.t|Warning--',bib,re.I),name
 size=sum(f.stat().st_blocks*512 for f in HERE.rglob('*') if f.is_file());assert size<12*1024**2;plan=read(HERE/'resource_plan.json');assert not plan['provisional'] and max(plan[k] for k in ['compute_peak_upper_bytes','publish_peak_upper_bytes','preview_peak_upper_bytes'])<10_000_000_000
 v=dict(complete=True,prior_models_unchanged=True,preceding_exact_unchanged=True,summary_sha256=sha(HERE/'summary.json'),protocol_sha256=sha(HERE/'protocol.json.gz'),source_sha256={f.name:sha(f) for f in HERE.glob('s*.py')},model_sha256=sha(HERE/'trained_model/policy.json'),appendix_sha256=sha(HERE/'direct_appendix.tex'),report_source_sha256={f.name:sha(f) for f in (ROOT/'report').glob('*') if f.suffix in ['.tex','.bib']},pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},final_entry_point='s01_runtime.py',study_allocated_bytes=size,exact_coefficient_checks=s['checks'],connected_analytic_value_checks=gamma_checks,completed=s['all']['new_completed'],resource_plan_sha256=sha(HERE/'resource_plan.json'))
 write(HERE/'validation.json',v);(ROOT/'report/direct_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v for k,v in v.items() if 'source_sha256' not in k}),flush=True)
if __name__=='__main__':main()
