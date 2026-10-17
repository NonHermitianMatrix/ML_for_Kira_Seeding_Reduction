"""Probe learned equation filtering with the tuned fixed seed configurations."""
import gzip,json,os,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];BOUNDS=ROOT/'ML_model_adaptive_reduction/learned_seed_bounds'
sys.path.insert(0,str(BOUNDS))
import s00_inputs as inputs
import s01_runtime as rt

def save(p,r):
 p.parent.mkdir(parents=True,exist_ok=True);raw=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0)
 used=sum(q.stat().st_blocks*512 for root in [HERE,BOUNDS] for q in root.rglob('*') if q.is_file())
 assert used+len(raw)<32*1024**2
 p.write_bytes(raw)

def attempt(c,basis,action,weight=None,threshold=.01,collect=False):
 with rt.environment():
  if weight:os.environ.update(KIRA_EQ_MODE='learned',KIRA_EQ_WEIGHTS=str(weight),KIRA_EQ_THRESHOLD=str(threshold))
  if collect:os.environ.update(KIRA_EQ_MODE='collect',KIRA_EQ_COLLECT='1',KIRA_RUNTIME_BINARY=str(ROOT/'.tools/kira-equation-selection/kira-lazy'))
  r=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=90,margin=0,archive=False,records=False,basis=basis,check_masters=True,scratch_cap=32*1024**2,bounds=inputs.bounds(c,action),ordering=1,threads=1,truncate=inputs.truncation(c,action))
 return r

def main():
 cfg=rt.read(BOUNDS/'trained_model/fixed.json');cases=rt.read(BOUNDS/'protocol.json')['splits']['training'];pairs=[('double_box','dots'),('double_box','mixed'),('ladder3','dots'),('vacuum3','dots'),('nonplanar_box','mixed'),('bubble_box3','dot'),('bubble_box4','corner'),('massless4','dot')]
 selected=[c for c in cases if '_h511_' in c['id'] and (c['topology_group'],c['shape']) in pairs]
 inputs.write(HERE/'development/protocol.json',dict(cases=selected,source='Previous training inputs only; no reserved results used.',settings=['off','early8','early12','family'],threshold=.01))
 for c in selected:
  ref=BOUNDS/'references'/(c['id']+'.json.gz');basis=rt.read(ref)['masters'];action=cfg['fixed_by_graph'][c['topology_group']]
  for name in ['off','early8','early12','family']:
   p=HERE/'development'/(c['id']+'_'+name+'.json.gz')
   if p.exists():continue
   weight=None if name=='off' else ROOT/'ML_model_equation_selection/early_generation/trained_model'/('early_d8' if name=='early8' else 'early_d12')/'weights.txt'
   if name=='family':
    weight=ROOT/'ML_model_equation_selection/scattering_training/trained_model'/(c['topology_group']+'.txt')
    if not weight.exists():continue
   start=time.perf_counter();r=attempt(c,basis,action,weight);attempts=[rt.compact(r)]
   if not r['success'] and weight:
    r=attempt(c,basis,action);attempts.append(rt.compact(r))
   out=dict(case=c['id'],model=name,seed_action=action,success=r['success'],attempts=attempts,coefficients=r.get('coefficients',{}),reference_coefficients_supplied=False)
   rt.verify(out,ref);out['complete_seconds']=time.perf_counter()-start;save(p,out)
   print(json.dumps(dict(case=c['id'],model=name,seconds=out['complete_seconds'],success=out['success'],fallbacks=len(attempts)-1,eq=[a.get('equation_metrics') for a in attempts])),flush=True)
 inputs.write(HERE/'development/completion.json',dict(complete=True))
if __name__=='__main__':main()
