"""Audit exact test exports and summarize the frozen paired costs."""
import gzip,hashlib,math,random,statistics
from s00_math import *
from s02_reduce import parse as parse_export
from s10_polynomial import parse as read_coefficient
def method(r):
 if r["mode"]=="dense":return "shared_dense" if r["shared"] else "separate_dense"
 if r["mode"]=="learned":return "shared_learned" if r["shared"] else "separate_learned"
 return "shared_control"
def ratio(values):
 log=[math.log(v) for v in values];rng=random.Random(2718)
 samples=sorted(math.exp(sum(rng.choices(log,k=len(log)))/len(log)) for _ in range(5000))
 return dict(ratio=math.exp(sum(log)/len(log)),interval=[samples[124],samples[4874]],case_ratios=values)
def main():
 freeze=json.loads((HERE/"trained_model/freeze.json").read_text())
 for n,h in freeze["sha256"].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
 records=[json.loads(p.read_text()) for p in (HERE/"model_test/results").glob("*.json")]
 assert len(records)==90 and all(r["success"] for r in records)
 extra=[json.loads(p.read_text()) for p in (HERE/"model_test/extrapolation").glob("extra_test_r*.json") if not p.name.endswith("_input.json")]
 assert len(extra)==6 and all(r["success"] for r in extra)
 requests={p.stem:json.loads(p.read_text()) for p in (HERE/"model_test/inputs").glob("*.json")}
 checks=0;peak=0;disk=0;calls=0;coeffs=set()
 for r in records+extra:
  base=r["case"].removeprefix("extra_");c=requests[base];R=len(c["mass_ratios"])
  for a in r["attempts"]:
   if "payload_sha256" not in a:continue
   h=a["payload_sha256"];p=HERE/"objects"/(h+".json.gz");raw=gzip.decompress(p.read_bytes());assert hashlib.sha256(raw).hexdigest()==h
   obj=json.loads(raw);rows=parse_export(obj["raw_export"]);L=a["loop"];loops=r["loops"] if L is None else [L];calls+=1
   peak=max(peak,a["algebra"]["peak_tree_rss_bytes"]);disk=max(disk,a["algebra"]["peak_scratch_bytes"])
   for i,b in enumerate(c["targets"]):
    row=rows[a["target_start"]+i];assert all(j<R for j in row)
    polys={j:read_coefficient(s,"z" if L is None else "d") for j,s in row.items()}
    for loop in loops:
     want=oracle(loop,c["mass_ratios"],tuple(b))
     for j in range(R):
      got=canonical(poly_substitute(polys.get(j,()),loop) if L is None else polys.get(j,()))
      assert got==canonical(want.get(j,())),(r["case"],loop,b,j)
      coeffs.add((base,loop,tuple(b),j));checks+=1
 groups={}
 for r in records:groups.setdefault((r["case"],method(r)),[]).append(r)
 assert all(len(v)==3 for v in groups.values())
 med={}
 for (c,m),rows in groups.items():
  med.setdefault(c,{})[m]={k:statistics.median(v[k] for v in rows) for k in ["external_seconds","complete_seconds","verification_seconds","substitution_seconds"]}
  for key,f in [
   ("kira_seconds",lambda v:sum(a.get("algebra",{}).get("seconds",0) for a in v["attempts"])),
   ("preparation_seconds",lambda v:sum(a.get("preparation_seconds",0) for a in v["attempts"])),
   ("selection_seconds",lambda v:sum(a.get("selection_seconds",0) for a in v["attempts"])),
   ("equations",lambda v:sum(a.get("equations",0) for a in v["attempts"])),
   ("solver_calls",lambda v:len(v["attempts"]))]:
   med[c][m][key]=statistics.median(f(v) for v in rows)
 comparisons={}
 for a,b in [("shared_learned","separate_dense"),("shared_learned","shared_dense"),("shared_learned","shared_control"),("separate_learned","separate_dense"),("shared_control","separate_dense"),("shared_dense","separate_dense")]:
  comparisons[a+"_over_"+b]={k:ratio([med[c][a][k]/med[c][b][k] for c in sorted(med)]) for k in ["external_seconds","complete_seconds","kira_seconds","equations"]}
 perloop={}
 for L in range(1,13):
  percase=[]
  for c in sorted(med):
   vals={}
   for m in ["separate_dense","separate_learned"]:
    vals[m]=statistics.median(next(a["solver_complete_seconds"] for a in r["attempts"] if a.get("loop")==L) for r in groups[c,m])
   percase.append(vals["separate_learned"]/vals["separate_dense"])
  perloop[str(L)]=ratio(percase)
 summary=dict(all_exact=True,workflows=len(records),extra_applications=len(extra),kira_calls=calls,coefficient_checks=checks,distinct_coefficient_positions=len(coeffs),peak_kira_tree_rss_bytes=peak,peak_scratch_bytes=disk,comparisons=comparisons,batch_medians=med,per_loop_solver_ratios=perloop,attempt_failures=sum("failure" in a for r in records+extra for a in r["attempts"]),fallbacks=sum(r["fallbacks"] for r in records+extra),scope="Restricted coupled vacuum scalar family; generated Euler and partial-fraction identities supplied to Kira.",primary_time="External complete worker time including startup and evidence writing.",internal_time="Input, model, equation generation, exact Kira, output reading, substitution, independent verification and fallback; excludes evidence serialization and interpreter startup.")
 write(HERE/"model_test/summary.json",summary)
 write(HERE/"model_test/verification.json",dict(all_passed=True,workflows=96,kira_calls=calls,coefficient_checks=checks,distinct_coefficient_positions=len(coeffs),runtime_hashes_match=True,all_payload_hashes_match=True))
 print(json.dumps({k:summary[k] for k in ["workflows","extra_applications","coefficient_checks","peak_kira_tree_rss_bytes","fallbacks","comparisons"]},indent=2),flush=True)
if __name__=="__main__":main()
