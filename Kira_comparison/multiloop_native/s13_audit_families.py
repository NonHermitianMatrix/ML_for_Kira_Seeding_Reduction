"""Check that denominators span the independent loop scalar products."""
import json,pathlib
import sympy as sp
HERE=pathlib.Path(__file__).resolve().parent
def audit():
 results=[]
 for c in json.loads((HERE/"families.json").read_text())["cases"]:
  d=c["definition"];loops=d["loop_momenta"];external=d["external_momenta"];names=loops+external
  syms={n:sp.Symbol(n) for n in names};N=len(loops);E=len(external)
  products=[(i,j) for i in range(N) for j in range(i,N+E)]
  rows=[]
  for p in d["propagators"]:
   q=sp.sympify(p["momentum"],locals=syms);co=[q.coeff(syms[n]) for n in names]
   assert sp.expand(q-sum(v*syms[n] for v,n in zip(co,names)))==0
   rows.append([co[i]*co[j]*(1 if i==j else 2) for i,j in products])
  matrix=sp.Matrix(rows);rank=matrix.rank();required=N*(N+1)//2+N*E
  assert rank==required==len(rows),(c["id"],rank,required)
  gram=sp.zeros(E)
  for (a,b),value in d["scalarproduct_rules"]:
   if a in external and b in external:gram[external.index(a),external.index(b)]=gram[external.index(b),external.index(a)]=sp.sympify(value,rational=True)
  det=gram.det() if E else sp.Integer(1);assert det!=0
  results.append(dict(case=c["id"],loop_scalar_product_count=required,denominator_rank=rank,
   external_gram_determinant=str(det),squared_momentum_matrix=[[str(v) for v in row] for row in rows]))
 p=HERE/"family_audit.json";p.write_text(json.dumps(dict(cases=results,all_passed=True),indent=2)+"\n")
 print("All physical denominator bases have full rank",flush=True)
if __name__=="__main__":audit()
