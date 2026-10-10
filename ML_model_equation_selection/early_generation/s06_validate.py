"""Compare complete costs and choose validation candidates without reading reserved results."""
import argparse,collections,json,math,pathlib,statistics
from s04_workflows import HERE,ROOT,read,save,setup,cases,reference,workflow,guard
FIELDS=["complete_seconds","equation_preparation_seconds","forward_seconds"]
def rows(directory):return [read(p) for p in sorted(directory.glob("*.json.gz"))]
def aggregate(rs):
 grouped=collections.defaultdict(lambda:collections.defaultdict(list))
 for r in rs:
  assert r["success"]
  grouped[(r["case"],r["size"])][r["label"]].append(r)
 out=[]
 for (case,n),methods in sorted(grouped.items()):
  sample=next(iter(methods.values()))[0]
  out.append(dict(case=case,size=n,topology=sample["topology"],group=sample["group"],methods={k:dict(repetitions=len(v),**{f:statistics.median(z[f] for z in v) for f in FIELDS},failed_attempts=sum(not a["success"] for z in v for a in z["attempts"]),fallback_workflows=sum(z["attempt_count"]>1 for z in v),skipped_construction_calls=statistics.median(z["skipped_construction_calls"] for z in v)) for k,v in methods.items()}))
 return out
def gmean(xs):return math.exp(sum(math.log(x) for x in xs)/len(xs))
def compare(bs,label,base="early_off"):
 paired=[b for b in bs if label in b["methods"] and base in b["methods"]]
 if not paired:return None
 return dict(batches=len(paired),**{f:gmean([b["methods"][label][f]/b["methods"][base][f] for b in paired]) for f in FIELDS},fallback_workflows=sum(b["methods"][label]["fallback_workflows"] for b in paired))
def controls():
 for i,(c,n) in enumerate(cases("validation")):
  ref=reference(c,n)
  for distance in [2,3,4]:
   label="distance"+str(distance);out=HERE/"validation/pilot"/f'{c["id"]}_n{n}_{label}.json.gz'
   if out.exists():continue
   r=workflow(c,n,label,ref,out,mode="distance",threshold=distance)
   print(json.dumps(dict(phase="control",case=c["id"],size=n,label=label,seconds=r["complete_seconds"],attempts=r["attempt_count"])),flush=True)
def candidates():
 bs=aggregate(rows(HERE/"validation/pilot"));selected={}
 for top in sorted({b["topology"] for b in bs}):
  sub=[b for b in bs if b["topology"]==top]
  labels=set.intersection(*[set(b["methods"]) for b in sub])
  learned=sorted([(compare(sub,l),l) for l in labels if l.startswith("early_d")],key=lambda z:(z[0]["fallback_workflows"]>0,z[0]["complete_seconds"]))
  distances=sorted([(compare(sub,l),l) for l in labels if l.startswith("distance")],key=lambda z:(z[0]["fallback_workflows"]>0,z[0]["complete_seconds"]))
  selected[top]=dict(models=[l for _,l in learned[:2]],distance=distances[0][1],pilot={l:v for v,l in learned+distances})
 p=HERE/"validation/candidates.json";assert not p.exists();p.write_text(json.dumps(dict(by_topology=selected,batches=bs),indent=2)+"\n")
 print(json.dumps(selected,indent=2),flush=True)
def method(label):
 if label=="early_off":return dict(label=label)
 if label.startswith("distance"):return dict(label=label,mode="distance",threshold=int(label[len("distance"):]))
 model,t=label.split("_t");return dict(label=label,mode="learned",model=model,threshold=float(t))
def confirm():
 config=json.loads((HERE/"validation/candidates.json").read_text())
 for i,(c,n) in enumerate(cases("validation")):
  ref=reference(c,n);route=config["by_topology"][c["topology_group"]]
  labels=["early_off"]+route["models"]+[route["distance"]]
  for rep in range(3):
   ordered=labels[rep%len(labels):]+labels[:rep%len(labels)]
   if (i+rep)%2:ordered=list(reversed(ordered))
   for label in ordered:
    out=HERE/"validation/confirmation"/f'{c["id"]}_n{n}_{label}_r{rep}.json.gz'
    if out.exists():continue
    r=workflow(c,n,ref=ref,out=out,**method(label))
    print(json.dumps(dict(phase="validation",case=c["id"],size=n,label=label,rep=rep,seconds=r["complete_seconds"],attempts=r["attempt_count"])),flush=True)
def summarize():
 bs=aggregate(rows(HERE/"validation/confirmation"));selected={}
 for top in sorted({b["topology"] for b in bs}):
  sub=[b for b in bs if b["topology"]==top];labels=set.intersection(*[set(b["methods"]) for b in sub])
  checks={l:compare(sub,l) for l in sorted(labels) if l!="early_off"}
  learned=sorted([(v,l) for l,v in checks.items() if l.startswith("early_d") and v["fallback_workflows"]==0 and v["complete_seconds"]<.99 and v["equation_preparation_seconds"]<.95],key=lambda z:z[0]["complete_seconds"])
  selected[top]=dict(label=learned[0][1] if learned else "early_off",comparisons=checks)
 summary=dict(by_topology=selected,batches=bs,criteria="No validation fallback, complete-time ratio below .99, equation-preparation ratio below .95. Choose minimum complete-time ratio among eligible learned candidates. Validation uses three repetitions; independent testing follows a separate freeze.")
 (HERE/"validation/summary.json").write_text(json.dumps(summary,indent=2)+"\n");print(json.dumps(selected,indent=2),flush=True);guard()
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("action",choices=["controls","candidates","confirm","summarize"]);a=ap.parse_args();setup()
 globals()[a.action]()
