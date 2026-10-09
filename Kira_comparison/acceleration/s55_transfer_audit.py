"""Independent modular checks of native exports and exact-update evidence."""
import argparse,gzip,json,pathlib,re,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
from s01_common import read,write,sha,load_case,old,DATA,load_module
from s08_verify import evaluate
from s61_evidence_archive import unpack
from s39_records import read_record
live=load_module("accel_live_audit",HERE.parent/"live_matrix/s07_audit.py")
_original_load_case=load_case
def load_case(case,size):
 offset=read(HERE/"transfer_plan.json")["target_offset"]
 fam=_original_load_case(case,size+offset);fam["targets"]=fam["targets"][offset:]
 assert len(fam["targets"])==size
 return fam
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--stage",default="transfer_test");a=ap.parse_args()
 plan=read(HERE/"transfer_plan.json");cache={};total=0;checks=0;rowchecks=0;choices=0;failed=[];hashes={};skipped=0;failed_trace_attempts=0;cpp_choices=0;cpp_scored=0;cpp_forced=0
 frozen=None
 if a.stage=="results":
  from s38_compact_records import compact_completed
  print(json.dumps(compact_completed(min_age=0)),flush=True)
  frozen=read(HERE/"frozen_policy.json")
  for name,digest in frozen["sha256"].items():assert sha(HERE/name)==digest,name
  for name,digest in frozen["input_sha256"].items():assert sha(ROOT/name)==digest,name
  for name,digest in frozen["validation_sha256"].items():assert sha(HERE/name)==digest,name
  assert sha(ROOT/"ML_model_seed_selection/trained_model.pt")==plan["seed_checkpoint_sha256"]
  assert sha(ROOT/"ML_model_reduction/trained_model.pt")==plan["row_checkpoint_sha256"]
  assert sha(ROOT/"ML_model_seed_selection/split_manifest.json")==plan["split_sha256"]
  assert sha(ROOT/".tools/kira-cpp-row/kira")==read(HERE/"cpp_build.json")["binary_sha256"]

 for path in sorted((HERE/a.stage).glob("*.json.gz")):
  r=read_record(path);total+=1;hashes[path.name]=sha(path)
  if not r.get("measured",True):skipped+=1
  assert not any(x.get("status")=="mismatch" for x in r.get("checks",[])),("Incorrect final coefficients",r["trial"])
  if r["status"]!="completed" or not r["success"]:
   failed.append(dict(trial=r["trial"],status=r["status"]));continue
  key=(r["partition"],r["case"],r["size"])
  if key not in cache:
   fam=load_case(plan[key[0]][key[1]],key[2])
   refs={x["id"]:x for x in old.rows(DATA/fam["meta"]["references"])}
   cache[key]=(fam,refs)
  fam,refs=cache[key];assert r["targets"]==[t["id"] for t in fam["targets"]]
  assert [x["target"] for x in r["checks"]]==r["targets"]
  assert all(x["status"]=="exact_match" for x in r["checks"])
  ev=unpack(r["evidence"]);final="attempt1" if r["fallback"] else "attempt0"
  raw=ev[final+"/results/F/kira_targets.kira"];native={};block=[]
  def consume(lines):
   pairs=[]
   for line in lines:
    m=re.fullmatch(r"F\[([-\d,]+)\]\*\((.*)\)",line.strip());assert m
    pairs.append((m[1],m[2]))
   assert old.exact_equal(pairs[0][1],"-1");native[pairs[0][0]]=dict(pairs[1:])
  for line in raw.splitlines()+[""]:
   if line.strip():block.append(line)
   elif block:consume(block);block=[]
  for t in fam["targets"]:
   for sample in refs[t["id"]]["samples"]:
    point=tuple(sorted(sample["point"].items()));p=sample["prime"];got={}
    for term in t["terms"]:
     c=",".join(map(str,term["indices"]));v=evaluate(term["coefficient"],point,p)
     for b,d in native.get(c,{c:"1"}).items():got[b]=(got.get(b,0)+v*evaluate(d,point,p))%p
    expected={k:int(v)%p for k,v in sample["master_coefficients"].items() if int(v)%p}
    assert {k:v for k,v in got.items() if v}==expected,(r["trial"],t["id"])
    checks+=1
  if r.get("seed_audits"):
   allowed=set(ev["seeds.txt"].splitlines())
   for audit in r["seed_audits"].values():
    assert audit["allowed"]==len(allowed) and set(audit["used"])<=allowed
    assert len(audit["used"])<=audit["accepted_calls"]<=audit["seen"]
  samples=refs[fam["targets"][0]["id"]]["samples"]
  for prefix in ("attempt0","attempt1"):
   number=int(prefix[-1])
   if number<len(r.get("attempts",[])) and "error" in r["attempts"][number]:
    failed_trace_attempts+=1
    continue
   steps=live.trace_rows(ev.get(prefix+"/row_trace.txt",""))
   for src,dst,after in steps:
    n,_=live.check_update(src,dst,after,samples);rowchecks+=n
   events=[json.loads(line) for line in ev.get(prefix+"/row_trace.txt.policy.jsonl.gz","").splitlines()]
   current={};position=0;chosen=None
   for event in events:
    if event["event"]=="initial":current=event["rows"]
    elif event["event"]=="choice":
     group=event["group"];pivot=event["pivot"];action=event["selected"]
     assert pivot not in {",".join(map(str,x)) for x in fam["masters"]}
     assert set(group)=={k for k,v in current.items() if next(iter(v),None)==pivot}
     pairs=[(q,d) for q in group for d in group if q!=d]
     if "candidate_actions" in event:
      requested=[(x["source_row"],x["destination_row"]) for x in event["candidate_actions"]]
      assert set(requested)<=set(pairs) and len(set(requested))==len(requested)
      if r["policy"]=="row_source":
       assert set(requested)=={(q,max(group,key=int)) for q in group if q!=max(group,key=int)}
      else:assert requested==pairs
      pairs=requested
     probs=event["probabilities"]
     assert len(probs)==len(pairs) and abs(sum(probs)-1)<1e-5
     index=pairs.index((action["source_row"],action["destination_row"]))
     assert probs[index]==max(probs)==event["confidence"]
     chosen=action;choices+=1
    elif event["event"]=="update":
     assert chosen and event["row"]==chosen["destination_row"]
     assert (current[chosen["source_row"]],current[chosen["destination_row"]],event["terms"])==steps[position]
     position+=1
     if event["terms"]:current[event["row"]]=event["terms"]
     else:del current[event["row"]]
     chosen=None
    elif event["event"]=="error":raise AssertionError(event)
   if events:assert position==len(steps)
   cpp=[json.loads(line) for line in ev.get(prefix+"/cpp_choices.jsonl","").splitlines()]
   if cpp:
    assert len(cpp)==len(steps)
    for event in cpp:
     group=event["group"];source=event["source"];destination=event["destination"];prob=event["probabilities"]
     assert destination==max(group) and source in group and source!=destination
     assert event["pivot"] not in {",".join(map(str,x)) for x in fam["masters"]}
     assert len(prob)==len(group)-1 and all(0<=x<=1 for x in prob) and abs(sum(prob)-1)<1e-5
     assert prob[group.index(source)]==max(prob)
     assert event["used_model"]==(len(group)>2)
     cpp_choices+=1;cpp_scored+=event["used_model"];cpp_forced+=not event["used_model"]
 assert total==60,total
 manifest=read(HERE/"transfer_freeze.json")
 for name,digest in manifest["sha256"].items():assert sha(HERE/name)==digest,name
 for name,digest in manifest["input_sha256"].items():assert sha(ROOT/name)==digest,name
 assert sha(ROOT/".tools/kira-cpp-row/kira")==read(HERE/"cpp_build.json")["binary_sha256"]
 assert total>0
 if frozen:assert total==frozen["expected_trials"],(total,frozen["expected_trials"])
 out=dict(passed=True,frozen_inputs_verified=bool(frozen),stage=a.stage,trials=total,executed_trials=total-skipped,skipped_repetitions=skipped,completed=total-len(failed),incomplete=failed,
  independent_master_sample_checks=checks,row_sample_checks=rowchecks,live_choices=choices,
  compiled_choices=cpp_choices,compiled_model_choices=cpp_scored,compiled_forced_actions=cpp_forced,
  unaudited_failed_attempt_traces=failed_trace_attempts,result_sha256=hashes)
 write(HERE/(a.stage+"_validation.json"),out);print(json.dumps({k:v for k,v in out.items() if k!="result_sha256"}),flush=True)
if __name__=="__main__":main()
