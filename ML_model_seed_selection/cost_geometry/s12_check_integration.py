"""Check model parity, physics guards, and the integrated application."""
import copy,json,os,statistics,subprocess,sys,tempfile,time
from s00_policy import *
from s05_reduce import feature,predict,choose
from s11_integrated import supports

def main():
 folder=HERE/'integration_test';folder.mkdir(exist_ok=True)
 (folder/'README.md').write_text('These checks compare the public integrated application with its preceding workflow.\nThey also check exported model predictions and physical input guards.\nThe models stay fixed and no test result changes a threshold.\n')
 parity=0;guards=0;cases=[]
 from s04_cost_model import feature as training_feature,predict as training_predict
 for g in ['double_box','nonplanar_box']:
  f=rt.read(HERE/'trained_model'/('cost_'+g+'.json'));p=rt.read(HERE/'protocols'/('cost_'+g+'.json'))
  for c in p['training']+p['validation']+p['reserved']:
   assert feature(c)==training_feature(c)
   assert predict(f['model'],feature(c))==training_predict(f['model'],feature(c));parity+=1
  c=p['reserved'][0]
  for kind in ['rank','dots','sector','mass','size']:
   q=copy.deepcopy(c);physical=q['definition']['physical_propagators']
   if kind=='rank':q['targets'][0][physical]=-5
   elif kind=='dots':q['targets'][0][0]=2
   elif kind=='sector':q['targets'][0][0]=0
   elif kind=='mass':q['definition']['propagators'][0]['mass_squared']='19'
   elif kind=='size':q['targets'].append(q['targets'][0].copy());q['size']=2
   assert choose(q,f,'learned')[1]['reason']=='outside_validated_domain';guards+=1
  cases.extend(c for c in p['reserved'] if '_h851_' in c['id'] and c['shape']=='single4')
 # A four-loop request outside the fitted graph domain keeps the old native path.
 batch=ROOT/'ML_model_adaptive_reduction/batch_policy'
 other=next(c for c in rt.read(batch/'model_test/protocol.json')['cases'] if c['topology_group']=='massless4' and '_h721_' in c['id'] and c['shape']=='all')
 cases.append(other)
 banana=ROOT/'ML_model_adaptive_reduction/massless_banana'
 sys.path.insert(0,str(banana));module=inputs.module('geometry_formula_checks',banana/'s05_route_test.py')
 c=module.analytic_case(8,901,False);cases.append(c)
 analytic_ref=module.analytic_reference(c)
 inputs.write(folder/'protocol.json',dict(cases=cases,methods=['previous','integrated'],repetitions=3,selection='Rank-four targets at the first reserved profile, a preceding four-loop batch, and an eight-loop analytic request.'))
 for i,c in enumerate(cases):
  if c['id'].startswith('analytic_'):ref=analytic_ref;reference=folder/'analytic_reference.json';inputs.write(reference,ref)
  else:
   reference=(HERE/'references' if c['topology_group']!='massless4' else batch/'references')/(c['id']+'.json.gz');ref=rt.read(reference)
  if not ref['success']:continue
  with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR'],prefix='integrated_seeds_') as tmp:
   tmp=Path(tmp);cp=tmp/'case.json';bp=tmp/'basis.json';out=tmp/'output.json.gz'
   cp.write_text(json.dumps({k:c[k] for k in ['id','size','definition','targets']}));bp.write_text(json.dumps(ref['masters']))
   for rep in range(3):
    methods=['previous','integrated'];methods=methods[(i+rep)%2:]+methods[:(i+rep)%2]
    for method in methods:
     path=folder/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
     if path.exists():continue
     start=time.perf_counter();command=[sys.executable,str(HERE/'s11_integrated.py'),'--case',str(cp),'--basis',str(bp),'--output',str(out)]+(['--previous'] if method=='previous' else [])
     p=subprocess.run(command,capture_output=True,text=True,timeout=300,preexec_fn=rt.native.limits)
     if p.returncode==0:r=rt.read(out);rt.verify(r,reference)
     else:r=dict(success=False,error=p.stderr[-3000:])
     r.update(case=c['id'],method=method,repetition=rep,process_complete_seconds=time.perf_counter()-start,reference_coefficients_supplied=False);save(path,r)
     print(json.dumps({k:r[k] for k in ['case','method','success','process_complete_seconds']}),flush=True)
 rows=[rt.read(p) for p in folder.glob('*.json.gz')]
 assert len(rows)==24 and all(r['success'] for r in rows),[(r['case'],r.get('error')) for r in rows if not r['success']]
 expected={c['id']:('proven_massless_banana' if c['id'].startswith('analytic_') else 'cost_trained_sparse_seeds' if supports(c) else 'native_kira_with_batch_policy') for c in cases}
 for r in rows:
  if r['method']=='integrated':assert r['route']==expected[r['case']],r['case']
 inputs.write(folder/'summary.json',dict(complete=True,all_exact=True,requests=len(rows),model_parity_checks=parity,guard_checks=guards,routes=expected,source_sha256={n:inputs.sha(HERE/n) for n in ['s00_policy.py','s05_reduce.py','s11_integrated.py']}))
 print('INTEGRATION_CHECKS_COMPLETE',flush=True)
if __name__=='__main__':main()
