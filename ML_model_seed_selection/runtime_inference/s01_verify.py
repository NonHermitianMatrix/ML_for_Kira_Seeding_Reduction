"""Check bitwise feature, embedding, probability and seed-decision parity."""
import hashlib,json,pathlib,random,sys,time
import numpy as np
from s00_vector_seed import VectorSeed,index_batch,ROOT
from s21_seed_loader import NativeSeed
from s01_fast_seed import index_features
from s07_seed import candidates
from s04_records import read_record
HERE=pathlib.Path(__file__).resolve().parent
def main():
 new=VectorSeed();old=NativeSeed();cfg=new.cfg;rng=random.Random(17019);features_checked=0
 for n in sorted({1,5,6,9,cfg["max_indices"]}):
  rows=[[rng.randint(-4,5) for _ in range(n)] for _ in range(1000)]
  want=np.asarray([index_features(a,cfg) for a in rows],np.float32)
  got=index_batch(rows,cfg);assert np.array_equal(got,want),(n,np.max(np.abs(got-want)))
  features_checked+=len(rows)
 manifest=json.loads((ROOT/"Kira_comparison/multiloop_native/families.json").read_text())
 outcomes=[]
 for case in manifest["cases"]:
  if case["split"]=="reserved":continue
  size=min(32,len(case["targets"]));targets=case["targets"][:size]
  ref=read_record(ROOT/"Kira_comparison/multiloop_native/references"/f'{case["id"]}_n{size}.json.gz')
  definition=case["definition"]
  r=max(sum(max(0,x) for x in a) for a in targets)
  s=max(sum(max(0,-x) for x in a) for a in targets)
  d=max(sum(max(0,x-1) for x in a) for a in targets)
  seeds=candidates(definition,r,s,d);target=dict(terms=[dict(indices=a,coefficient="1") for a in targets])
  times=[];answers=[]
  for model in [old,new]:
   begin=time.perf_counter();shared=model.shared(definition,ref["masters"],seeds);prob=model.predict(target,shared)
   times.append(time.perf_counter()-begin);answers.append((shared,prob))
  assert all(np.array_equal(a,b) for a,b in zip(answers[0][0],answers[1][0])),case["id"]
  assert np.array_equal(answers[0][1],answers[1][1]),case["id"]
  outcomes.append(dict(case=case["id"],candidates=len(seeds),legacy_seconds=times[0],vector_seconds=times[1],probabilities_identical=True,threshold_decisions_identical=True))
 result=dict(all_passed=True,index_vectors_checked=features_checked,cases=outcomes,
  source_sha256=hashlib.sha256((HERE/"s00_vector_seed.py").read_bytes()).hexdigest(),
  timing_scope="single parity passes; complete paired production timings remain required")
 (HERE/"parity.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result),flush=True)
if __name__=="__main__":main()
