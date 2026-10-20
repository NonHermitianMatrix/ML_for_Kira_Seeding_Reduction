"""Check angular reduction against signed IBP and independent native Kira."""
from s00_tensor_common import *
from s03_cases import case
from s01_tensor import reduce

def main():
 old=previous();h=old.batch.legacy().h;measure=load('tensor_native_measure',old.BATCH/'s04_measure.py');records=[]
 for P,e,r,d,mass in [(2,1,1,0,'massive'),(2,2,2,1,'massive'),(3,1,1,1,'massive'),(3,2,2,0,'massive'),(4,1,1,0,'massive'),(2,1,2,1,'massless')]:
  c=case(P,e,7001+P+e,rank=r,dots=d,count=2,mass=mass,seed=41)
  outputs={};times={}
  for a in ACTIONS:
   tick=time.perf_counter();ans=reduce(c,a,deadline=tick+20);times[a]=time.perf_counter()-tick;assert ans is not None,(c['id'],a)
   outputs[a]=ans
  for a in ACTIONS[1:]:assert h.equal(outputs[ACTIONS[0]]['coefficients'],outputs[a]['coefficients'])[0],(c['id'],a)
  native=measure.native(h,c,None,expanded=True);assert native['success'],(c['id'],'native',native)
  ok,n=h.equal(outputs[ACTIONS[0]]['coefficients'],native['coefficients']);assert ok,(c['id'],'native mismatch',outputs[ACTIONS[0]],native)
  record=dict(case=c,times=times,outputs=outputs,native=native,checks=n);write(HERE/'development'/(c['id']+'.json.gz'),record);records.append(dict(case=c['id'],times=times,checks=n,states={a:r['recurrence_states'] for a,r in outputs.items()}));print(json.dumps(records[-1]),flush=True)
 write(HERE/'pilot.json',dict(complete=True,rows=records,checks=sum(r['checks'] for r in records)))
if __name__=='__main__':main()
