"""Measure new processes with physical inputs and basis, without reference answers."""
import json,os,statistics,subprocess,sys,tempfile,time
from s00_policy import *
def main():
 folder=HERE/'application';folder.mkdir(exist_ok=True)
 (folder/'README.md').write_text('These tests start a new process for each reduction.\nInputs contain a physical family, target indices, and a master basis.\nReference coefficients enter only the later exact check.\nTimes include imports, model loading, file output, process exit, and that check.\n')
 cases=[]
 for g in ['double_box','nonplanar_box']:
  cases.extend([c for c in rt.read(HERE/'protocols'/('cost_'+g+'.json'))['reserved'] if '_h851_' in c['id'] and c['shape'] in ['single2','single4']])
 inputs.write(folder/'protocol.json',dict(cases=cases,methods=['native','fixed','learned','previous'],repetitions=3,selection='First reserved profile; single numerator at ranks two and four. No observed test timing enters this choice.'))
 for i,c in enumerate(cases):
  refpath=HERE/'references'/(c['id']+'.json.gz');ref=rt.read(refpath)
  if not ref['success']:continue
  with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR'],prefix='seed_application_') as tmp:
   t=Path(tmp);cp=t/'case.json';bp=t/'basis.json';out=t/'output.json.gz'
   cp.write_text(json.dumps({k:c[k] for k in ['id','definition','targets','size']}));bp.write_text(json.dumps(ref['masters']))
   for rep in range(3):
    order=['native','fixed','learned','previous'];k=(i+rep)%4;order=order[k:]+order[:k]
    for method in order:
     dest=folder/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
     if dest.exists():continue
     begin=time.perf_counter()
     command=[sys.executable,str(HERE/'s05_reduce.py'),'--case',str(cp),'--basis',str(bp),'--output',str(out),'--method',method]
     p=subprocess.run(command,capture_output=True,text=True,timeout=300,preexec_fn=rt.native.limits)
     if p.returncode==0:
      r=rt.read(out);rt.verify(r,refpath)
     else:r=dict(success=False,error=p.stderr[-2000:])
     r.update(case=c['id'],method=method,repetition=rep,process_complete_seconds=time.perf_counter()-begin,reference_coefficients_supplied=False,returncode=p.returncode)
     save(dest,r);print(json.dumps({k:r[k] for k in ['case','method','success','process_complete_seconds']}),flush=True)
 records=[rt.read(p) for p in folder.glob('*.gz')];matched=[]
 for c in cases:
  rows=[r for r in records if r['case']==c['id']]
  if len(rows)==12 and all(r['success'] for r in rows):matched.append(dict(case=c['id'],times={m:statistics.median(r['process_complete_seconds'] for r in rows if r['method']==m) for m in ['native','fixed','learned','previous']}))
 totals={m:sum(r['times'][m] for r in matched) for m in ['native','fixed','learned','previous']}
 inputs.write(folder/'summary.json',dict(complete=True,requests=len(records),matched=len(matched),all_exact=all(r['success'] for r in records),rows=matched,totals=totals))
if __name__=='__main__':main()
