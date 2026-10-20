"""New triangle examples and disjoint native kinematics and target batches."""
from s00_triangle_common import *
from fractions import Fraction as Q
import random,itertools

def triangle(L,h,targets,phase='development'):
 lm=['k'+str(i+1) for i in range(L)];ps=[]
 for k in lm:
  ps.extend(dict(momentum=v,mass_squared='0') for v in [k,k+'-p1',k+'-p1-p2'])
 # Complete the scalar-product coordinates; cross-loop powers remain zero.
 ps.extend(dict(momentum=lm[i]+'-'+lm[j],mass_squared='0') for i in range(L) for j in range(i+1,L))
 ts=[list(t)+[0]*(len(ps)-3*L) for t in targets]
 return dict(id=f'triangle_{phase}_L{L}_Q{h}',group='triangle_'+str(h),topology_group='one_scale_triangle',split=phase,size=len(ts),targets=ts,definition=dict(name='F',kind='one_scale_triangle',loop_momenta=lm,external_momenta=['p1','p2'],propagators=ps,invariants=[],scalarproduct_rules=[[['p1','p1'],'0'],[['p2','p2'],'0'],[['p1','p2'],str(Q(-h,2))]],physical_propagators=3*L,top_level_sectors=[(1<<(3*L))-1],parameters=dict(Q=h),coefficient_field='Q(d)'))

def triangle_cases(phase):
 rng=random.Random({'development':31001,'reserved':31013}[phase]);out=[]
 for L in ([1,2,3] if phase=='development' else range(1,14)):
  ts=[]
  for j in range(6):
   t=[]
   for k in range(L):t.extend(rng.choice([(1,1,1),(2,1,1),(1,2,1),(1,1,2),(2,2,1),(1,0,1),(2,0,2)]))
   if t not in ts:ts.append(t)
  out.append(triangle(L,31+L if phase=='development' else 101+2*L,ts,phase))
 return out

def native_cases(phase):
 h=helper();canon=prior().previous().current().previous().previous().batch.canonical
 rng=random.Random(31901);blocked=set()
 # Exclude whole target batches from every preceding reconstruction split.
 maker=load('triangle_old_case_maker',PRIOR/'s10_cases.py')
 for split in ['training','validation','reserved']:
  blocked.update(tuple(sorted(map(tuple,c['targets']))) for c in maker.cases(split))
 powers=[(a,b) for a in range(5) for b in range(5-a) if 1<=a+b<=4];pool=[]
 while len(pool)<24:
  ts=tuple(sorted(tuple([1]*7+[-a,-b]) for a,b in rng.sample(powers,rng.choice([2,3,4,5,6]))))
  if ts not in blocked and ts not in pool:pool.append(ts)
 lo,hi={'development':(0,2),'training':(2,14),'validation':(14,19),'reserved':(19,24)}[phase]
 out=[]
 for kind in ['double_box','nonplanar_box']:
  for i in range(lo,hi):
   c=h.inputs.case(kind,31901+i,'rank2',phase);a=137+6*i;b=167+4*i;orient=1 if kind=='double_box' else -1
   scalar={('p1','p1'):Q(0),('p2','p2'):Q(0),('p3','p3'):Q(0),('p1','p2'):Q(-a,2),('p1','p3'):Q(-orient*b,2),('p2','p3'):Q(orient*(a+b),2)}
   c['definition']['scalarproduct_rules']=[[pair,str(scalar[tuple(pair)])] for pair,_ in c['definition']['scalarproduct_rules']]
   params=c['definition']['parameters'];(params if kind=='double_box' else params['values']).update(s=-a,t=-b)
   c.update(id=f'triangle_native_{phase}_{kind}_{i}',targets=list(map(list,pool[i])),size=len(pool[i]),test_group='native')
   out.append(canon(c))
 for kind in ['sunrise','vacuum3']:
  for i in range(lo,hi):
   c=h.inputs.case(kind,32101+i,'dot' if i%2 else 'corner',phase)
   c.update(id=f'triangle_native_{phase}_{kind}_{i}',test_group='native');out.append(canon(c))
 return out
