"""Choose policies on validation measurements and freeze before reserved tests."""
import hashlib,math,statistics
from s00_math import *
def key(r):return r["mode"]+":"+str(r["model"])
def main():
 records=[json.loads(p.read_text()) for p in (HERE/"validation/results").glob("*.json")]
 assert len(records)==6*8*3 and all(r["success"] for r in records)
 groups={}
 for r in records:groups.setdefault((r["case"],key(r)),[]).append(r["external_seconds"])
 assert all(len(v)==3 for v in groups.values())
 med={k:statistics.median(v) for k,v in groups.items()};cases=sorted({r["case"] for r in records})
 methods=sorted({key(r) for r in records})
 scores={m:math.exp(sum(math.log(med[c,m]/med[c,"dense:None"]) for c in cases)/len(cases)) for m in methods}
 best_model=min((m for m in methods if m.startswith("learned:")),key=scores.get).split(":")[1]
 control=min((m for m in methods if m.split(":")[0] not in ("dense","learned")),key=scores.get).split(":")[0]
 learned=scores["learned:"+best_model];rule=scores[control+":None"]
 deployed="learned" if learned<.98*rule else control
 policy=dict(model=best_model,control=control,deployed_mode=deployed,selection="Three-repeat median external complete costs, geometric mean across six validation batches; use learned route only if at least 2 percent below the best simple control.",validation_ratios_to_dense=scores,learned_over_control=learned/rule,shared_loop_variable="z=L*(d-2)")
 write(HERE/"trained_model/deployment.json",policy)
 paths=[HERE/n for n in ["s00_math.py","s01_train.py","s02_reduce.py","s03_cases.py","s04_study.py","s06_select.py","s08_application.py","s10_polynomial.py","s14_extrapolate.py"]]+list((HERE/"trained_model").glob("*.json"))+list((HERE/"model_test/inputs").glob("*.json"))+[ROOT/".tools/kira-early-generation/kira"]
 paths=[p for p in paths if p.name!="freeze.json"]
 write(HERE/"trained_model/freeze.json",dict(sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},test_repetitions=3,frozen_before_test=True))
 print(json.dumps(policy,indent=2))
if __name__=="__main__":main()
