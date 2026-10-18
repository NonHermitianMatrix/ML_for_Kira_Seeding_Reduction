"""Fresh verification of basis refresh, with frozen models and complete timers."""
from s00_common import *
from s14_prepare import equal
import subprocess
R=HERE/'recovery';P=HERE/'preparation'

def initialize():
 if (R/'protocol.json').exists():return
 groups=['vacuum_all_mass_L4','vacuum_all_mass_L5','propagator_massless_L3','propagator_massive_L3','bubble_box_L3','ladder_L2']
 selected=[c for c in cases(1249) if c['topology_group'] in groups and c['shape']==('dots' if len(c['definition']['loop_momenta'])%2 else 'mixed')]
 assert len(selected)==6
 write(R/'protocol.json',dict(cases=selected,profile=1249,methods=['cached_native','cached_learned','cached_risk'],repetitions=3,total_budget_seconds=110,runtime_sha256=inputs.sha(HERE/'s20_prepare_resilient.py'),risk_sha256=inputs.sha(P/'trained_model/freeze.json'),neural_sha256=inputs.sha(HERE/'refit/trained_model/freeze.json'),cache_sha256=inputs.sha(P/'basis_cache.json'),scope='Fresh parameters after the profile 1237 experiment exposed an incomplete reused basis. Same frozen models and cache. Basis refresh and expanded target checking apply equally to all three controls. This is a focused recovery test, not a new broad coverage claim.'))

def main(worker):
 protocol=READ(R/'protocol.json');assert inputs.sha(HERE/'s20_prepare_resilient.py')==protocol['runtime_sha256']
 assert inputs.sha(P/'trained_model/freeze.json')==protocol['risk_sha256'];assert inputs.sha(HERE/'refit/trained_model/freeze.json')==protocol['neural_sha256'];assert inputs.sha(P/'basis_cache.json')==protocol['cache_sha256']
 for c in protocol['cases'][worker::2]:
  coverage=R/'coverage'/(c['id']+'.json')
  if coverage.exists():continue
  first={};results={};methods=protocol['methods']
  for rep in range(3):
   shift=(sum(c['id'].encode())+rep)%len(methods)
   for m in methods[shift:]+methods[:shift]:
    if rep and not first[m]['success']:continue
    file=R/'model_test'/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz')
    if file.exists():r=READ(file)
    else:
     request=R/'requests'/(file.stem+'.json');out=file.with_name(file.name+'.pending.gz');file.parent.mkdir(parents=True,exist_ok=True);write(request,dict(case=c,method=m));tick=time.perf_counter()
     process=subprocess.run([sys.executable,str(HERE/'s20_prepare_resilient.py'),'--input',str(request),'--output',str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=145)
     r=READ(out) if out.exists() else dict(success=False,status='process_error',error=process.stderr.decode()[-1200:])
     r.update(case=c['id'],method=m,complete_seconds=time.perf_counter()-tick,process_timer_complete=True);write(file,r);request.unlink()
     if out.exists():out.unlink()
    if rep==0:first[m]=r
    results.setdefault(m,[]).append(r)
    print(c['id'],m,rep,r['success'],r.get('basis_refreshed'),round(r['complete_seconds'],3),flush=True)
  write(coverage,dict(case=c['id'],first_success={m:r['success'] for m,r in first.items()},three_complete={m:len(v)==3 and all(r['success'] for r in v) for m,v in results.items()}))
 write(R/('worker_'+str(worker)+'_complete.json'),dict(complete=True,runtime_sha256=protocol['runtime_sha256']))

def analyze():
 from s17_analyze_preparation import paired
 protocol=READ(R/'protocol.json');methods=protocol['methods'];rows=[];checks=0
 for w in [0,1]:assert READ(R/('worker_'+str(w)+'_complete.json'))['complete']
 for c in protocol['cases']:
  rs={};complete={};pairs={}
  for m in methods:
   first=READ(R/'model_test'/(c['id']+'_'+m+'_r0.json.gz'));rs[m]=[READ(R/'model_test'/(c['id']+'_'+m+'_r'+str(j)+'.json.gz')) for j in range(3 if first['success'] else 1)]
   complete[m]=len(rs[m])==3 and all(r['success'] for r in rs[m])
   for r in rs[m]:
    assert r['process_timer_complete'];checks+=r.get('coefficient_checks',0)
    if r['success']:
     agree,num=equal(r['coefficients'],first['coefficients']);checks+=num;assert agree
     assert {tuple(v) for v in r['masters']}=={tuple(v) for v in first['masters']}
  for a in methods:
   for b in methods:
    if a==b:continue
    same=complete[a] and complete[b] and {tuple(v) for v in rs[a][0]['masters']}=={tuple(v) for v in rs[b][0]['masters']}
    agree,num=equal(rs[a][0]['coefficients'],rs[b][0]['coefficients']) if same else (False,0);checks+=num
    if same:assert agree
    pairs[a+'/'+b]=dict(agree=agree,same_basis=bool(same))
  rows.append(dict(id=c['id'],loops=len(c['definition']['loop_momenta']),complete=complete,pairs=pairs,times={m:[r['complete_seconds'] for r in v] for m,v in rs.items()},first_action={m:v[0].get('first_action') for m,v in rs.items()},basis_refreshed={m:v[0].get('basis_refreshed',False) for m,v in rs.items()},failed_attempts={m:sum(r.get('failed_attempts',0) for r in v) for m,v in rs.items()}))
 comparisons={a+'/cached_native':paired(rows,a,'cached_native') for a in ['cached_learned','cached_risk']}
 summary=dict(complete=True,requests=6,rows=rows,comparisons=comparisons,coefficient_checks=checks,all_matched_exact=True,completed={m:sum(r['complete'][m] for r in rows) for m in methods},refreshed={m:sum(r['basis_refreshed'][m] for r in rows) for m in methods},scope=protocol['scope'])
 write(R/'summary.json',summary);write(ROOT/'report/recovery_data.json',summary)
 print(json.dumps({k:v for k,v in summary.items() if k!='rows'}),flush=True)

if __name__=='__main__':
 if sys.argv[1]=='initialize':initialize()
 elif sys.argv[1]=='analyze':analyze()
 else:main(int(sys.argv[1]))
