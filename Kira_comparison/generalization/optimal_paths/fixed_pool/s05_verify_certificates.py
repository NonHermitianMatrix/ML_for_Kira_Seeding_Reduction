"""Check every certificate edge independently using exact symbolic matrices."""
import gzip,json,pathlib
import sympy as sp
HERE=pathlib.Path(__file__).resolve().parent
def verify(p):
 with gzip.open(p,"rt") as f:r=json.load(f)
 local={x:sp.Symbol(x) for x in r["symbols"]};nodes=r["nodes"];n=len(r["columns"])-1
 matrices=[sp.Matrix([[sp.sympify(x,locals=local) for x in row] for row in node["matrix"]]) for node in nodes]
 expected=sp.Matrix([sp.sympify(v,locals=local) for v in r["expected_coefficients"]]);edges=0;leaves=0
 for idx,node in enumerate(nodes):
  A=matrices[idx];remaining=node["remaining"];k=n-len(remaining)
  assert all(sp.cancel(v)==0 for v in A*expected)
  if not remaining:
   assert node["optimum"]==0 and node["path_count"]==1
   leaves+=1
   for c in range(n):
    hits=[i for i in range(k) if A[i,c]!=0]
    assert len(hits)==1 and A[hits[0],c]==1
    assert sp.cancel(-A[hits[0],n]-expected[c])==0
   continue
  possible={(i,c) for i in range(k,A.rows) for c in remaining if A[i,c]!=0}
  assert possible=={(a["row"],a["column"]) for a in node["actions"]}
  for a in node["actions"]:
   B=A.copy();B.row_swap(k,a["row"]);c=a["column"];pivot=B[k,c]
   support=[j for j in range(B.cols) if j!=c and B[k,j]!=0]
   cost=len(support) if pivot!=1 else 0
   B[k,:]=B[k,:]/pivot
   for i in range(B.rows):
    if i==k or B[i,c]==0:continue
    cost+=2*len(support);B[i,:]=B[i,:]-B[i,c]*B[k,:]
   child=nodes[a["child"]]
   assert cost==a["cost"]
   assert child["remaining"]==[j for j in remaining if j!=c]
   assert all(sp.cancel(v)==0 for v in B-matrices[a["child"]])
   assert a["total"]==cost+child["optimum"];edges+=1
  assert node["optimum"]==min(a["total"] for a in node["actions"])
  assert node["path_count"]==sum(nodes[a["child"]]["path_count"] for a in node["actions"])
 assert r["paths"]["optimal"]["cost"]==nodes[r["root"]]["optimum"]
 return dict(system=r["system"],all_edges_verified=edges,terminal_states_verified=leaves,
  minimum_cost=nodes[r["root"]]["optimum"],all_actions_enumerated=True,exact_symbolic_residuals_zero=True)
def main():
 results=[verify(p) for p in [HERE/"optimal_paths"/(name+".json.gz") for name in ["massless_bubble","massive_tadpole"]]]
 assert len(results)==2
 (HERE/"optimal_paths/verification.json").write_text(json.dumps(dict(success=True,systems=results),indent=2)+"\n")
 print(json.dumps(results),flush=True)
if __name__=="__main__":main()
