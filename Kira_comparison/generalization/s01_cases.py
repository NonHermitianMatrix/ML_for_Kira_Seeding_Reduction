"""Define new physical scattering families without using learned scores."""
import copy,hashlib,itertools,json,pathlib
import sympy as sp
HERE=pathlib.Path(__file__).resolve().parent
def build(kind,symbolic,profile=0):
 if kind=="pentagon":
  loops=["k1"];external=["p1","p2","p3","p4"];physical=5
  momenta=["k1","k1-p1","k1-p1-p2","k1-p1-p2-p3","k1-p1-p2-p3-p4"]
  names=["s12","s23","s34","s45","s51"]
  a,b,c,e,f=sp.symbols(" ".join(names))
  pairs={(0,1):a/2,(1,2):b/2,(2,3):c/2,(0,2):(e-a-b)/2,
         (1,3):(f-b-c)/2,(0,3):(b-e-f)/2}
  values=[-11-20*profile,-13-20*profile,-17-20*profile,-19-20*profile,-23-20*profile]
 else:
  external=["p1","p2","p3"];names=["s","t"];s,t=sp.symbols("s t");mass=sp.Integer(0)
  if kind=="one_mass_box":names+=["q2"];mass=sp.Symbol("q2")
  pairs={(0,1):s/2,(0,2):-t/2,(1,2):(s+t-mass)/2}
  values=[-113-18*profile,-127-10*profile]+([-149-12*profile] if mass!=0 else [])
  if kind=="nonplanar_box":
   loops=["k1","k2"];physical=7
   momenta=["k1","k2","p1-k1","p2-k2","p1+p2-p3-k1","p1-k1+k2","p1-p3-k1+k2","k1-p3","k2-p1-p2"]
  elif kind=="one_mass_box":
   loops=["k1"];physical=4
   momenta=["k1","k1-p1","k1-p1-p2","k1-p3"]
  else:raise ValueError(kind)
 substitution={} if symbolic else dict(zip(map(sp.Symbol,names),values))
 rules=[]
 for i in range(len(external)):
  for j in range(i,len(external)):
   value=sp.Integer(0) if i==j else pairs[(i,j)]
   rules.append([[external[i],external[j]],str(value.subs(substitution))])
 definition=dict(name="F",kind=kind,loop_momenta=loops,external_momenta=external,
  physical_propagators=physical,propagators=[dict(momentum=m,mass_squared="0") for m in momenta],
  invariants=[[n,2] for n in names] if symbolic else [],scalarproduct_rules=rules,
  top_level_sectors=[2**physical-1],coefficient_field="Q(d,"+",".join(names)+")" if symbolic else "Q(d)",
  parameters=dict(symbolic=symbolic,values=dict(zip(names,values)) if not symbolic else {}))
 return definition
def targets(d):
 n=len(d["propagators"]);p=d["physical_propagators"];out=[]
 for pinch in range(2):
  for missing in itertools.combinations(range(p),pinch):
   a=[int(i<p and i not in missing) for i in range(n)];out.append(a)
   for i in range(p):
    if a[i]:b=a.copy();b[i]+=1;out.append(b)
   for i in range(p,n):b=a.copy();b[i]=-1;out.append(b)
 return out
def audit(d):
 lm=sp.symbols(" ".join(d["loop_momenta"]),seq=True);em=sp.symbols(" ".join(d["external_momenta"]),seq=True)
 mom=lm+em;terms=[lm[i]*lm[j] for i in range(len(lm)) for j in range(i,len(lm))]+[l*p for l in lm for p in em]
 mat=sp.Matrix([[sp.expand(sp.sympify(p["momentum"])**2).coeff(t) for t in terms] for p in d["propagators"]])
 gram=sp.zeros(len(em))
 for (x,y),v in d["scalarproduct_rules"]:
  i=d["external_momenta"].index(x);j=d["external_momenta"].index(y);gram[i,j]=gram[j,i]=sp.sympify(v)
 det=sp.factor(gram.det());rank=mat.rank()
 assert rank==len(terms)==len(d["propagators"])
 assert det!=0
 return dict(scalar_products=len(terms),rank=rank,external_gram_determinant=str(det))
def case(kind,symbolic,profile,split,size):
 d=build(kind,symbolic,profile);cid=f"{kind}_{'symbolic' if symbolic else 'point'+str(profile)}"
 return dict(id=cid,split=split,group=cid,topology_group=kind,definition=d,targets=targets(d)[:size],audit=audit(d),size=size)
def main():
 cases=[]
 for kind in ["nonplanar_box","pentagon"]:
  for profile in [2,3]:cases.append(case(kind,False,profile,"reserved",16))
 for kind,size in [("nonplanar_box",10),("pentagon",6),("one_mass_box",8)]:
  cases.append(case(kind,True,0,"reserved",size))
 pilots=[case("nonplanar_box",False,1,"development",4),
         case("pentagon",True,0,"development",2),case("one_mass_box",True,0,"development",2),
         case("nonplanar_box",True,0,"development",4)]
 for c in pilots:c["id"]="pilot_"+c["id"];c["group"]=c["id"]
 manifest=dict(cases=cases,pilots=pilots,source_nonplanar="Kira original paper arXiv:1705.05610, topology topo4, massless limit",pilot_overlap="Symbolic feasibility pilots use subsets of final targets; weights and thresholds stay frozen and no policy is selected from these results.")
 for directory in ["scattering_families","symbolic_kinematics"]:
  subset=[c for c in cases if bool(c["definition"]["invariants"])==(directory=="symbolic_kinematics")]
  (HERE/directory/"families.json").write_text(json.dumps(subset,indent=2)+"\n")
 (HERE/"cases.json").write_text(json.dumps(manifest,indent=2)+"\n")
 print(json.dumps(dict(cases=len(cases),pilots=len(pilots),basis_ranks=[c["audit"]["rank"] for c in cases])))
if __name__=="__main__":main()
