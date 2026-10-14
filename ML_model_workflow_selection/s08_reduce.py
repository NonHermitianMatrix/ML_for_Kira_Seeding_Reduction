"""Apply the frozen complete-cost selector with a supplied master basis."""
import argparse,json,time
from pathlib import Path
from s05_study import HERE,ROOT,CONFIGS,BINARY,sha,choose,workflow,save,features

def structure(c):
 d=c['definition']
 return (tuple(d['loop_momenta']),tuple(d['external_momenta']),d['physical_propagators'],
  tuple((p['momentum'],p['mass_squared']=='0') for p in d['propagators']),
  tuple(tuple(k) for k,v in d['scalarproduct_rules']),tuple(tuple(v) for v in d['invariants']))

def select(c,frozen,manifest):
 training=[r for r in manifest['cases'] if r['split']=='training' and structure(r)==structure(c)]
 if not training:return 'fixed','unmatched_structure'
 c['topology_group']=training[0]['topology_group'];x=features(c);xs=[features(r) for r in training]
 # Restrict the learned route to the observed target complexity envelope.
 for j in range(8):
  if x[j]<min(v[j] for v in xs)-1e-12 or x[j]>max(v[j] for v in xs)+1e-12:return 'fixed','outside_training_range'
 return choose(frozen['model'],c,frozen['gate']),'learned'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--basis',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
 a=ap.parse_args()
 assert a.output.resolve().is_relative_to((HERE/'model_test').resolve())
 begin=time.perf_counter();c=json.loads(a.input.read_text());basis=json.loads(a.basis.read_text())
 assert 1<=len(c['targets'])<=128 and all(len(t)==len(c['definition']['propagators']) for t in c['targets'])
 c['size']=len(c['targets']);c.setdefault('split','application');c.setdefault('group',c['id'])
 manifest=json.loads((HERE/'cases.json').read_text());f=json.loads((HERE/'trained_model/freeze.json').read_text())
 assert sha(BINARY)==f['binary_sha256']
 for p,h in f['weights'].items():assert sha(ROOT/p)==h
 cfg,reason=select(c,f,manifest);decision=time.perf_counter()-begin
 r=workflow(c,None,cfg,basis=basis);r.update(complete_seconds=time.perf_counter()-begin,decision_seconds=decision,selection_reason=reason,answers_withheld=True)
 assert a.output.resolve().is_relative_to((HERE/'model_test').resolve())
 save(a.output,r);print(json.dumps(dict(success=r['success'],configuration=cfg,reason=reason,seconds=r['complete_seconds'])))
 if not r['success']:raise SystemExit(1)
if __name__=='__main__':main()
