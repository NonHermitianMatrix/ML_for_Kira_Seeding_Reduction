"""Check seed-bound candidates on development targets before freezing the study."""
import json,time
from s00_inputs import *
import s01_runtime as rt

def reference(c,check=True):
 p=HERE/'references'/(c['id']+'.json.gz')
 if not p.exists():
  r=rt.attempt(c,action='expanded',timeout=120);rt.save(p,rt.compact(r));print(json.dumps(dict(stage='reference',case=c['id'],success=r['success'],seconds=r['complete_seconds'])),flush=True)
 r=rt.read(p)
 if not r['success']:return None
 q=HERE/'references'/(c['id']+'_check.json.gz')
 if check and not q.exists():
  b=bounds(c,'expanded');b[1]+=1;z=rt.attempt(c,r['masters'],custom=b,timeout=120);rt.verify(z,p);rt.save(q,rt.compact(z));print(json.dumps(dict(stage='reference_check',case=c['id'],success=z['success'],seconds=z['complete_seconds'])),flush=True)
 if check and not rt.read(q)['success']:return None
 return p

def main():
 pairs=[('ladder3','dots'),('double_box','mixed'),('vacuum3','dots'),('sunrise','mixed'),('bubble_box3','dot'),('massless4','numerator'),('double_box','rank4'),('pentagon','rank4'),('nonplanar_box','rank3')]
 cases=[case(g,501,s,'development') for g,s in pairs]
 write(HERE/'development/protocol.json',dict(cases=cases,actions=ACTIONS,binary=sha(rt.BINARY),scope='Development only; no reserved results enter decisions.'))
 for c in cases:
  ref=reference(c)
  if ref is None:continue
  basis=rt.read(ref)['masters']
  for a in ACTIONS:
   p=HERE/'development'/(c['id']+'_'+a+'.json.gz')
   if p.exists():continue
   r=rt.run(c,basis,first=a,reference=ref);rt.save(p,r)
   print(json.dumps(dict(stage='development',case=c['id'],action=a,success=r['success'],seconds=r['complete_seconds'],fallbacks=r['fallbacks'],equations=sum(sum(x.get('counters',{}).get('generated_equations',[])) for x in r['attempts']))),flush=True)
 write(HERE/'development/completion.json',dict(complete=True))
if __name__=='__main__':main()
