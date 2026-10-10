"""Compare cold seed backends with identical candidates and decisions."""
import hashlib,json,pathlib,statistics,subprocess,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 cases=[c for c in json.loads((ROOT/"Kira_comparison/integrated_runtime/families.json").read_text())["cases"] if c["split"]=="validation"]
 batches=[(c["id"],min(32,len(c["targets"]))) for c in cases]+[(c["id"],128) for c in cases if not c["id"].endswith("_deep") and len(c["targets"])>=128]
 rows=[]
 for rep in range(3):
  for i,(case,size) in enumerate(batches):
   pair=[]
   for backend in (["numpy","compiled"] if (rep+i)%2==0 else ["compiled","numpy"]):
    begin=time.perf_counter()
    text=subprocess.check_output([sys.executable,str(HERE/"s07_cold_component.py"),backend,case,str(size)],cwd=ROOT,text=True,timeout=120)
    r=json.loads(text);r["process_seconds"]=time.perf_counter()-begin;r["repeat"]=rep;rows.append(r);pair.append(r)
   assert pair[0]["selection_sha256"]==pair[1]["selection_sha256"],(case,size)
 out=[]
 for case,size in batches:
  d=dict(case=case,size=size)
  for backend in ["numpy","compiled"]:
   r=[x for x in rows if (x["case"],x["size"],x["backend"])==(case,size,backend)]
   d[backend+"_median_seconds"]=statistics.median(x["complete_seconds"] for x in r)
  d["compiled_ratio"]=d["compiled_median_seconds"]/d["numpy_median_seconds"];out.append(d)
 result=dict(all_selection_checks_passed=True,repetitions=3,raw=rows,summary=out,compiled_parity_sha256=hashlib.sha256((HERE/"compiled_parity.json").read_bytes()).hexdigest())
 (HERE/"cold_benchmark.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(out),flush=True)
if __name__=="__main__":main()
