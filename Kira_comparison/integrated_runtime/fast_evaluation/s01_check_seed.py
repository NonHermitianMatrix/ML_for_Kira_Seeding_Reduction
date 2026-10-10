"""Check bitwise probabilities and masks against the preceding compiled network."""
import array,hashlib,json,os,pathlib,statistics,sys,time
HERE=pathlib.Path(__file__).resolve().parent;EXP=HERE.parent;ROOT=EXP.parents[1]
sys.path.insert(0,str(EXP));sys.path.insert(0,str(ROOT/"ML_model_seed_selection/runtime_inference"))
from s03_records import read_record
from s04_compiled_seed import CompiledSeed as Old
from s12_shared_seed import CompiledSeed as New
from s07_seed import candidates
def main():
 os.environ["KIRA_FAST_EVAL"]="1";old=Old();new=New();results=[]
 cases=json.loads((EXP/"families.json").read_text())["cases"]
 for case in cases:
  name=case["id"];n=min(32,len(case["targets"]));targets=case["targets"][:n]
  ref=ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n{n}.json.gz"
  if not ref.exists():ref=EXP/"references"/f"{name}_n{n}.json.gz"
  masters=read_record(ref)["masters"];definition=case["definition"]
  for margin in [0,1]:
   r=max(sum(max(0,v) for v in a) for a in targets)+margin
   s=max(sum(max(0,-v) for v in a) for a in targets)+margin
   d=max(sum(max(0,v-1) for v in a) for a in targets)+margin
   seeds=candidates(definition,r,s,d);times={0:[],1:[]};prob={}
   for rep in range(3):
    for flag in ([0,1] if rep%2==0 else [1,0]):
     start=time.perf_counter();p=(new if flag else old).probabilities(definition,masters,targets,seeds)
     times[flag].append(time.perf_counter()-start);prob[flag]=p
   a,b=prob[0],prob[1];error=max(abs(x-y) for x,y in zip(a,b));assert a==b,(name,margin,error)
   masks={str(t):sum((x>=t)!=(y>=t) for x,y in zip(a,b)) for t in [.003,.01,.03,.1,.3,.5]}
   result=dict(case=name,margin=margin,candidates=len(seeds),targets=n,maximum_probability_difference=error,bitwise_equal=array.array("f",a).tobytes()==array.array("f",b).tobytes(),threshold_changes=masks,old_seconds=statistics.median(times[0]),new_seconds=statistics.median(times[1]))
   results.append(result);print(json.dumps(result),flush=True)
 data=dict(all_passed=True,contexts=len(results),maximum_probability_difference=max(r["maximum_probability_difference"] for r in results),results=results,
  weights_sha256=hashlib.sha256((ROOT/"ML_model_seed_selection/runtime_inference/compiled_weights.bin").read_bytes()).hexdigest(),
  new_library_sha256=hashlib.sha256((ROOT/".tools/kira-shared-inference/libseed.so").read_bytes()).hexdigest())
 (HERE/"seed_parity.json").write_text(json.dumps(data,indent=2)+"\n")
if __name__=="__main__":main()
