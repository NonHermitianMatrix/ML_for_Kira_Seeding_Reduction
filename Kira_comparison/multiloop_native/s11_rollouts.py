"""Measure downstream algebraic work after one alternative native source choice."""
import json,pathlib,sys
from s02_run import run
from s04_records import read_record,write_record
HERE=pathlib.Path(__file__).resolve().parent
def main(index):
 paths=sorted((HERE/"training").glob("*.json.gz"));source=read_record(paths[index])
 cases=json.loads((HERE/"families.json").read_text())["cases"];case=next(c for c in cases if c["id"]==source["case"])
 assert case["split"] in ("training","validation")
 groups=[g for g in source["choices"] if len(g["candidates"])>=3]
 if not groups:groups=source["choices"]
 # Fixed evenly spaced checkpoints; no selection by measured outcome.
 selected=[groups[i] for i in sorted({round(k*(len(groups)-1)/3) for k in range(4)})]
 root=HERE/"rollouts";root.mkdir(exist_ok=True)
 ref=HERE/"references"/(case["id"]+f'_n{source["size"]}.json.gz')
 summary=[]
 for g in selected:
  trials=[]
  for q in range(len(g["candidates"])):
   output=root/(case["id"]+f'_g{g["group"]}_q{q}.json.gz')
   if output.exists():r=read_record(output)
   else:r=run(case,source["size"],"forced",output,timeout=180,margin=1,reference=ref,force=(g["group"],q))
   entries=[x for x in r.get("choices",[]) if x["group"]==g["group"]]
   same=bool(r["success"] and len(entries)==1 and entries[0]["pivot"]==g["pivot"] and
      len(entries[0]["candidates"])==len(g["candidates"]) and
      all(max(abs(a-b) for a,b in zip(x["features"],y["features"]))<1e-12
          for x,y in zip(entries[0]["candidates"],g["candidates"])))
   trial=dict(source=q,path=str(output.relative_to(HERE)),valid=same)
   if same:
    trial["remaining_operations"]=sum(m["operations"] for m in r["metrics"])-entries[0]["prefix_operations"]
    trial["seconds"]=r["complete_seconds"]
   trials.append(trial)
   print(json.dumps(dict(case=case["id"],group=g["group"],**trial)),flush=True)
  summary.append(dict(group=g["group"],pivot=g["pivot"],candidates=g["candidates"],trials=trials))
 out=root/(case["id"]+"_summary.json.gz")
 if not out.exists():write_record(out,dict(case=case["id"],split=case["split"],groups=summary))
if __name__=="__main__":main(int(sys.argv[1]))
