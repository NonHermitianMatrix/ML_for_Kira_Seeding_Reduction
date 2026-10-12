"""Certify minimum counted field operations over every admissible finite pivot path."""
import gzip,hashlib,itertools,json,math,pathlib,time
from functools import lru_cache
import sympy as sp
HERE=pathlib.Path(__file__).resolve().parent
d,s,m2=sp.symbols("d s m2")
def systems():
 # D1=l^2, D2=(l-p)^2, p^2=s. Zero-index massless tadpoles vanish.
 yield dict(name="massless_bubble",symbols=[d,s],columns=["B(2,1)","B(1,2)","B(2,2)","B(1,1)"],
  rows=[[0,s,0,d-3],[s,0,0,d-3],[d-5,-1,s,0],[-1,d-5,s,0]],
  seeds=["(1,1)","(1,1)","(2,1)","(1,2)"],operators=["l","l-p","l","l-p"],
  expected=[(3-d)/s,(3-d)/s,(d-6)*(d-3)/s**2,1])
 # D=l^2-m2. Each identity is (d-2a)T(a)-2*a*m2*T(a+1)=0.
 yield dict(name="massive_tadpole",symbols=[d,m2],columns=["T(2)","T(3)","T(4)","T(1)"],
  rows=[[-2*m2,0,0,d-2],[d-4,-4*m2,0,0],[0,d-6,-6*m2,0]],
  seeds=["1","2","3"],operators=["l"]*3,
  expected=[(d-2)/(2*m2),(d-2)*(d-4)/(8*m2**2),(d-2)*(d-4)*(d-6)/(48*m2**3),1])
def certificate(system):
 started=time.perf_counter();K=sp.QQ.frac_field(*system["symbols"])
 rows=tuple(tuple(K.from_sympy(sp.sympify(v)) for v in row) for row in system["rows"])
 n=len(rows[0])-1;one=K.one;zero=K.zero;nodes=[];indices={};paths={}
 def encode(a):return [[str(v) for v in r] for r in a]
 def move(a,remaining,i,j):
  k=n-len(remaining);b=[list(r) for r in a];b[k],b[i]=b[i],b[k];pivot=b[k][j]
  support=[c for c,v in enumerate(b[k]) if c!=j and v]
  divisions=len(support) if pivot!=one else 0
  for c in support:b[k][c]/=pivot
  b[k][j]=one;updates=0
  for r in range(len(b)):
   if r==k or not b[r][j]:continue
   factor=b[r][j]
   for c in support:b[r][c]-=factor*b[k][c];updates+=1
   b[r][j]=zero
  return tuple(tuple(r) for r in b),tuple(c for c in remaining if c!=j),divisions+2*updates
 def visit(a,remaining):
  key=(a,remaining)
  if key in indices:return indices[key]
  assert len(nodes)<10000,"Bounded certificate exceeds node cap"
  assert time.perf_counter()-started<180,"Certificate time cap"
  idx=len(nodes);indices[key]=idx
  node=dict(id=idx,matrix=encode(a),remaining=list(remaining),actions=[])
  nodes.append(node)
  if not remaining:
   node.update(optimum=0,path_count=1);return idx
  k=n-len(remaining)
  for i in range(k,len(a)):
   for j in remaining:
    if not a[i][j]:continue
    b,cols,cost=move(a,remaining,i,j);child=visit(b,cols)
    node["actions"].append(dict(row=i,column=j,cost=cost,child=child,total=cost+nodes[child]["optimum"]))
  assert node["actions"]
  node["optimum"]=min(x["total"] for x in node["actions"])
  node["path_count"]=sum(nodes[x["child"]]["path_count"] for x in node["actions"])
  return idx
 root=visit(rows,tuple(range(n)))
 def trace(kind,start=root):
  idx=start;cost=0;path=[]
  while nodes[idx]["remaining"]:
   actions=nodes[idx]["actions"]
   if kind=="optimal":a=min(actions,key=lambda a:(a["total"],a["column"],a["row"]))
   elif kind=="fixed":a=min(actions,key=lambda a:(a["column"],a["row"]))
   elif kind=="greedy":a=min(actions,key=lambda a:(a["cost"],a["column"],a["row"]))
   path.append(dict(state=idx,**a));cost+=a["cost"];idx=a["child"]
  return dict(cost=cost,path=path,final=idx)
 expected=sp.Matrix(system["expected"])
 assert sp.simplify(sp.Matrix(system["rows"])*expected)==sp.zeros(len(rows),1)
 # Gamma-function ratios give an independent check of the bubble coefficients.
 if system["name"]=="massless_bubble":
  for (a,b),v in zip([(2,1),(1,2),(2,2)],system["expected"]):
   gamma_ratio=s**(2-a-b)*sp.rf(2-d/2,a+b-2)*sp.rf(d-a-b,a+b-2)/(sp.factorial(a-1)*sp.factorial(b-1)*sp.rf(d/2-a,a-1)*sp.rf(d/2-b,b-1))
   assert sp.cancel(gamma_ratio-v)==0
 # Exact subset ranks certify how many source rows and distinct seeds suffice.
 subsets=[]
 for mask in range(1<<len(rows)):
  ids=[i for i in range(len(rows)) if mask>>i&1]
  rank=sp.Matrix([system["rows"][i][:-1] for i in ids]).rank() if ids else 0
  subsets.append(dict(rows=ids,seeds=sorted(set(system["seeds"][i] for i in ids)),rank=rank,sufficient=rank==n))
 sufficient=[x for x in subsets if x["sufficient"]]
 subset_roots=[]
 for subset in sufficient:
  selected=tuple(rows[i] for i in subset["rows"])
  sid=visit(selected,tuple(range(n)))
  subset_roots.append(dict(rows=subset["rows"],seeds=subset["seeds"],root=sid,optimum=nodes[sid]["optimum"],path_count=nodes[sid]["path_count"]))
 best=min(subset_roots,key=lambda x:(x["optimum"],len(x["rows"]),len(x["seeds"]),x["rows"]))
 joint=dict(minimum_cost=best["optimum"],selected_rows=best["rows"],selected_seeds=best["seeds"],
  path=trace("optimal",best["root"]),all_sufficient_subsets=subset_roots,
  complete_path_count=sum(x["path_count"] for x in subset_roots),
  initial_selection_cost=0,scope="Select any sufficient subset of the original source pool, then use the stated Gauss-Jordan actions. Selection and certificate-search cost are excluded from the field-operation objective.")
 result=dict(joint_optimum=joint,system=system["name"],symbols=list(map(str,system["symbols"])),columns=system["columns"],
  original_rows=[[str(x) for x in r] for r in system["rows"]],seeds=system["seeds"],operators=system["operators"],
  expected_coefficients=list(map(str,system["expected"])),coefficient_field="Q("+",".join(map(str,system["symbols"]))+")",
  allowed_actions="Choose any nonzero active nonmaster column in any unprocessed row; swap into next pivot row; normalize; remove the pivot from every other row. Protect the last master column.",
  cost="One division for each nonpivot nonzero source entry when the pivot differs from one; one multiplication and one subtraction for every updated nonpivot source entry. Assignments, pivot cancellation, comparisons and polynomial internal work are excluded.",
  objective="Reduce all three nonmaster integrals. No new equations or row combinations outside the stated Gauss-Jordan actions may be introduced.",
  nodes=nodes,root=root,paths={name:trace(name) for name in ["optimal","fixed","greedy"]},
  all_subsets=subsets,minimum_equations=min(len(x["rows"]) for x in sufficient),
  minimum_seeds=min(len(x["seeds"]) for x in sufficient),states=len(nodes),complete_path_count=nodes[root]["path_count"],
  seconds=time.perf_counter()-started,source_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest())
 p=HERE/"optimal_paths"/(system["name"]+".json.gz")
 with gzip.open(p,"wt",compresslevel=9) as f:json.dump(result,f,separators=(",",":"))
 print(json.dumps({k:result[k] for k in ["system","states","complete_path_count","minimum_equations","minimum_seeds","seconds"]}|{"costs":{k:v["cost"] for k,v in result["paths"].items()}}),flush=True)
 return result
def main():
 summaries=[]
 for system in systems():
  r=certificate(system);summaries.append({k:v for k,v in r.items() if k not in ("nodes","all_subsets")})
 (HERE/"optimal_paths/summary.json").write_text(json.dumps(summaries,indent=2)+"\n")
if __name__=="__main__":main()
