"""Select only on validation complete costs, then freeze before fresh tests."""
import statistics
from s00_common import *
def main():
 records=[json.loads(p.read_text()) for p in (HERE/"validation/results").glob("*.json")]
 assert len(records)==324 and all(r["success"] and r["fallbacks"]==0 for r in records)
 cases=sorted(set(r["case"] for r in records));keys=sorted(set((r["mode"],r.get("model") or "none") for r in records))
 med={}
 for key in keys:
  med[key]={c:statistics.median(r["complete_seconds"] for r in records if r["case"]==c and (r["mode"],r.get("model") or "none")==key) for c in cases}
 baseline=med["previous","none"]
 ratios={k:math.exp(sum(math.log(v[c]/baseline[c]) for c in cases)/len(cases)) for k,v in med.items()}
 candidates=[k for k in keys if k[0]=="model"];model=min(candidates,key=lambda k:ratios[k])
 controls=[k for k in keys if k[0] in ["extreme","first","sum_ascending","sum_descending"]]
 control=min(controls,key=lambda k:ratios[k])
 deploy=model if ratios[model]<.98*ratios[control] else control
 result=dict(mode=deploy[0],model=model[1],control=control[0],selected_model=model[1],model_vs_control=ratios[model]/ratios[control],rule="Require at least 2 percent lower validation complete time to deploy the newly trained model.",validation_ratios={"/".join(k):v for k,v in ratios.items()},validation_workflows=len(records))
 packed=[json.loads(p.read_text()) for p in (HERE/"validation/pack_results").glob("*.json") if "_part" not in p.name]
 if packed:
  assert len(packed)==48 and all(x["success"] and x["fallbacks"]==0 for x in packed)
  groups=sorted(set(x["input"] for x in packed))
  v={mode:{g:statistics.median(x["complete_seconds"] for x in packed if x["input"]==g and x["mode"]==mode and x["packed"]) for g in groups} for mode in ["model",control[0]]}
  ratio=math.exp(sum(math.log(v["model"][g]/v[control[0]][g]) for g in groups)/len(groups))
  result.update(packed_mode="model" if ratio<.98 else control[0],packed_model_vs_control=ratio,packed_validation_workflows=len(packed))
 else:result["packed_mode"]=result["mode"]
 write(HERE/"trained_model/deployment.json",result)
 paths=list(HERE.glob("s0[0-9]_*.py"))+[HERE/"s11_pack.py",HERE/"s12_pack_study.py"]+[HERE/"s04_run.sh"]+list((HERE/"trained_model").glob("forest*"))+[HERE/"trained_model/deployment.json"]+list((HERE/"model_test/inputs").glob("*.json"))
 paths += [OLD/"trained_model/depth4.json",OLD/"s00_math.py",OLD/"s02_reduce.py",OLD/"s10_polynomial.py",ROOT/".tools/kira-early-generation/kira"]
 write(HERE/"trained_model/freeze.json",dict(sha256={str(p.relative_to(ROOT)):sha(p) for p in paths},reserved_cases=len(cases),created_before_tests=True))
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
