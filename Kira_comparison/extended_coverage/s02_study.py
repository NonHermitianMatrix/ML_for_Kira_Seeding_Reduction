"""Evaluate each frozen case and retain every failure."""
import argparse,subprocess,sys,time
from s00_protocol import HERE,ROOT,read,write
PYTHON=ROOT/'.tools/seed-model/venv/bin/python'
def call(c,method,dest,basis=None,reference=None,sequence=None):
 if dest.exists():return read(dest)
 req=dict(case=c,method=method,basis=basis,reference=str(reference) if reference else None,sequence=sequence)
 p=HERE/'requests'/(dest.stem+'.json');write(p,req)
 start=time.perf_counter();proc=subprocess.run([str(PYTHON),str(HERE/'s01_call.py'),'--input',str(p),'--output',str(dest)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 elapsed=time.perf_counter()-start
 r=read(dest) if dest.exists() else dict(success=False,status='worker_exit',exit_code=proc.returncode,error=proc.stderr.decode()[-1800:])
 r.update(complete_seconds=elapsed,case=c['id'],method=method);write(dest,r);p.unlink()
 print(c['id'],method,r['success'],r.get('status',''),round(elapsed,3),flush=True);return r

def process(c):
 coverage=HERE/'coverage'/(c['id']+'.json')
 if coverage.exists():return
 info={k:c[k] for k in ['id','loops','indices','coverage_type','kinematics']}
 if c['preflight']!='eligible':write(coverage,dict(info,status=c['preflight']));return
 rp=HERE/'references'/(c['id']+'.json.gz');r=call(c,'reference',rp)
 if not r['success']:write(coverage,dict(info,status='reference_failed',reason=r.get('status'),reference_seconds=r['complete_seconds']));return
 basis=r['masters'];cp=HERE/'references'/(c['id']+'_check.json.gz');check=call(c,'check',cp,basis,rp)
 if not check['success']:write(coverage,dict(info,status='reference_check_failed',reason=check.get('status')));return
 nontrivial=any(row and row!={t:'1'} for t,row in r.get('coefficients',{}).items())
 failed=set();methods=['native','previous','selected']
 for rep in range(3):
  shift=(sum(c['id'].encode())+rep)%3
  for method in methods[shift:]+methods[:shift]:
   if method in failed:continue
   result=call(c,method,HERE/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz',basis,rp)
   if not result['success']:failed.add(method)
 write(coverage,dict(info,status='verified' if not failed else 'method_failed',failed_methods=sorted(failed),nontrivial=nontrivial,masters=len(basis),reference_seconds=r['complete_seconds'],check_seconds=check['complete_seconds']))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worker',type=int,default=0);p.add_argument('--pilot',action='store_true');a=p.parse_args();protocol=read(HERE/'protocol.json')
 cases=protocol['cases']
 if a.pilot:cases=[c for c in cases if c['id'] in ['vacuum_one_mass_L1_h1001','double_box_h1009_distributed3']]
 else:cases=cases[a.worker::2]
 for c in cases:process(c)
 write(HERE/('pilot_completion.json' if a.pilot else f'completion_{a.worker}.json'),dict(complete=True,cases=len(cases)))
