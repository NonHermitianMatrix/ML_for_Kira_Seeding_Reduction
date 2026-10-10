"""Measure a fresh-process seed decision, including imports and model loading."""
import argparse,hashlib,json,pathlib,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("backend");ap.add_argument("case");ap.add_argument("size",type=int);a=ap.parse_args()
 begin=time.perf_counter()
 exp=ROOT/"Kira_comparison/integrated_runtime";sys.path.insert(0,str(exp))
 from s03_records import read_record
 case=next(c for c in json.loads((exp/"families.json").read_text())["cases"] if c["id"]==a.case)
 targets=case["targets"][:a.size];assert len(targets)==a.size
 ref=ROOT/"Kira_comparison/multiloop_native/references"/f"{a.case}_n{a.size}.json.gz"
 if not ref.exists():ref=exp/"references"/f"{a.case}_n{a.size}.json.gz"
 masters=read_record(ref)["masters"]
 if a.backend=="compiled":
  from s04_compiled_seed import choose
 else:
  from s00_vector_seed import VectorSeed
  import s07_seed as original;original.FastSeed=VectorSeed;choose=original.choose
 spec=dict(r=max(sum(max(0,v) for v in x) for x in targets),s=max(sum(max(0,-v) for v in x) for x in targets),d=max(sum(max(0,v-1) for v in x) for x in targets))
 selected,predictions,parts=choose(case["definition"],masters,targets,spec,closure=True,threshold=.01)
 result=dict(case=a.case,size=a.size,backend=a.backend,complete_seconds=time.perf_counter()-begin,selected=len(selected),candidates=parts["candidates"],selection_sha256=hashlib.sha256(predictions["selection_bits_base64"].encode()).hexdigest(),parts=parts)
 print(json.dumps(result))
if __name__=="__main__":main()
