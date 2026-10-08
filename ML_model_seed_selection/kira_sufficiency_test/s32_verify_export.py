"""Regenerate each actual Kira input from public targets and selected identities."""
import collections,hashlib
from s02_common import *
def prepare(meta):
 identities=list(rows(family_file(meta["family"],"identities.jsonl.gz")))
 byid={e["id"]:e for e in identities}
 assert len(byid)==len(identities)
 return dict(identities=identities,byid=byid,targets={t["id"]:t for t in rows(DATA/meta["inputs"])},
  seeds=[tuple(a) for a in read(DATA/meta["seeds"])["indices"]],pools={})
def verify(state,manifest):
 mapping={};allweights=set()
 for weight,entry in manifest["mapping"].items():
  weight=int(weight);assert weight not in allweights;allweights.add(weight)
  inverse=mapping.setdefault(entry["block"],{})
  a=tuple(entry["indices"]);assert a not in inverse;inverse[a]=weight
 targets=collections.defaultdict(list);targetweights=set()
 for weight,t in sorted(manifest["targets"].items(),key=lambda item:int(item[0])):
  weight=int(weight);assert weight not in allweights and weight not in targetweights
  targetweights.add(weight);targets[t["block"]].append((weight,t["target"]))
 assert len(allweights)+len(targetweights)==manifest["columns"]
 assert len({b["id"] for b in manifest["blocks"]})==len(manifest["blocks"])
 digest=hashlib.sha256();equations=0
 def line(text):digest.update(text.encode("utf-8"))
 def coefficient(text):return "".join(str(text).split()).replace("**","^")
 for b in manifest["blocks"]:
  bid=b["id"];mask=tuple(b["candidate_positions"])
  assert mask==tuple(sorted(set(mask))) and all(0<=i<len(state["seeds"]) for i in mask)
  if mask not in state["pools"]:
   seeds={state["seeds"][i] for i in mask}
   pool=[e for e in state["identities"] if e["source"]["kind"]!="ibp" or tuple(e["source"]["seed"]) in seeds]
   incidence=collections.defaultdict(list)
   for e in pool:
    for term in e["terms"]:incidence[tuple(term["indices"])].append(e["id"])
   state["pools"][mask]=(pool,incidence)
  pool,incidence=state["pools"][mask]
  assert b["available_equations"]==len(pool)
  supplied=b["source_equations"];assert len(supplied)==len(set(supplied))
  allowed={e["id"] for e in pool};assert set(supplied)<=allowed
  requested={tid for _,tid in targets[bid]}
  assert requested=={tid for tids in b["policies"].values() for tid in tids}
  connected={tuple(term["indices"]) for tid in requested for term in state["targets"][tid]["terms"]}
  pending=list(connected);required=set()
  while pending:
   for eid in incidence.get(pending.pop(),()):
    if eid in required:continue
    required.add(eid)
    for term in state["byid"][eid]["terms"]:
     a=tuple(term["indices"])
     if a not in connected:connected.add(a);pending.append(a)
  # Splitting a previous group can retain additional disconnected components.
  assert required<=set(supplied),"Missing connected source identity"
  for eid in supplied:
   e=state["byid"][eid]
   for term in e["terms"]:
    weight=mapping[bid][tuple(term["indices"])]
    line("%d*(%s)\n"%(weight,coefficient(term["coefficient"])))
   line("\n");equations+=1
  for weight,tid in targets[bid]:
   line("%d*(1)\n"%weight)
   for term in state["targets"][tid]["terms"]:
    integral=mapping[bid][tuple(term["indices"])]
    line("%d*(-(%s))\n"%(integral,coefficient(term["coefficient"])))
   line("\n");equations+=1
 for weight in manifest["master_unit_rows"]:
  assert weight in allweights
  line("%d*(1)\n\n"%weight);equations+=1
 assert equations==manifest["equations"]
 assert digest.hexdigest()==manifest["input_sha256"],"Public input regeneration disagrees"
 return True
