"""Run disjoint reserved requests with the original paired timing procedure."""
import argparse,json,socket
from s03_train import reference
from s05_reduce import reduce
from s00_policy import *

def main():
 p=argparse.ArgumentParser();p.add_argument('part',choices=['0','1','2','finish']);a=p.parse_args()
 graph='nonplanar_box';folder=HERE/'model_test'
 paths=['trained_model/cost_'+graph+'.json','s00_policy.py','s05_reduce.py','s16_parallel_test.py','protocols/cost_'+graph+'.json']
 hashes={n:inputs.sha(HERE/n) for n in paths}
 protocol=rt.read(HERE/'protocols'/('cost_'+graph+'.json'))
 if a.part=='finish':
  chunks=[rt.read(folder/(graph+'_part'+str(k)+'_completion.json')) for k in range(3)]
  assert all(c['complete'] and c['hashes']==hashes for c in chunks)
  names=[n for c in chunks for n in c['cases']]
  assert len(names)==len(set(names))==len(protocol['reserved'])
  assert set(names)=={c['id'] for c in protocol['reserved']}
  inputs.write(folder/(graph+'_freeze.json'),dict(hashes=hashes,cases=names,parts=chunks,same_worker_per_case=True,repetitions=7,methods=['native','fixed','learned','previous'],execution='Three disjoint request groups; unchanged candidate list, repeated method order, and exact checks.'))
  inputs.write(folder/(graph+'_completion.json'),dict(complete=True,hashes=hashes,cases=names,parts=3));return
 part=int(a.part);cases=[(i,c) for i,c in enumerate(protocol['reserved']) if i%3==part]
 metadata=dict(hashes=hashes,cases=[c['id'] for i,c in cases],worker=socket.gethostname(),same_worker_per_case=True,repetitions=7,methods=['native','fixed','learned','previous'])
 inputs.write(folder/(graph+'_part'+a.part+'_freeze.json'),metadata)
 for i,c in cases:
  refp,ref=reference(c)
  if not ref['success']:continue
  for rep in range(7):
   methods=['native','fixed','learned','previous'];shift=(i+rep)%4;methods=methods[shift:]+methods[:shift]
   for method in methods:
    out=folder/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
    if out.exists():continue
    r=reduce(c,ref['masters'],method,refp);r.update(repetition=rep,worker=socket.gethostname());save(out,r)
    print(json.dumps(dict(case=c['id'],method=method,repetition=rep,success=r['success'],seconds=r['complete_seconds'],fallbacks=r['fallbacks'])),flush=True)
 for n,h in hashes.items():assert inputs.sha(HERE/n)==h,n
 inputs.write(folder/(graph+'_part'+a.part+'_completion.json'),dict(metadata,complete=True))

if __name__=='__main__':main()
