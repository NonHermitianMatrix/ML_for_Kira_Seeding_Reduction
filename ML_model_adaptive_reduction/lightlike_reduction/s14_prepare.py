"""Freeze the integrated model and a new complete-time comparison."""
from s00_light_common import *
from s02_cases import case,product
from s06_native_cases import native_cases

def cases():
 out=[]
 for j,kind in enumerate(['unequal','equal','mixed','massless']):
  for rank in range(5):
   c=case(211+17*j+rank,kind,rank,min(rank,3),3);c['split']='reserved';out.append(c)
 for j,kind in enumerate(['unequal','equal','mixed']):
  c=case(301+j,kind,0,0,1);c['definition']['invariants']=[['x',2],['y',2]];c['definition']['propagators'][0]['mass_squared']='x';c['definition']['propagators'][1]['mass_squared']={'unequal':'y','equal':'x','mixed':'0'}[kind];c['targets']=[[1,1,0,0],[2,1,0,0],[1,2,0,0],[2,2,0,0]];c.update(id=c['id']+'_symbolic',test_group='symbolic',split='reserved',size=4);out.append(c)
 for L in range(2,14):
  c=product(case(351+L,'unequal' if L%2 else 'equal',2,1,3),L);c['split']='reserved';out.append(c)
 for j,kind in enumerate(['unequal','equal','mixed']):
  c=case(391+j,kind,1,1,1);c['definition']['physical_propagators']=3;c['definition']['top_level_sectors']=[7];c['definition']['propagators'][2]['mass_squared']=str(421+j);c['targets']=[[2,1,1,-1],[1,2,1,-1],[2,1,0,-1]];c.update(id=c['id']+'_embedded',test_group='embedded',split='reserved',size=3);out.append(c)
 oldcases=load('lightlike_old_tensor_cases',PRIOR/'s03_cases.py')
 for P,e in [(2,1),(3,1),(4,1)]:
  c=oldcases.case(P,e,433+P,rank=2,dots=1,count=3);c.update(test_group='ordinary_tensor',split='reserved');out.append(c)
 vac=previous().previous();vcases=load('lightlike_vacuum_cases',vac.HERE/'s04_cases.py')
 for L in [1,7,13]:
  c=vcases.vacuum_case(L,'chain',461+L,count=4);c['test_group']='vacuum';out.append(c)
 out+=native_cases('reserved');return out

def main():
 assert read(HERE/'checks.json')['complete']
 from s13_extended_checks import main as checks
 checks()
 from s10_train import main as train
 train()
 splits={phase:{(('nonplanar' if 'nonplanar' in c['id'] else 'planar'),tuple(sorted(tuple(t) for t in c['targets']))) for c in native_cases(phase)} for phase in ['training','validation','reserved']}
 assert not (splits['training'] & splits['validation'] or splits['training'] & splits['reserved'] or splits['validation'] & splits['reserved'])
 p=dict(cases=cases(),repetitions=3,seconds_per_application=20,source_sha256={p.name:sha(p) for p in HERE.glob('s*.py') if int(p.name[1:3])<=16 or int(p.name[1:3])==21},model_sha256=sha(HERE/'trained_model/policy.json'),prior_commit='9daaa6322a6931206ac51589655f2f06f5803920',previous_entry_sha256=sha(PRIOR/'s18_fast_runtime.py'))
 write(HERE/'protocol.json.gz',p);print(json.dumps({'frozen':True,'requests':len(p['cases'])}),flush=True)
if __name__=='__main__':main()
