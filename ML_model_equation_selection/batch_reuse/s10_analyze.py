"""Fresh-case complete times and independent exact audits of saved reductions."""
import gzip,statistics
from s00_common import *
def object_read(h):
 raw=gzip.decompress((HERE/"objects"/(h+".json.gz")).read_bytes());assert hashlib.sha256(raw).hexdigest()==h
 return json.loads(raw)
def interval(values):
 logs=[math.log(v) for v in values];rng=random.Random(19421)
 boot=sorted(math.exp(sum(rng.choice(logs) for _ in logs)/len(logs)) for i in range(4000))
 return dict(ratio=math.exp(sum(logs)/len(logs)),interval=[boot[100],boot[3899]])
def main():
 policy=json.loads((HERE/"trained_model/deployment.json").read_text())
 for n,h in json.loads((HERE/"trained_model/freeze.json").read_text())["sha256"].items():assert sha(ROOT/n)==h,n
 records=[json.loads(p.read_text()) for p in (HERE/"model_test/results").glob("*.json")]
 expected=json.loads((HERE/"model_test/test_complete.json").read_text())["workflows"]
 assert len(records)==expected and all(x["success"] and x["fallbacks"]==0 for x in records)
 cases={json.loads(p.read_text())["id"]:json.loads(p.read_text()) for p in (HERE/"model_test/inputs").glob("*.json")}
 checks=0;objects=set();coeff_objects=set();maxrss=0;maxdisk=0
 for x in records:
  c=cases[x["case"]]
  if "payload_sha256" in x:
   payload=object_read(x["payload_sha256"]);objects.add(x["payload_sha256"])
   cp=x["coefficients_sha256"]
   if cp not in coeff_objects:
    coeff_objects.add(cp);data=object_read(cp);symbolic=decode(data["symbolic_coefficients"])
    for L,encoded in data["coefficients"].items():
     coeff=decode(encoded)
     for b,row,z in zip(c["targets"],coeff,symbolic):
      want=old.oracle(int(L),c["mass_ratios"],b)
      assert row==want
      assert row=={j:canonical(old.poly_substitute(p,int(L))) for j,p in z.items()}
      checks+=len(row)
   a=x["algebra"]
  else:
   assert x["mode"]=="previous"
   a=x["attempts"][0]["algebra"]
  maxrss=max(maxrss,a["peak_tree_rss_bytes"]);maxdisk=max(maxdisk,a["peak_scratch_bytes"])
 methods=sorted(set(x["mode"] for x in records));med={}
 for m in methods:
  med[m]={c:{field:statistics.median(
    (x["attempts"][0]["algebra"]["seconds"] if m=="previous" else x["algebra"]["seconds"]) if field=="kira_seconds" else x[field]
    for x in records if x["mode"]==m and x["case"]==c)
   for field in ["complete_seconds","external_seconds","kira_seconds"]} for c in cases}
 comparisons={}
 for m,control in [("model","previous"),("model",policy["control"]),("model","extreme"),("model","exhaustive"),("old_model","previous"),(policy["mode"],"previous")]:
  key=m+"_vs_"+control
  comparisons[key]={field:interval([med[m][c][field]/med[control][c][field] for c in cases]) for field in ["complete_seconds","external_seconds","kira_seconds"]}
 costs={}
 for m in methods:
  if m=="previous":continue
  costs[m]={c:dict(equations=next(x["equations"] for x in records if x["case"]==c and x["mode"]==m),weighted_cost=next(x["weighted_cost"] for x in records if x["case"]==c and x["mode"]==m)) for c in cases}
 regret=[costs["model"][c]["weighted_cost"]/costs["exhaustive"][c]["weighted_cost"] for c in cases]
 result=dict(all_exact=True,workflows=len(records),batches=len(cases),repetitions=5,methods=methods,deployment=policy,comparisons=comparisons,case_medians=med,equation_costs=costs,model_cost_regret=dict(mean=statistics.mean(regret),maximum=max(regret),reference="minimum weighted count within all fixed mass permutations"),unique_coefficient_objects=len(coeff_objects),independent_loop_coefficient_checks=checks,peak_kira_tree_rss_bytes=maxrss,peak_kira_scratch_bytes=maxdisk)
 write(HERE/"model_test/summary.json",result)
 print(json.dumps({k:result[k] for k in ["all_exact","workflows","comparisons","model_cost_regret","independent_loop_coefficient_checks"]},indent=2))
if __name__=="__main__":main()
