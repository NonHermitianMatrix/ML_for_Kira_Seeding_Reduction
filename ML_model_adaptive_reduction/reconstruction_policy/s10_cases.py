"""Separate physical batches and kinematics for algebra-cost learning."""
from s00_reconstruction_common import *
import random,copy
from fractions import Fraction

def cases(phase):
 assert phase in ['training','validation','reserved']
 h=helper();rng=random.Random(26701)
 blocked=set()
 maker=load('reconstruction_old_cases',PREVIOUS/'s03_cases.py')
 for split in ['development','training','validation','reserved']:
  blocked.update(tuple(sorted(map(tuple,c['targets']))) for c in maker.cases(split))
 for c in read(PREVIOUS/'final_protocol.json.gz')['cases']:
  if c.get('test_group')=='native':blocked.add(tuple(sorted(map(tuple,c['targets']))))
 powers=[(a,b) for a in range(5) for b in range(5-a) if 1<=a+b<=4]
 pool=[]
 while len(pool)<26:
  ts=tuple(sorted(tuple([1]*7+[-a,-b]) for a,b in rng.sample(powers,rng.choice([2,3,4,5,6]))))
  if ts not in blocked and ts not in pool:pool.append(ts)
 lo,hi={'training':(0,14),'validation':(14,20),'reserved':(20,26)}[phase]
 out=[]
 for kind in ['double_box','nonplanar_box']:
  for i in range(lo,hi):
   c=h.inputs.case(kind,26713+i,'rank2',phase)
   c.update(id=f'reconstruction_{phase}_{kind}_{i}',targets=list(map(list,pool[i])),size=len(pool[i]),test_group='native')
   # Match both graph classes over small and large rational invariants.
   # Each split has fresh complete batches, not isolated targets from a batch.
   a=[3,13,103,1009,10007,100003][i%6]
   b=[7,19,107,1013,10009,100019][i%6]
   a+=2*(i//6);b+=4*(i//6)
   orientation=1 if kind=='double_box' else -1
   scalar={('p1','p1'):Fraction(0),('p2','p2'):Fraction(0),('p3','p3'):Fraction(0),
    ('p1','p2'):Fraction(-a,2),('p1','p3'):Fraction(-orientation*b,2),
    ('p2','p3'):Fraction(orientation*(a+b),2)}
   c['definition']['scalarproduct_rules']=[[pair,str(scalar[tuple(pair)])] for pair,_ in c['definition']['scalarproduct_rules']]
   if kind=='double_box':c['definition']['parameters'].update(s=-a,t=-b)
   else:c['definition']['parameters']['values'].update(s=-a,t=-b)
   # The physical fourth leg is p1+p2+p3 for the planar routing and
   # p1+p2-p3 for the nonplanar routing. Both are massless.
   assert scalar[('p1','p2')]+orientation*(scalar[('p1','p3')]+scalar[('p2','p3')])==0
   out.append(previous().current().previous().previous().batch.canonical(c))
 profiles={'training':[27701,27713],'validation':[27733],'reserved':[27739]}[phase]
 for kind in ['double_box','nonplanar_box','sunrise','vacuum3']:
  shapes=['corner','numerator','dot'] if kind in ['double_box','nonplanar_box'] else ['corner','dot']
  for profile in profiles:
   for shape in shapes:
    c=h.inputs.case(kind,profile,shape,phase)
    c.update(id=f'reconstruction_{phase}_{kind}_{shape}_{profile}',test_group='native')
    out.append(previous().current().previous().previous().batch.canonical(c))
 return out

def features(c):
 h=helper();x=h.inputs.features(c)
 values=[v for _,v in c['definition']['scalarproduct_rules']]
 values += [p['mass_squared'] for p in c['definition']['propagators']]
 rationals=[]
 for v in values:
  try:rationals.append(Fraction(v))
  except (ValueError,ZeroDivisionError):pass
 return x+[max([abs(v.numerator).bit_length() for v in rationals] or [0]),max([v.denominator.bit_length() for v in rationals] or [0])]
