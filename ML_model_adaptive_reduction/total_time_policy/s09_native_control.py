"""Add unadjusted native bounds before fitting or reserved testing."""
from s00_cost_common import *
from s02_collect import measured,get_reference,claim

def main(worker):
 p=READ(HERE/'protocol.json')
 for phase in ['training','validation']:
  for c in p[phase]:
   if not claim(c,'native_control_'+phase,worker):continue
   ref=get_reference(c);records=[]
   for rep in range(p[phase+'_repetitions']):
    r=measured(c,'raw_native',rep,ref,phase);records.append(dict(action='raw_native',rep=rep,verified=r['independently_verified'],seconds=r['complete_process_and_check_seconds'],failed_attempts=r.get('failed_attempts',0)))
   dest=HERE/'coverage'/phase/(c['id']+'.json');row=READ(dest);row['records']+=records;write(dest,row)
   print(json.dumps(dict(phase=phase,case=c['id'],native_control_verified=all(r['verified'] for r in records))),flush=True)
 write(HERE/('native_control_'+str(worker)+'_complete.json'),dict(complete=True))
if __name__=='__main__':main(int(sys.argv[1]))
