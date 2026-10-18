"""Audit new formulas against saved native coefficients, without native work."""
from s00_common import *
from s09_extension import exact_cases,EXT
import s07_exact_vacuum as vacuum

def main():
 rows=[]
 for c in exact_cases():
  t=time.perf_counter();a=vacuum.reduce(c);b=vacuum.reduce(c,reference=True);assert a is not None and b is not None,c['id']
  ok,n=equal(a['coefficients'],b['coefficients']);assert ok,(c['id'],a,b)
  rows.append(dict(case=c['id'],gamma_checks=n,seconds=time.perf_counter()-t));print(json.dumps(rows[-1]),flush=True)
 saved=[]
 for c in READ(HERE/'protocol.json')['cases']:
  if c.get('topology_group','').startswith('vacuum_one_mass_L') and 2<=len(c['definition']['loop_momenta'])<=4:
   p=HERE/'references'/(c['id']+'.json.gz')
   if not p.exists():continue
   ref=READ(p)
   if not ref['success']:continue
   out=vacuum.reduce(c);assert out is not None
   ok,n=equal(out['coefficients'],ref['blocks'][0]['result']['coefficients']);assert ok,(c['id'],out,ref)
   saved.append(dict(case=c['id'],checks=n,reference_sha256=sha(p)));print(json.dumps(saved[-1]),flush=True)
 write(EXT/'formula_audit.json',dict(complete=True,gamma=rows,saved_native=saved,source_sha256=sha(HERE/'s07_exact_vacuum.py')))
if __name__=='__main__':main()
