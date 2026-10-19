"""Check identities, fit the model, then freeze all reserved comparisons."""
from s00_vac_common import *
from s04_cases import native_cases,vacuum_case

def main():
 from s08_train import main as train
 from s09_checks import main as check
 train();check();cases=[]
 for L in range(1,14):
  shapes=['star'] if L<3 else ['star','chain'] if L==3 else ['star','chain','branched']
  for shape in shapes:
   c=vacuum_case(L,shape,6053);c['test_group']='vacuum';cases.append(c)
 cases.extend(dict(c,test_group='native') for c in native_cases('reserved'))
 # Exact path regression checks do not enter fitting.
 m=load('vac_prop_cases',PRIOR/'s03_prop_cases.py')
 for L in [1,3,7,13]:
  c=m.case(L,'chain',6059);c['test_group']='propagator';cases.append(c)
 q=ROOT/'ML_model_adaptive_reduction/loop_coverage13';m=load('vac_triangle_cases',q/'s03_cases.py')
 for L in [1,3,7,13]:
  c=m.tree_case(L,'chain',6067,True);c['test_group']='triangle';cases.append(c)
 write(HERE/'protocol.json.gz',dict(complete=True,repetitions=3,seconds_per_application=18,cases=cases,
  source_sha256={p.name:sha(p) for p in HERE.glob('s*.py') if int(p.name[1:3])<=12},
  model_sha256=sha(HERE/'trained_model/policy.json'),fixed_sha256=sha(HERE/'trained_model/fixed.json'),
  prior_model_sha256=sha(BATCH/'trained_model/policy.json'),prior_entry_sha256=sha(PRIOR/'s02_runtime.py'),
  objective='All complete fresh process costs; external comparison checks are outside both timers; retain failures and verify returned exact coefficients.'))
 print(json.dumps(dict(frozen=True,requests=len(cases),model_enabled=read(HERE/'trained_model/policy.json')['enabled'])),flush=True)
if __name__=='__main__':main()
