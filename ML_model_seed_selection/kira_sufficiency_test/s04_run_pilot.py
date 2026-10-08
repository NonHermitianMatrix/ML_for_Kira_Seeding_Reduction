"""Run bounded mathematical checks and representative held-out Kira reductions."""
import collections,gzip,json,shutil,time,traceback
from s03_kira_adapter import *
from s08_verify import check_records
def arithmetic_checks():
 import sympy as sp
 examples=[
 ("(d**2-9)/(d-3)","d+3",True),("1/(m2+1)+1/(m2-1)","2*m2/(m2**2-1)",True),
 ("(d-2)*(d-4)/(4*m2**2)","(d**2-6*d+8)/(4*m2**2)",True),
 ("(d-3)/(2*m2)","(3-d)/(2*m2)",False),("m2**(-2)","1/m2**2",True),
 ("(s+t)**3","s**3+3*s**2*t+3*s*t**2+t**3",True),
 ("(d-d)/(m2+2)","0",True)]
 for a,b,expected in examples:
  assert exact_equal(a,b)==expected
  assert (sp.cancel(sp.sympify(a)-sp.sympify(b))==0)==expected
 fixtures=read(HERE/"fixture_runs.json")
 assert len(fixtures)==3 and all(x["returncode"]==0 for x in fixtures)
 for name in ["sufficient","insufficient","disjoint"]:
  p=WORK/("fixture_"+name)/"results/Tuserweight/kira_targets.kira";out=parse_output(p)
  if name=="sufficient":assert exact_equal(out[2][0],"(3-d)/(2*m2)")
  if name=="insufficient":assert out[2]=={1:"(1)"}
  if name=="disjoint":assert exact_equal(out[4][0],"(3-d)/(2*m2)") and out[5]=={3:"(1)"}
 return dict(arithmetic_cases=len(examples),independent_engine="SymPy "+sp.__version__,kira_fixtures=3)
def main():
 dest=HERE/"pilot";dest.mkdir(exist_ok=True)
 summary=dict(arithmetic=arithmetic_checks(),families=[])
 previous={f["family"]:f for f in read(dest/"summary.json")["families"]} if (dest/"summary.json").exists() else {}
 split=read(MODEL/"split_manifest.json");metadata={x["family"]:x for x in split["families"] if x["split"]=="test"}
 predictions={x["family"]:x for x in read(MODEL/"model_test/prediction_manifest.json")["families"]}
 ids=["vacuum_L12_profile001","vacuum_L12_profile002","vacuum_L12_profile015","box_massless_one_offshell","propagator_two_loop_massless"]
 for fid in ids:
  old=previous.get(fid,{})
  if not old.get("error") and old.get("counts",{}).get("full")=={"exact_match":old.get("targets")} and all("independent_sample_checks" in r for r in old.get("runs",[])):
   summary["families"].append(old);continue
  clear_caches();start=time.monotonic()
  family=load_family(metadata[fid],predictions[fid],limit=6 if "vacuum_" not in fid else None)
  blocks=selected_blocks(family);counts={p:collections.Counter() for p in ["predicted","full","background"]}
  fs=dict(family=fid,targets=len(family["targets"]),selection_groups=len(blocks),runs=[])
  try:
   for j,batch in enumerate(batches(blocks)):
    w=Path(os.environ.get("KIRA_SCRATCH",str(WORK)))/("pilot_"+fid+"_"+str(j))
    if w.exists():shutil.rmtree(w)
    manifest=export(family,batch,w,quotient=False);run=run_kira(w)
    # Read reference data only after Kira has produced its output.
    refs={x["id"]:x for x in rows(DATA/metadata[fid]["references"])}
    assert run["status"]=="completed",run
    outpath=w/"results/Tuserweight/kira_targets.kira"
    records=assess(family,manifest,parse_output(outpath),refs)
    run["independent_sample_checks"]=check_records(records,refs)
    assert all(r["status"] in ("exact_match","residual_nonmasters") for r in records)
    byblock={b["id"]:b for b in manifest["blocks"]}
    for rec in records:
     for policy,tids in byblock[rec["block"]]["policies"].items():
      if rec["target"] in tids:counts[policy][rec["status"]]+=1
    detail=dict(manifest=manifest,run=run,records=records)
    with gzip.open(str(dest/(fid+"_%03d.json.gz"%j)),"wt",encoding="utf-8") as f:json.dump(detail,f,separators=(",",":"))
    with outpath.open("rb") as inp,gzip.open(str(dest/(fid+"_%03d.kira.gz"%j)),"wb") as out:shutil.copyfileobj(inp,out)
    if j==0:
     with (w/"run.log").open("rb") as inp,gzip.open(str(dest/(fid+".log.gz")),"wb") as out:shutil.copyfileobj(inp,out)
    fs["runs"].append(run);shutil.rmtree(w)
   fs["counts"]={p:dict(c) for p,c in counts.items()}
  except Exception:
   fs["error"]=traceback.format_exc()
   if w.exists():
    for name in ["run.log","system.kira","jobs.yaml"]:
     if (w/name).exists():
      with (w/name).open("rb") as inp,gzip.open(str(dest/(fid+".failed_"+name+".gz")),"wb") as out:shutil.copyfileobj(inp,out)
  fs["seconds"]=time.monotonic()-start;summary["families"].append(fs)
  write(dest/"summary.json",summary);print(json.dumps(fs),flush=True)
 write(dest/"summary.json",summary)
 if any("error" in f for f in summary["families"]):raise RuntimeError("Pilot errors require review")
if __name__=="__main__":
 main()
