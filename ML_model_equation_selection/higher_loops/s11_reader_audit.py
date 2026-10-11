"""Cross-check a fast exact coefficient reader against symbolic algebra."""
import gzip,hashlib,time
from s00_math import *
from s10_polynomial import parse
def main():
 examples=set()
 for p in (HERE/"objects").glob("*.json.gz"):
  obj=json.loads(gzip.decompress(p.read_bytes()))
  for line in obj.get("raw_export","").splitlines():
   if line.strip():
    s=line.split("*(",1)[1][:-1]
    if s!="-1":examples.add(s)
 assert examples
 fast={};start=time.perf_counter()
 for s in sorted(examples):fast[s]=canonical(parse(s,"z"))
 fast_time=time.perf_counter()-start
 start=time.perf_counter()
 for s in sorted(examples):assert fast[s]==canonical(rational_polynomial(s,"z")),s
 slow_time=time.perf_counter()-start
 checks={"(z^2-1)/(z-1)":[F(1),F(1)],"(3*z+1)/6":[F(1,6),F(1,2)],"0":[], "z^0":[F(1)],"-(-z)":[F(0),F(1)]}
 for s,expected in checks.items():assert parse(s,"z")==expected
 rejected=0
 for s in ["1/(z-1)","1/0","unexpected+1","__import__('os')","z^1000"]:
  try:parse(s,"z")
  except (AssertionError,ValueError,SyntaxError,ZeroDivisionError):rejected+=1
  else:raise AssertionError(s)
 write(HERE/"validation/reader_audit.json",dict(all_passed=True,distinct_coefficients=len(examples),special_cases=len(checks),rejected_unsupported=rejected,fast_seconds=fast_time,symbolic_seconds=slow_time,parser_sha256=hashlib.sha256((HERE/"s10_polynomial.py").read_bytes()).hexdigest(),examples_sha256=hashlib.sha256(json.dumps(sorted(examples)).encode()).hexdigest()))
 print(json.dumps(dict(reader_exact=True,coefficients=len(examples),fast_seconds=fast_time,symbolic_seconds=slow_time)),flush=True)
if __name__=="__main__":main()
