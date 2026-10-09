"""Select native IBP seeds from public family and target files."""
import argparse,gzip,json,pathlib,time
from s01_fast_seed import FastSeed
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--definition",type=pathlib.Path,required=True)
 ap.add_argument("--masters",type=pathlib.Path,required=True)
 ap.add_argument("--targets",type=pathlib.Path,required=True)
 ap.add_argument("--candidates",type=pathlib.Path,required=True)
 ap.add_argument("--output",type=pathlib.Path,required=True)
 ap.add_argument("--name",default="F");ap.add_argument("--threshold",type=float)
 ap.add_argument("--input-mode",choices=["components","expressions"],default=None)
 ap.add_argument("--halo",action="store_true")
 a=ap.parse_args()
 frozen=json.loads((pathlib.Path(__file__).resolve().parent/"frozen_policy.json").read_text())
 chosen_policy=frozen["selected_seed_policy"]
 if a.threshold is None:a.threshold=0.01 if chosen_policy=="ml_lower" else 0.5
 if a.input_mode is None:a.input_mode="expressions" if chosen_policy=="ml_lower" else "components"
 a.halo=a.halo or chosen_policy=="ml_components_halo"
 assert 0<a.threshold<1
 assert a.name.isidentifier()
 for p in (a.definition,a.masters,a.targets,a.candidates):
  if p.stat().st_size>16000000:raise ValueError("Public input exceeds 16 MB")
 start=time.perf_counter();definition=json.loads(a.definition.read_text());basis=json.loads(a.masters.read_text())
 masters=[tuple(x["indices"]) for x in basis["masters"]];seeds=[tuple(x) for x in json.loads(a.candidates.read_text())["indices"]]
 with (gzip.open if a.targets.suffix==".gz" else open)(a.targets,"rt") as stream:targets=[json.loads(line) for line in stream]
 if len(targets)>4096:raise ValueError("Batch exceeds 4096 target expressions")
 if a.input_mode=="components":
  components=sorted({tuple(t["indices"]) for x in targets for t in x["terms"]}-set(masters))
  targets=[dict(id=a.name+"["+",".join(map(str,c))+"]",terms=[dict(indices=list(c),coefficient="1")]) for c in components]
 model=FastSeed();shared=model.shared(definition,masters,seeds);chosen=set();scores=[]
 for t in targets:
  probabilities=model.predict(t,shared);chosen.update(s for s,p in zip(seeds,probabilities) if p>=a.threshold)
  scores.append(dict(target=t["id"],probabilities=[float(x) for x in probabilities]))
 original=set(chosen)
 if a.halo:chosen.update(b for b in seeds if any(sum(abs(x-y) for x,y in zip(b,c))<=1 for c in original))
 if not chosen:raise ValueError("Empty prediction: use the standard native seed bounds")
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text("".join(a.name+"["+",".join(map(str,s))+"]\n" for s in sorted(chosen)))
 sectors={}
 for s in chosen:
  sector=sum(1<<j for j,v in enumerate(s) if v>0)
  if not sector:continue
  bound=sectors.setdefault(sector,dict(topologies=[a.name],sectors=[sector],r=0,s=0,d=0))
  for key,value in [("r",sum(max(v,0) for v in s)),("s",sum(max(-v,0) for v in s)),("d",sum(max(v-1,0) for v in s))]:
   bound[key]=max(bound[key],value)
 record=dict(input_mode=a.input_mode,threshold=a.threshold,halo=a.halo,candidate_count=len(seeds),
  selected=len(chosen),before_halo=len(original),seconds=time.perf_counter()-start,probabilities=scores,
  reduce=[sectors[k] for k in sorted(sectors)],
  use="Set KIRA_ML_SEEDS to the absolute seed-list path for the patched binary. Use these reduce bounds. Check that every requested integral reduces to the prescribed master basis; expand seeds or use standard Kira if it does not.")
 a.output.with_suffix(a.output.suffix+".json").write_text(json.dumps(record,indent=2)+"\n")
 print(json.dumps({k:record[k] for k in ["input_mode","threshold","candidate_count","selected","seconds"]}))
if __name__=="__main__":main()
