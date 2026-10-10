"""Verify modular values and row-cancellation estimates against exact SymPy arithmetic."""
import hashlib,json,math,pathlib,random,subprocess
import sympy as sp
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];D=sp.Symbol("d");P=2147483647
def main():
 rng=random.Random(1407)
 expressions=["-d^2","(-d)^2","(d+1)^(-2)","2*d+3/d","0","d^0","17^17","d/(d-17)","s+1","2^10001"]
 for i in range(200):
  a=sum(rng.randint(-9,9)*D**j for j in range(rng.randint(1,5)))
  b=sum(rng.randint(-9,9)*D**j for j in range(rng.randint(1,4))) or sp.Integer(1)
  expressions.append(str(a)+"/("+str(b)+")")
 expressions=[s.replace("**","^") for s in expressions]
 executable=ROOT/".tools/kira-runtime-modular/feature_test"
 proc=subprocess.run([str(executable)],input="\n".join(expressions+["@fixture"])+"\n",text=True,capture_output=True,check=True,timeout=15)
 lines=proc.stdout.splitlines();assert len(lines)==len(expressions)+1
 for s,line in zip(expressions,lines):
  valid,*values=map(int,line.split())
  if s in ["s+1","2^10001"]:assert not valid;continue
  expr=sp.sympify(s.replace("^","**"),locals={"d":D},rational=True)
  expected=[];ok=True
  for d in [17,19]:
   x=expr.subs(D,d)
   if x.has(sp.zoo,sp.nan,sp.oo):ok=False;break
   n,z=sp.fraction(x);n=int(n)%P;z=int(z)%P
   if z==0:ok=False;break
   expected.append(n*pow(z,P-2,P)%P)
  assert bool(valid)==ok,(s,line,expected)
  if ok:assert values==expected,(s,values,expected)
 rows=[{5:D,4:2*D,3:D+1},{5:sp.Integer(1),4:sp.Integer(2),2:sp.Integer(1)},{5:D+1,3:sp.Integer(2),2:D}]
 expected=[]
 for q,source in enumerate(rows):
  sizes=[];total_union=0;cancelled=0
  for j,dest in enumerate(rows):
   if j==q:continue
   keys=(set(source)|set(dest))-{5};total_union+=len(keys)
   after={k:sp.expand(dest.get(k,0)*source[5]-source.get(k,0)*dest[5]) for k in keys}
   size=sum(x!=0 for x in after.values());sizes.append(size);cancelled+=len(keys)-size
  expected.append([math.log1p(sum(sizes)),cancelled/total_union,math.log1p(max(sizes)),math.log1p(sizes.count(0)),math.log1p(sum(n*n for n in sizes)),1.])
 actual=json.loads(lines[-1])
 assert all(abs(a-b)<1e-12 for row,want in zip(actual,expected) for a,b in zip(row,want))
 result=dict(all_passed=True,coefficient_expressions=len(expressions),dimension_samples=[17,19],prime=P,exact_row_candidates=3,header_sha256=hashlib.sha256((HERE/"s01_modular_features.h").read_bytes()).hexdigest())
 (HERE/"feature_tests.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result),flush=True)
if __name__=="__main__":main()
