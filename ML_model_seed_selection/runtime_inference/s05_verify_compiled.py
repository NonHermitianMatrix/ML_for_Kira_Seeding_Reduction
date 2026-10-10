"""Compare compiled neural inference with the unchanged NumPy network."""
import hashlib,json,math,pathlib,sys,time
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];EXP=ROOT/"Kira_comparison/integrated_runtime"
sys.path.insert(0,str(EXP));from s03_records import read_record
from s00_vector_seed import VectorSeed
from s04_compiled_seed import CompiledSeed
from s07_seed import candidates
def main():
 cpp=CompiledSeed();original=VectorSeed();results=[];maximum=0.;different=0
 cases=json.loads((EXP/"families.json").read_text())["cases"]
 for case in cases:
  name=case["id"];targets=case["targets"][:32];n=len(targets);definition=case["definition"]
  reference=ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n{n}.json.gz"
  if not reference.exists():reference=EXP/"references"/f"{name}_n{n}.json.gz"
  masters=read_record(reference)["masters"]
  for margin in [0,1]:
   r=max(sum(max(0,v) for v in a) for a in targets)+margin
   s=max(sum(max(0,-v) for v in a) for a in targets)+margin
   d=max(sum(max(0,v-1) for v in a) for a in targets)+margin
   seeds=candidates(definition,r,s,d)
   begin=time.perf_counter();shared=original.shared(definition,masters,seeds)
   want=original.predict(dict(terms=[dict(indices=a,coefficient="1") for a in targets]),shared)
   old_time=time.perf_counter()-begin;begin=time.perf_counter()
   got=np.asarray(cpp.probabilities(definition,masters,targets,seeds),np.float32);cpp_time=time.perf_counter()-begin
   error=float(np.max(np.abs(got-want)));maximum=max(maximum,error)
   assert np.isfinite(got).all() and np.all((0<=got)&(got<=1))
   assert error<1e-4,(name,margin,error)
   masks={}
   for threshold in ([.003,.01,.03,.1,.3,.5] if "--expanded" in sys.argv else [.01,.5]):
    changes=int(np.count_nonzero((got>=threshold)!=(want>=threshold)));different+=changes;masks[str(threshold)]=changes
   results.append(dict(case=name,margin=margin,candidates=len(seeds),maximum_probability_error=error,threshold_changes=masks,numpy_seconds=old_time,compiled_seconds=cpp_time))
   print(json.dumps(results[-1]),flush=True)
 record=dict(all_passed=different==0,probability_tolerance=1e-4,maximum_probability_error=maximum,threshold_changes=different,cases=results,weights_sha256=hashlib.sha256((HERE/"compiled_weights.bin").read_bytes()).hexdigest(),library_sha256=hashlib.sha256((ROOT/".tools/kira-seed-inference/libseed.so").read_bytes()).hexdigest(),implementation_sha256=hashlib.sha256((HERE/"s02_seed_runtime.cpp").read_bytes()).hexdigest(),scope="Unchanged float32 weights with independently ordered floating-point arithmetic; exact selection parity checked at 0.01 and 0.5 on every listed development candidate.")
 (HERE/("compiled_threshold_parity.json" if "--expanded" in sys.argv else "compiled_parity.json")).write_text(json.dumps(record,indent=2)+"\n")
 assert record["all_passed"],"A threshold decision changed; inspect before integration"
 print(json.dumps({k:v for k,v in record.items() if k!="cases"}),flush=True)
if __name__=="__main__":main()
