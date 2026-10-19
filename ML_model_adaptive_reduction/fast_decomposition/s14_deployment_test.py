"""Test the full-cost admission rule on fresh requests after its decision."""
from s00_fast_common import *
from s07_cases import load_physics,set_case
from s13_application_gate import measure,DEP

def cases():
 old,h,polys,families=load_physics();out=[]
 for n in [3,4,5]:
  for index,a in enumerate([[3,2]+[1]*(n-2),[1]*(n-2)+[2,3]]):
   c=polys.polygon(n,2917,1);c['id']=f'final_polygon_n{n}_shape{index}';out.append(set_case(c,'recurrence',[a]))
 for L in [2,13]:
  blocks=[]
  for b in range(L):
   c=polys.polygon(3,2927,1)
   for prop in c['definition']['propagators']:prop['mass_squared']=str(int(prop['mass_squared'])+7*b+L)
   c['targets']=[[2,1,1]];c['size']=1;blocks.append(c)
  out.append(set_case(families.compose(blocks,f'final_distinct_triangles_L{L}','reserved'),'products'))
 c=h.inputs.case('nonplanar_box',2939,'rank2','reserved');c['id']='final_nonplanar_h2939';out.append(set_case(c,'learned_native',[[1]*7+[-3,0]]))
 out.append(set_case(polys.polygon(2,2941,1,True),'symbolic_native'))
 for kind in ['vacuum_one_mass','propagator_massless']:out.append(set_case(h.gen.case(kind,13,False,2953),'finite_formula'))
 assert len(out)==12;return out

def main():
 admission=read(DEP/'admission.json');assert admission['complete'];original=read(HERE/'protocol.json')
 if not (DEP/'protocol.json').exists():
  p=dict(complete=True,cases=cases(),methods=['final','candidate','fixed_recurrence','previous'],repetitions=3,admission_sha256=sha(DEP/'admission.json'),model_sha256=sha(HERE/'trained_model/recurrence.json'),source_sha256={q.name:sha(q) for q in HERE.glob('s*.py') if q.name[:3] in ['s00','s01','s02','s03','s07','s08','s12','s13','s14']},prior_basis_sha256=original['prior_basis_sha256'],scope='Fresh full-process requests after an admission decision based only on the original validation split.')
  write(DEP/'protocol.json',p)
 p=read(DEP/'protocol.json');assert sha(DEP/'admission.json')==p['admission_sha256'];assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items())
 old=legacy();refs=old.h.inputs.module('fast_final_reference',HERE/'s08_test.py')
 for i,c in enumerate(p['cases']):
  dest=DEP/'coverage'/(c['id']+'.json')
  if dest.exists():continue
  begin=time.perf_counter();ref=refs.reference(c);ref['preparation_seconds']=time.perf_counter()-begin;assert ref['success'],c['id'];write(DEP/'references'/(c['id']+'.json.gz'),ref);first={}
  for rep in range(3):
   ms=p['methods'];order=ms[(i+rep)%4:]+ms[:(i+rep)%4]
   for m in order:
    if rep and not first[m]['independently_verified']:continue
    r=measure(c,m,rep,ref,'model_test')
    if not rep:first[m]=r
  row=dict(case=c['id'],scope=c['scope'],reference_seconds=ref['preparation_seconds'],verified={m:r['independently_verified'] for m,r in first.items()});write(dest,row);print(json.dumps(row),flush=True)
 write(DEP/'complete.json',dict(complete=True))
if __name__=='__main__':main()
