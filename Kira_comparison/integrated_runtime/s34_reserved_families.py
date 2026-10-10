"""Define fresh physical test profiles before inspecting any reserved reductions."""
import datetime,hashlib,importlib.util,itertools,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location("physical_families",ROOT/"Kira_comparison/multiloop_native/s01_families.py")
physical=importlib.util.module_from_spec(spec);spec.loader.exec_module(physical)
def deeper(d):
 t=d["physical_propagators"];n=len(d["propagators"]);corner=[int(i<t) for i in range(n)];rows=[corner]
 for i in range(t):
  a=corner.copy();a[i]+=2;rows.append(a)
 for i,j in itertools.combinations(range(t),2):
  a=corner.copy();a[i]+=1;a[j]+=1;rows.append(a)
 for j in range(t,n):
  for i in range(t):
   a=corner.copy();a[i]+=1;a[j]=-1;rows.append(a)
 rows+=physical.targets(d)
 return [list(a) for a in dict.fromkeys(map(tuple,rows))]
def main():
 dest=HERE/"reserved_families.json";assert not dest.exists(),"Preserve reserved definitions"
 specs=[("sunrise",dict(masses=[1,2,2],p2=-5)),("sunrise",dict(masses=[1,2,4],p2=-7)),
  ("double_box",dict(s=-11,t=-13)),("double_box",dict(s=-13,t=-17)),
  ("vacuum3",dict(masses=[1,1,1,1,1,3])),("vacuum3",dict(masses=[1,1,1,3,3,3])),
  ("ladder3",dict(p2=-3,masses=[1,0,0,0,0,0,0,0])),
  ("ladder3",dict(p2=-5,masses=[1,0,0,0,0,0,0,0]))]
 prior=json.loads((ROOT/"Kira_comparison/multiloop_native/families.json").read_text())["cases"]
 old_groups={c["group"] for c in prior};cases=[];batches=[]
 for i,(kind,params) in enumerate(specs):
  d=physical.definition(kind,params);group=kind+":"+json.dumps(params,sort_keys=True);assert group not in old_groups
  name=f"runtime_reserved_{i:02d}_{kind}";targets=physical.targets(d)
  case=dict(id=name,split="reserved",group=group,topology_group=kind,definition=d,targets=targets)
  cases.append(case)
  if kind=="sunrise":
   batches.append(dict(case=name,size=len(targets)))
   deep=dict(case,id=name+"_deep",targets=deeper(d));cases.append(deep)
   batches.append(dict(case=deep["id"],size=32))
  else:
   for size in [32,128]:
    assert len(targets)>=size;batches.append(dict(case=name,size=size))
 result=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_profiles=len(specs),cases=cases,batches=batches,
  scope="New rational mass/kinematic points of sunrise, double-box, three-loop vacuum and three-loop ladder integrals; symbolic dimension d. Ladder topology excluded from current row training and validation.",
  no_reserved_calculation_before_policy_freeze=True)
 dest.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(dict(profiles=len(specs),batches=len(batches),sha256=hashlib.sha256(dest.read_bytes()).hexdigest())),flush=True)
if __name__=="__main__":main()
