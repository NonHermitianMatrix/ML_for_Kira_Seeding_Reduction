"""Check bounded sector storage with complete reductions and independent bases."""
from s00_common import *
import statistics,contextlib
BIN=ROOT/'.tools/kira-sector-storage/kira'
def attempt(c,basis=None,check=False,optimized=True,reference=None):
 begin=time.perf_counter();b=inputs.bounds(c,'expanded')
 if check:b[1]+=1
 with rt.environment():
  os.environ['KIRA_RUNTIME_BINARY']=str(BIN)
  if optimized:os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
  r=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=60,margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=b,ordering=2 if check else 1,threads=1)
  if reference:rt.verify(r,reference)
 r=rt.compact(r);r.update(optimized=optimized,complete_seconds=time.perf_counter()-begin);return r

def main():
 assert read(HERE/'integration/build.json')['complete'];assert inputs.sha(BIN)==read(HERE/'integration/build.json')['binary_sha256']
 gen=module('sector_physics',ROOT/'Kira_comparison/coverage_study/s00_cases.py')
 cases=[gen.case(k,l,False,1131) for k in ['vacuum_one_mass','vacuum_all_mass','propagator_massless','propagator_massive'] for l in ([5,6,7] if k.startswith('vacuum') else [5,6])]
 cases.extend(gen.case(k,5,False,1131) for k in ['ladder','bubble_box'])
 # Low-loop coefficient controls use unrelated parameter profiles.
 cases.extend(gen.case(k,l,False,1132) for k,l in [('vacuum_one_mass',3),('vacuum_all_mass',3),('propagator_massive',2),('ladder',2)])
 cases=cases[-4:]+cases[:-4]
 write(HERE/'integration/protocol.json',dict(cases=cases,binary_sha256=inputs.sha(BIN),repetitions=3,seconds_per_attempt=60,methods=['native_allocation','bounded_allocation'],independent_check='One more numerator power and ordering two. Same supplied basis.'))
 for c in cases:
  marker=HERE/'integration/results'/(c['id']+'.json')
  if marker.exists():continue
  ref=HERE/'integration/references'/(c['id']+'.json.gz');r=attempt(c);write(ref,r)
  if not r['success']:write(marker,dict(case=c['id'],status='new_reference_failed',reason=r.get('status')));print(c['id'],'reference failed',flush=True);continue
  check=attempt(c,r['masters'],True,True,ref);write(ref.with_name(ref.stem+'_check.json.gz'),check)
  if not check['success']:write(marker,dict(case=c['id'],status='new_check_failed',reason=check.get('status')));continue
  methods={False:[],True:[]};failed=set()
  for rep in range(3):
   for opt in ([False,True] if rep%2==0 else [True,False]):
    if opt in failed:continue
    r=attempt(c,read(ref)['masters'],False,opt,ref);write(HERE/'integration/model_test'/(c['id']+'_'+str(int(opt))+'_'+str(rep)+'.json.gz'),r)
    methods[opt].append(r['complete_seconds'])
    if not r['success']:failed.add(opt)
  write(marker,dict(case=c['id'],status='verified' if not failed else 'control_failed',failed_methods=list(failed),times={str(k):v for k,v in methods.items()},loops=len(c['definition']['loop_momenta']),indices=len(c['definition']['propagators'])))
  print(c['id'], 'complete',failed,flush=True)
 write(HERE/'integration/completion.json',dict(complete=True,cases=len(cases)))
if __name__=='__main__':main()
