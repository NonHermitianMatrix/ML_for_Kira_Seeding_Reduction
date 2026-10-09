"""Independently replay exact-operation records and verify archived native reductions."""
import gzip,json,math,pathlib,re,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
from s01_common import read,write,sha,load_case,old,DATA
from s08_verify import evaluate
def vec(row,point,p):
 return {k:v for k,c in row.items() if (v:=evaluate(c,point,p))}
def trace_rows(text):
 lines=iter(text.splitlines());out=[]
 def row():
  n=int(next(lines));r={}
  for _ in range(n):
   key,c=next(lines).split("\t",1);assert key.startswith("F[") and key.endswith("]")
   r[key[2:-1]]=c
  return r
 for marker in lines:
  assert marker=="STEP";out.append((row(),row(),row()))
 return out
def check_update(src,dst,after,samples):
 key=next(iter(src));assert key==next(iter(dst))
 valid=0;singular=0
 for sample in samples:
  p=sample["prime"];point=tuple(sorted(sample["point"].items()))
  try:
   q=vec(src,point,p);r=vec(dst,point,p);a=vec(after,point,p)
   if not q.get(key):singular+=1;continue
   factor=r.get(key,0)*pow(q[key],-1,p)%p
  except (ZeroDivisionError,ValueError):singular+=1;continue
  expected={k:v for k in set(q)|set(r) if (v:=(r.get(k,0)-factor*q.get(k,0))%p)}
  assert expected==a and key not in after
  valid+=1
 assert valid>=2,"Insufficient independent nonsingular points"
 return valid,singular
def main():
 plan=read(HERE/"plan.json");frozen=read(HERE/"frozen_inputs.json")
 for name,digest in frozen["sha256"].items():assert sha(ROOT/name)==digest,name
 total=0;samplechecks=0;rowchecks=0;singular=0;changed_sources=0;choices=0;failed=[];hashes={}
 for caseid,case in enumerate(plan["family_cases"]):
  fam=load_case(case,min(16,case["meta"]["counts"]["targets"]))
  refs={r["id"]:r for r in old.rows(DATA/case["meta"]["references"])}
  samples=refs[fam["targets"][0]["id"]]["samples"]
  jobs=None
  for rep in range(3):
   for policy in plan["policies"]:
    path=HERE/"results"/("%02d_r%d_%s.json.gz"%(caseid,rep,policy))
    r=json.load(gzip.open(path,"rt"));hashes[path.name]=sha(path);total+=1
    assert (r["case"],r["repetition"],r["policy"])==(caseid,rep,policy)
    if r["status"]!="completed" or not r["success"]:
     failed.append(dict(trial=r["trial"],status=r["status"]));continue
    ev=r["evidence"];config=json.loads(ev["native/jobs.yaml"])
    if jobs is None:jobs=config
    else:assert config==jobs,"Changed seeding configuration"
    assert r["targets"]==[t["id"] for t in fam["targets"]]
    raw=ev["native/results/F/kira_targets.kira"];native={};block=[]
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
     ref=refs[t["id"]]
     for sample in ref["samples"]:
      point=tuple(sorted(sample["point"].items()));p=sample["prime"];got={}
      for term in t["terms"]:
       a=",".join(map(str,term["indices"]));v=evaluate(term["coefficient"],point,p)
       for b,c in native.get(a,{a:"1"}).items():
        got[b]=(got.get(b,0)+v*evaluate(c,point,p))%p
      expected={k:int(v)%p for k,v in sample["master_coefficients"].items() if int(v)%p}
      assert {k:v for k,v in got.items() if v}==expected,(r["trial"],t["id"])
      samplechecks+=1
    steps=trace_rows(ev.get("native/row_trace.txt",""))
    if policy!="stock":
     metrics=r["native"]["forward"]
     assert len(steps)==sum(m["steps"] for m in metrics)
     assert sum(1+2*len(src) for src,dst,after in steps)==sum(m["coefficient_operations"] for m in metrics)
     for src,dst,after in steps:
      a,b=check_update(src,dst,after,samples);rowchecks+=a;singular+=b
    if policy=="learned":
     events=[json.loads(s) for s in ev.get("native/row_trace.txt.policy.jsonl.gz","").splitlines()]
     current={};updated=set();chosen=None;position=0
     for event in events:
      if event["event"]=="initial":current=event["rows"];updated=set()
      elif event["event"]=="choice":
       group=event["group"];pivot=event["pivot"];a=event["selected"]
       assert pivot not in {",".join(map(str,x)) for x in fam["masters"]}
       assert set(group)=={k for k,v in current.items() if next(iter(v),None)==pivot}
       pairs=[(q,d) for q in group for d in group if q!=d]
       probs=event["probabilities"];assert len(probs)==len(pairs)
       assert all(0<=v<=1 for v in probs) and abs(sum(probs)-1)<1e-5
       index=pairs.index((a["source_row"],a["destination_row"]))
       assert probs[index]==max(probs) and event["confidence"]==probs[index]
       assert event["nonzeros"]==sum(len(vec(v,tuple(sorted(json.loads(ev["context.json"])["point"].items())),
                                                 json.loads(ev["context.json"])["prime"])) for v in current.values())
       chosen=a;choices+=1
       changed_sources+=int(a["source_row"] in updated)
      elif event["event"]=="update":
       assert chosen is not None and event["row"]==chosen["destination_row"]
       src=current[chosen["source_row"]];dst=current[chosen["destination_row"]]
       assert (src,dst,event["terms"])==steps[position];position+=1
       if event["terms"]:current[event["row"]]=event["terms"]
       else:del current[event["row"]]
       updated.add(event["row"]);chosen=None
      elif event["event"]=="error":raise AssertionError(event)
     assert position==len(steps)
  print(json.dumps(dict(family=fam["id"],trials=total,choices=choices)),flush=True)
 assert total==len(list((HERE/"results").glob("*.json.gz")))
 write(HERE/"validation.json",dict(passed=True,trials=total,incomplete=failed,
      independent_master_sample_checks=samplechecks,row_sample_checks=rowchecks,
      singular_row_sample_points=singular,live_choices=choices,
      choices_using_previously_updated_source=changed_sources,result_sha256=hashes))
if __name__=="__main__":main()

