"""Compare fresh application processes without supplying reference coefficients to Kira."""
import json,os,statistics,subprocess,sys,tempfile,time
from pathlib import Path
from s00_probe import HERE,ROOT,rt,inputs,save

def main():
 f=rt.read(HERE/'trained_model/freeze.json');p=rt.read(HERE/'model_test/protocol.json');summary=[];records=[]
 for graph,v in f['selection'].items():
  if not v['option']:continue
  eligible=[c for c in p['cases'] if c['topology_group']==graph and (HERE/'model_test'/(c['id']+'_learned_r0.json.gz')).exists() and rt.read(HERE/'references'/(c['id']+'.json.gz'))['success']]
  if not eligible:continue
  c=eligible[0];ref=HERE/'references'/(c['id']+'.json.gz');times=dict(off=[],learned=[]);success=True
  for j in range(3):
   for method in (['off','learned'] if j%2==0 else ['learned','off']):
    dest=HERE/'application_test'/(c['id']+'_'+method+f'_r{j}.json.gz')
    if dest.exists():r=rt.read(dest)
    else:
     with tempfile.TemporaryDirectory(prefix='eq_live_application_',dir=os.environ['TMPDIR']) as tmp:
      tmp=Path(tmp);inputs.write(tmp/'case.json',c);inputs.write(tmp/'basis.json',rt.read(ref)['masters'])
      start=time.perf_counter();q=subprocess.run([sys.executable,str(HERE/'s07_reduce.py'),'--case',str(tmp/'case.json'),'--basis',str(tmp/'basis.json'),'--output',str(tmp/'output.json.gz'),'--method',method],capture_output=True,text=True,timeout=300)
      if q.returncode==0:r=rt.read(tmp/'output.json.gz');r['inner_seconds']=r['complete_seconds'];rt.verify(r,ref)
      else:r=dict(case=c['id'],method=method,success=False,stderr=q.stderr[-2500:],stdout=q.stdout[-1500:])
      r['complete_seconds']=time.perf_counter()-start;r['fresh_process']=True;save(dest,r)
    records.append(r);times[method].append(r['complete_seconds']);success=success and r['success']
    if r['success']:assert r['reference_checked'] and not r['reference_coefficients_supplied']
    print('APPLICATION',c['id'],method,j,r['success'],r['complete_seconds'],flush=True)
  if success:
   med={m:statistics.median(t) for m,t in times.items()};summary.append(dict(case=c['id'],graph=graph,seconds=med,ratio=med['learned']/med['off']))
 totals={m:sum(c['seconds'][m] for c in summary) for m in ['off','learned']}
 out=dict(complete=True,cases=summary,timed=len(records),successes=sum(r['success'] for r in records),totals=totals,ratio=totals['learned']/totals['off'] if summary else None,all_successful_outputs_exact=all(r.get('reference_checked') for r in records if r['success']),reference_coefficients_supplied=False,scope='First supported reserved request per validation-enabled graph; three rotated fresh-process repetitions. Same primary reserved inputs, not a new topology test.')
 inputs.write(HERE/'application_test/summary.json',out);assert summary and out['all_successful_outputs_exact']
if __name__=='__main__':main()
