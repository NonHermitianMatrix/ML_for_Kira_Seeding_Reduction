"""Define native integral families and independent targets before experiments."""
import hashlib,itertools,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
def definition(kind,parameters):
 if kind=="sunrise":
  loops=["k1","k2"];external=["p"];momenta=["k1","k2","p-k1-k2","p-k1","p-k2"]
  masses=parameters["masses"]+[0,0];physical=3
  rules=[[["p","p"],str(parameters["p2"])]]
 elif kind=="double_box":
  loops=["k1","k2"];external=["p1","p2","p3"];physical=7
  momenta=["k1","k1-p1","k1-p1-p2","k2","k2-p1-p2","k2-p1-p2-p3","k1-k2","k1-p3","k2-p1"]
  masses=parameters.get("masses",[0]*7)+[0,0];s,t=parameters["s"],parameters["t"]
  rules=[[["p1","p1"],"0"],[["p2","p2"],"0"],[["p3","p3"],"0"],
         [["p1","p2"],str(s)+"/2"],[["p1","p3"],str(t)+"/2"],[["p2","p3"],str(-s-t)+"/2"]]
 elif kind=="vacuum3":
  loops=["k1","k2","k3"];external=[];physical=6
  momenta=["k1","k2","k3","k1-k2","k2-k3","k1-k3"]
  masses=parameters["masses"];rules=[]
 elif kind=="ladder3":
  loops=["k1","k2","k3"];external=["p"];physical=8
  momenta=["k1","k1-p","k2","k2-p","k3","k3-p","k1-k2","k2-k3","k1-k3"]
  masses=parameters.get("masses",[0]*8)+[0]
  rules=[[["p","p"],str(parameters["p2"])]]
 else:raise ValueError(kind)
 return dict(name="F",kind=kind,loop_momenta=loops,external_momenta=external,
  propagators=[dict(momentum=q,mass_squared=str(m)) for q,m in zip(momenta,masses)],
  invariants=[],scalarproduct_rules=rules,top_level_sectors=[(1<<physical)-1],physical_propagators=physical,
  parameters=parameters,coefficient_field="Q(d); all listed squared masses and invariants fixed in a common unit")
def targets(d):
 t=d["physical_propagators"];n=len(d["propagators"]);rows=[]
 for pinches in range(0,min(3,t-2)+1):
  for missing in itertools.combinations(range(t),pinches):
   a=[int(i<t and i not in missing) for i in range(n)]
   rows.append(tuple(a))
   for i in range(t):
    if a[i]:
     b=a.copy();b[i]+=1;rows.append(tuple(b))
   for i in range(t,n):
    b=a.copy();b[i]=-1;rows.append(tuple(b))
 # Explicit ordering begins with the top corner and its dots, then pinched
 # sectors. These are integral indices, not constructed master combinations.
 return [list(a) for a in dict.fromkeys(rows)]
def main():
 specifications={
 "training":[("sunrise",dict(masses=[1,1,1],p2=-1)),("sunrise",dict(masses=[1,2,3],p2=-2)),
  ("double_box",dict(s=-1,t=-2)),("double_box",dict(s=-2,t=-3)),
  ("vacuum3",dict(masses=[1,1,1,1,1,1])),("vacuum3",dict(masses=[1,1,1,2,2,2]))],
 "validation":[("sunrise",dict(masses=[1,1,2],p2=-3)),("double_box",dict(s=-3,t=-4)),
  ("vacuum3",dict(masses=[1,1,1,1,1,2]))],
 "reserved":[("double_box",dict(s=-5,t=-7)),("double_box",dict(s=-7,t=-11)),
  ("vacuum3",dict(masses=[1,1,2,1,2,2])),("vacuum3",dict(masses=[1,2,2,1,2,2])),
  ("ladder3",dict(p2=-1)),("ladder3",dict(p2=-2,masses=[1,0,0,0,0,0,0,0]))]}
 cases=[]
 for split,items in specifications.items():
  for i,(kind,par) in enumerate(items):
   d=definition(kind,par);tid=f"{split}_{i:02d}_{kind}"
   cases.append(dict(id=tid,split=split,group=kind+":"+json.dumps(par,sort_keys=True),
    topology_group=kind,definition=d,targets=targets(d)))
 assert len({c["group"] for c in cases})==len(cases)
 plan=dict(cases=cases,larger_batch_sizes=[32,128],pilot_size=8,
  physical_target_selection="fixed sector/dot/numerator enumeration; no reverse-construction labels",
  original_models_preserved=True,scalar_dimension="d",policy_selection_partition="validation",
  reserved_case_results_must_not_select_policies=True)
 p=HERE/"families.json";assert not p.exists()
 p.write_text(json.dumps(plan,indent=2)+"\n")
 print(json.dumps(dict(cases=len(cases),sha256=hashlib.sha256(p.read_bytes()).hexdigest())))
if __name__=="__main__":main()
