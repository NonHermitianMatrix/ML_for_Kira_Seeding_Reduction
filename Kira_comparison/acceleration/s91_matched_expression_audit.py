"""Independently validate supplied-expression seed choices and raw Kira exports."""
import argparse,json,pathlib,re,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
from s01_common import read,write,sha,load_case,old,DATA,connected
from s08_verify import evaluate
from s39_records import read_record
from s61_evidence_archive import unpack
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--stage",required=True);ap.add_argument("--plan",default="plan.json");a=ap.parse_args()
 plan=read(HERE/a.plan)
 if a.stage=="expression_matched":
  frozen=read(HERE/"expression_matched_freeze.json")
  assert sha(HERE/a.plan)==frozen["plan_sha256"]
  assert sha(ROOT/"ML_model_seed_selection/trained_model.pt")==frozen["seed_checkpoint_sha256"]
  for name,digest in frozen["sha256"].items():assert sha(HERE/name)==digest,name
  for name,digest in frozen["input_sha256"].items():assert sha(ROOT/name)==digest,name
  assert len(list((HERE/a.stage).glob("*.json.gz")))==frozen["expected_trials"]
 total=0;completed=0;samples_checked=0;raw_checked=0;failed=[];hashes={};cache={}
 for path in sorted((HERE/a.stage).glob("*.json.gz")):
  r=read_record(path);total+=1;hashes[path.name]=sha(path)
  assert not any(c.get("status")=="mismatch" for c in r.get("checks",[]))
  if not r["success"] or r["status"]!="completed":
   failed.append(dict(trial=r["trial"],status=r["status"]));continue
  key=r["partition"],r["case"],r["size"]
  if key not in cache:
   fam=load_case(plan[key[0]][key[1]],key[2])
   refs={x["id"]:x for x in old.rows(DATA/fam["meta"]["references"])}
   cache[key]=fam,refs
  fam,refs=cache[key];want=[t["id"] for t in fam["targets"]]
  assert r["targets"]==want and [c["target"] for c in r["checks"]]==want
  assert all(c["status"]=="exact_match" for c in r["checks"]);completed+=1
  if r["policy"].startswith("stored_ml"):
   selected=set()
   for target in r["model"]["probabilities"]:
    assert target["target"] in want and len(target["probabilities"])==len(fam["seeds"])
    assert all(0<=p<=1 for p in target["probabilities"])
    selected.update(seed for seed,p in zip(fam["seeds"],target["probabilities"]) if p>=r["model"].get("threshold",.5))
   assert selected=={tuple(s) for s in r["model"]["selected_seeds"]}
   available=[e for e in fam["identities"] if e["source"]["kind"]!="ibp" or tuple(e["source"]["seed"]) in selected]
   if "source_ids" in r["attempts"][0]:
    assert r["attempts"][0]["source_ids"]==[e["id"] for e in connected(available,fam["targets"],fam["masters"])]
  if r["policy"] in ("stored_distance","stored_distance_checked"):
   components={tuple(term["indices"]) for target in fam["targets"] for term in target["terms"]}
   order=sorted(fam["seeds"],key=lambda b:(min(sum(abs(x-y) for x,y in zip(b,c)) for c in components),b))
   selected=set(order[:64])
   assert selected=={tuple(s) for s in r["model"]["selected_seeds"]}
   available=[e for e in fam["identities"] if e["source"]["kind"]!="ibp" or tuple(e["source"]["seed"]) in selected]
   if "source_ids" in r["attempts"][0]:
    assert r["attempts"][0]["source_ids"]==[e["id"] for e in connected(available,fam["targets"],fam["masters"])]
  if r["policy"]=="stored_pool" or r["fallback"]:
   assert r["attempts"][-1]["source_ids"]==[e["id"] for e in connected(fam["identities"],fam["targets"],fam["masters"])]
  final=len(r["attempts"])-1;ev=unpack(r["evidence"])
  keys=[k for k in ev if k.startswith("attempt%d/"%final) and k.endswith("kira_targets.kira")]
  assert len(keys)==1;raw=ev[keys[0]]
  import hashlib
  assert hashlib.sha256(raw.encode()).hexdigest()==r["attempts"][-1]["export_sha256"]
  rows={};block=[]
  def consume(lines):
   pairs=[]
   for line in lines:
    m=re.fullmatch(r"(\d+)\*\((.*)\)",line.strip());assert m,line
    pairs.append((int(m[1]),m[2]))
   assert old.exact_equal(pairs[0][1],"-1");rows[pairs[0][0]]=pairs[1:]
  for line in raw.splitlines()+[""]:
   if line.strip():block.append(line)
   elif block:consume(block);block=[]
  manifest=r["attempts"][-1]["manifest"]
  for check in r["checks"]:
   tid=check["target"];weight=next(int(k) for k,v in manifest["targets"].items() if v["target"]==tid)
   assert weight in rows
   for sample in refs[tid]["samples"]:
    point=tuple(sorted(sample["point"].items()));prime=sample["prime"];got={};reported={}
    expected={tuple(map(int,k.split(","))):int(v)%prime for k,v in sample["master_coefficients"].items() if int(v)%prime}
    for n,c in rows[weight]:
     index=tuple(manifest["mapping"][str(n)]["indices"])
     got[index]=(got.get(index,0)+evaluate(c,point,prime))%prime
    for term in check["coefficients"]:
     index=tuple(term["indices"])
     reported[index]=(reported.get(index,0)+evaluate(term["coefficient"],point,prime))%prime
    assert {k:v for k,v in got.items() if v}==expected=={k:v for k,v in reported.items() if v}
    samples_checked+=1;raw_checked+=1
 assert total>0
 result=dict(passed=True,stage=a.stage,trials=total,exact_completions=completed,incomplete=failed,
  independent_master_sample_checks=samples_checked,raw_export_checks=raw_checked,result_sha256=hashes)
 write(HERE/(a.stage+"_validation.json"),result)
 print(json.dumps({k:v for k,v in result.items() if k!="result_sha256"}),flush=True)
if __name__=="__main__":main()
