"""Check C++ feature construction and selected tree decisions against saved feature rows."""
import os,subprocess,tempfile,time
from pathlib import Path
import numpy as np
from s00_probe import HERE,ROOT,BOUNDS,rt,inputs
from s02_train import FEATURES

def main():
 selected=rt.read(HERE/'trained_model/candidates.json')['candidates'];header=ROOT/'ML_model_equation_selection/early_generation/integration/s00_early_policy.h'
 names={o['name'] for options in selected.values() for o in options};fingerprint={n:inputs.sha(HERE/'trained_model'/(n+'.txt')) for n in sorted(names)};dest=HERE/'trained_model/prediction_parity.json'
 if dest.exists():
  old=rt.read(dest)
  if old['weights']==fingerprint and old['header_sha256']==inputs.sha(header):assert old['passed'];return
 start=time.perf_counter();cases={c['id']:c for c in rt.read(BOUNDS/'protocol.json')['splits']['validation']};records=[]
 with tempfile.TemporaryDirectory(prefix='eq_model_parity_',dir=os.environ['TMPDIR']) as scratch:
  scratch=Path(scratch);src=scratch/'check.cpp';exe=scratch/'check';context=scratch/'context.txt'
  src.write_text('#include <cstdint>\n#include <iostream>\n#include <string>\n#include <utility>\n#include <vector>\nnamespace pyred {using pow_type=int;using eqdata=std::vector<std::pair<int,std::string>>;}\n#include "'+str(header)+'"\nint main(){auto&s=kira_eq::state();size_t op;while(std::cin>>op){std::vector<int>a(s.targets.front().size());for(auto&v:a)std::cin>>v;std::cout<<kira_eq::precheck(a,op)<<"\\n";}}\n')
  subprocess.run(['g++','-O2','-std=c++17',str(src),'-o',str(exe)],check=True)
  for p in sorted((HERE/'validation').glob('*.json.gz')):
   if p.name.endswith('_failed.json.gz'):continue
   r=rt.read(p);c=cases[r['case']];assert len(r['candidate_keys'])==len(r['samples']);payload=[]
   for key in r['candidate_keys']:
    seed,op=key.split(':');payload.append(op+' '+' '.join(v for v in seed.split(',') if v))
   payload='\n'.join(payload)+'\n';context.write_text(f"{len(c['definition']['loop_momenta'])} {len(c['definition']['external_momenta'])} {c['size']} {len(c['targets'][0])}\n"+'\n'.join(' '.join(map(str,a)) for a in c['targets'])+'\n')
   for option in selected.get(r['graph'],[]):
    model=rt.read(HERE/'trained_model'/(option['name']+'.json.gz'));nodes=model['nodes'];want=[]
    for row in r['samples']:
     x=dict(zip(FEATURES,row[2:]));i=0
     while nodes[i]['feature']>=0:
      z=nodes[i];i=z['left'] if x[z['feature']]<=z['threshold'] else z['right']
     want.append(nodes[i]['probability']>=option['threshold'])
    env={k:v for k,v in os.environ.items() if not k.startswith('KIRA_')};env.update(KIRA_EQ_MODE='learned',KIRA_EQ_CONTEXT=str(context),KIRA_EQ_WEIGHTS=str(HERE/'trained_model'/(option['name']+'.txt')),KIRA_EQ_THRESHOLD=str(option['threshold']))
    raw=subprocess.check_output([str(exe)],input=payload,text=True,env=env);got=np.fromstring(raw,sep=' ',dtype=int)
    assert len(got)==len(want) and np.array_equal(got,np.array(want,dtype=int)),(r['case'],option)
    records.append(dict(case=r['case'],option=option,decisions=len(want),retained=int(got.sum())))
 out=dict(passed=True,decisions=sum(r['decisions'] for r in records),records=records,weights=fingerprint,header_sha256=inputs.sha(header),seconds=time.perf_counter()-start)
 inputs.write(dest,out);print('PREDICTION_PARITY',out['decisions'],flush=True)
if __name__=='__main__':main()
