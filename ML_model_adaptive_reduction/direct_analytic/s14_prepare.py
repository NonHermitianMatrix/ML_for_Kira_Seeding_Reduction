"""Freeze formulas, model, and held-out physical requests before testing."""
from s00_direct_common import *
from s03_cases import cases as native_cases
from s07_exact_cases import cases as exact_cases,vacuum,massless_vacuum
import hashlib

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert read(HERE/'checks.json')['complete'] and read(HERE/'trained_model/policy.json')['complete']
 sets={p:{tuple(sorted(map(tuple,c['targets']))) for c in native_cases(p)} for p in ['development','training','validation','reserved']}
 for a in sets:
  for b in sets:
   if a!=b:assert not sets[a]&sets[b]
 p=dict(cases=exact_cases()+native_cases('reserved'),extended_cases=[vacuum(L,23511+L,True) for L in range(1,14)]+[massless_vacuum(L) for L in range(1,14)],repetitions=3,seconds_per_application=30,source_sha256={f.name:sha(f) for f in HERE.glob('s*.py') if int(f.name[1:3])<=17},model_sha256=sha(HERE/'trained_model/policy.json'),prior_commit='250d88aabb9d622b87f0f9bffdd2dc64f0fa12b7',previous_entry_sha256=sha(PRIOR/'s05_runtime.py'))
 write(HERE/'protocol.json.gz',p);print('frozen',len(p['cases']),len(p['extended_cases']),flush=True)
if __name__=='__main__':main()
