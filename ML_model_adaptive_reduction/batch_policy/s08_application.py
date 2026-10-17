"""Time fresh application processes, including imports, output and exact checks."""
import json,os,statistics,subprocess,sys,tempfile,time
from pathlib import Path
from s00_runtime import HERE,ROOT,rt,inputs,save

def main():
 p=rt.read(HERE/'model_test/protocol.json');cases=[]
 for g in ['double_box','ladder3','nonplanar_box','massless4']:
  eligible=[c for c in p['cases'] if c['topology_group']==g and '_h721_' in c['id'] and c['shape']=='all']
  if eligible:
   c=eligible[0];q=HERE/'references'/(c['id']+'.json.gz')
   if q.exists() and rt.read(q)['success']:cases.append(c)
 protocol=dict(cases=cases,methods=['previous','fixed_off','learned'],repetitions=3,selection='First reserved profile, all-target pattern, four predeclared graphs; reference success only.',freeze_sha256=p['freeze_sha256'])
 protocol['implementation']='Compact deployment; identical frozen choices, with unused tree arrays omitted when the predictor is disabled.'
 protocol['deployment_sha256']=inputs.sha(HERE/'trained_model/deployment.json')
 protocol['application_input_fields']=['id','size','targets','definition']
 dest=HERE/'application'
 if (dest/'protocol.json').exists():assert rt.read(dest/'protocol.json')==protocol
 else:inputs.write(dest/'protocol.json',protocol)
 for ci,c in enumerate(cases):
  ref=HERE/'references'/(c['id']+'.json.gz');basis=rt.read(ref)['masters']
  for j in range(protocol['repetitions']):
   methods=protocol['methods'];off=(ci+j)%len(methods)
   for method in methods[off:]+methods[:off]:
    path=dest/(c['id']+'_'+method+f'_r{j}.json.gz')
    if path.exists():continue
    with tempfile.TemporaryDirectory(prefix='batch_application_',dir=os.environ['TMPDIR']) as work:
     work=Path(work);inputs.write(work/'case.json',{k:c[k] for k in protocol['application_input_fields']});inputs.write(work/'basis.json',basis)
     begin=time.perf_counter();call=subprocess.run([sys.executable,str(HERE/'s16_deployment.py'),'--case',str(work/'case.json'),'--basis',str(work/'basis.json'),'--output',str(work/'answer.json.gz'),'--method',method],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=200)
     assert call.returncode==0,call.stdout[-2000:]
     r=rt.read(work/'answer.json.gz');rt.verify(r,ref);r['application_seconds']=time.perf_counter()-begin;r['process_output']=call.stdout[-600:];save(path,r)
     print('APPLICATION',c['id'],method,j,r['success'],r['application_seconds'],flush=True)
 rows=[];runs=0
 for c in cases:
  d={m:[rt.read(dest/(c['id']+'_'+m+f'_r{j}.json.gz')) for j in range(3)] for m in protocol['methods']};runs+=sum(len(v) for v in d.values())
  rows.append(dict(case=c['id'],success=all(r['success'] for rs in d.values() for r in rs),seconds={m:statistics.median(r['application_seconds'] for r in rs) for m,rs in d.items()}))
 matched=[r for r in rows if r['success']];totals={m:sum(r['seconds'][m] for r in matched) for m in protocol['methods']}
 out=dict(complete=True,cases=rows,matched=len(matched),timed=runs,totals=totals,ratios={m:totals['learned']/totals[m] for m in ['previous','fixed_off']} if matched else {},costs='New Python process, policy import, input/output, native generation, exact algebra, recovery and coefficient check. Reference construction excluded.')
 inputs.write(dest/'summary.json',out);print('APPLICATION_SUMMARY',json.dumps(out),flush=True)

if __name__=='__main__':main()
