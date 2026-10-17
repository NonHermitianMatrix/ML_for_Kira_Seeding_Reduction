"""Compare frozen partition selection with current and fixed controls."""
import json,time
from s00_runtime import HERE,FILTER,rt,inputs,save,reduce
from s01_cases import make,reference

def main():
 f=rt.read(HERE/'trained_model/freeze.json')
 for n,h in f['sources'].items():assert inputs.sha(HERE/n)==h,n
 assert inputs.sha(rt.BINARY)==f['native_sha256']
 assert inputs.sha(HERE/'fixed_inputs.json')==f['filter_source_sha256']
 assert inputs.sha(FILTER/'trained_model/freeze.json')==rt.read(HERE/'fixed_inputs.json')['source_freeze_sha256']
 cases=[c for h in f['test_profiles'] for c in make(h,'reserved')]
 protocol=dict(cases=cases,methods=['previous','off','fixed','fixed_off','learned'],repetitions=f['test_repetitions'],freeze_sha256=inputs.sha(HERE/'trained_model/freeze.json'))
 p=HERE/'model_test/protocol.json'
 if p.exists():assert rt.read(p)==protocol
 else:inputs.write(p,protocol)
 for ci,c in enumerate(cases):
  ref=reference(c)
  if ref is None:print('TEST_REFERENCE_FAILED',c['id'],flush=True);continue
  for j in range(protocol['repetitions']):
   methods=protocol['methods'];offset=(ci+2*j)%len(methods);order=methods[offset:]+methods[:offset]
   for method in order:
    p=HERE/'model_test'/(c['id']+'_'+method+f'_r{j}.json.gz')
    if p.exists():continue
    tick=time.perf_counter();basis=rt.read(ref)['masters'];r=reduce(c,basis,method,ref);r['complete_seconds']=time.perf_counter()-tick;save(p,r)
    print('TEST',c['id'],method,j,r['success'],round(r['complete_seconds'],4),r['action'],flush=True)
 inputs.write(HERE/'model_test/completion.json',dict(complete=True))

if __name__=='__main__':main()
