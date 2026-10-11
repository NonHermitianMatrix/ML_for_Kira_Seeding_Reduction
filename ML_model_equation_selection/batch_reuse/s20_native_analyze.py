"""Audit native-backend confirmation and compare full applications."""
import statistics,subprocess
from s00_common import *
from s10_analyze import object_read,interval
from s10_polynomial import parse as independent_reader
import importlib.util
sp=importlib.util.spec_from_file_location("earlier_driver",OLD/"s02_reduce.py");previous=importlib.util.module_from_spec(sp);sp.loader.exec_module(previous)
def main():
 subprocess.run([sys.executable,str(HERE/"s24_native_application_check.py")],check=True)
 stage=HERE/"model_test"
 rows=[json.loads(p.read_text()) for p in (stage/"native_results").glob("*.json") if "_part" not in p.name]
 assert len(rows)==80 and all(x["success"] and x["fallbacks"]==0 for x in rows)
 policy=json.loads((HERE/"trained_model/native_deployment.json").read_text())
 groups=sorted(set(x["input"] for x in rows));med={}
 for backend in ["previous","control","python","native"]:
  med[backend]={g:{f:statistics.median(x["algebra"]["seconds"] if f=="kira_seconds" else x[f] for x in rows if x["input"]==g and x["backend"]==backend) for f in ["complete_seconds","external_seconds","kira_seconds"]} for g in groups}
 comparisons={}
 for a,b in [("native","previous"),("native","control"),("native","python"),("python","control"),(policy["backend"],"previous")]:
  comparisons[a+"_vs_"+b]={f:interval([med[a][g][f]/med[b][g][f] for g in groups]) for f in ["complete_seconds","external_seconds","kira_seconds"]}
 coefficients=set();payloads=set();checks=0;raw_checks=0;cache={}
 for x in rows:
  if x["backend"]=="previous":continue
  c=object_read(x["coefficients_sha256"]);p=object_read(x["payload_sha256"])
  requests=json.loads((HERE/x["input"]).read_text())["requests"]
  if x["coefficients_sha256"] not in coefficients:
   coefficients.add(x["coefficients_sha256"])
   for request in requests:
    for L,encoded in c["coefficients"][request["id"]].items():
     for b,row in zip(request["targets"],decode(encoded)):
      assert row==old.oracle(int(L),request["mass_ratios"],b);checks+=len(row)
  if x["payload_sha256"] not in payloads:
   payloads.add(x["payload_sha256"]);parsed=previous.parse(p["raw_export"])
   assert len(parsed)==sum(len(v["targets"]) for v in requests)
   rawrows=iter(v for k,v in sorted(parsed.items()));offset=0
   for request in requests:
    for wanted in decode(c["symbolic_coefficients"][request["id"]]):
     row=next(rawrows);got={}
     for j,text in row.items():
      if text not in cache:cache[text]=canonical(independent_reader(text,"z"))
      got[j-offset]=cache[text];raw_checks+=1
     assert got==wanted
    offset+=len(request["mass_ratios"])
 for g in groups:
  a={x["source_sha256"] for x in rows if x["input"]==g and x["backend"]=="python"}
  b={x["source_sha256"] for x in rows if x["input"]==g and x["backend"]=="native"}
  assert len(a)==1 and a==b,"Compiled choices changed the equation system"
 result=dict(all_exact=True,workflows=len(rows),kira_calls=120,groups=len(groups),families=12,loops=list(range(1,13)),repetitions=5,comparisons=comparisons,case_medians=med,deployment=policy,independent_loop_coefficient_checks=checks,independent_raw_coefficient_checks=raw_checks,distinct_raw_coefficients=len(cache),compiled_sources_identical=True,peak_kira_tree_rss_bytes=max(x["algebra"]["peak_tree_rss_bytes"] for x in rows),peak_kira_scratch_bytes=max(x["algebra"]["peak_scratch_bytes"] for x in rows))
 write(stage/"native_summary.json",result)
 print(json.dumps({k:result[k] for k in ["all_exact","comparisons","independent_loop_coefficient_checks","independent_raw_coefficient_checks"]},indent=2))
if __name__=="__main__":main()
