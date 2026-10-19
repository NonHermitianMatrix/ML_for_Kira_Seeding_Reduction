"""Validate complete learned cost, freeze deployment, then test fresh requests."""
from s00_batch_common import *
from s03_cases import batches,reserved
from s04_measure import measured,prepare
import random

def interval(a,b,seed=3109):
 rng=random.Random(seed);ratios=[]
 for _ in range(1500):
  ix=[rng.randrange(len(a)) for _ in range(len(a))];ratios.append(sum(a[j] for j in ix)/sum(b[j] for j in ix))
 ratios.sort();return [ratios[int(.025*len(ratios))],ratios[int(.975*len(ratios))]]

def validate(worker):
 for i,c in enumerate(batches(3041,'application_validation')):
  if i%2!=worker:continue
  ref=prepare(c)
  for rep in range(3):
   for m in (['learned','fixed'] if (i+rep)%2 else ['fixed','learned']):
    r=measured(c,m,rep,ref,'application_validation');print(json.dumps(dict(case=c['id'],method=m,verified=r['independently_verified'],seconds=r['complete_process_and_check_seconds'])),flush=True)
 write(HERE/f'application_validation_{worker}_complete.json',dict(complete=True))

def admit():
 for worker in [0,1]:assert read(HERE/f'application_validation_{worker}_complete.json')['complete']
 totals={'learned':[],'fixed':[]};all_ok=True
 for c in batches(3041,'application_validation'):
  for m in totals:
   rs=[read(HERE/'application_validation'/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz')) for rep in range(3)];all_ok &= all(r['independently_verified'] for r in rs);totals[m].append(statistics.median(r['complete_process_and_check_seconds'] for r in rs))
 ratio=sum(totals['learned'])/sum(totals['fixed']);ci=interval(totals['learned'],totals['fixed']);model=read(HERE/'trained_model/initial_policy.json');enabled=model['enabled'] and all_ok and ratio<.98 and ci[1]<1
 receipt=dict(complete=True,enabled=bool(enabled),initial_model_enabled=model['enabled'],all_verified=all_ok,time_ratio=ratio,request_bootstrap_interval=ci,learned_seconds=sum(totals['learned']),fixed_seconds=sum(totals['fixed']))
 model['enabled']=bool(enabled);model['application_admission']=receipt;write(HERE/'trained_model/policy.json',model);write(HERE/'admission.json',receipt)
 old=legacy();p=dict(complete=True,parent_commit='14b53c579a8b5f54cbefda7db485dc0c657e166f',cases=reserved(),methods=['learned','fixed','all_fixed','previous_prepared','previous'],repetitions=3,source_sha256={q.name:sha(q) for q in HERE.glob('s0*.py')},model_sha256=sha(HERE/'trained_model/policy.json'),preceding_admission_sha256=sha(PREVIOUS/'deployment/admission.json'),preceding_model_sha256=sha(old.PREVIOUS/'trained_model/expert.json'),basis_sha256=sha(support.PRIOR/'basis_registry.json'),additional_basis_sha256=sha(HERE/'basis_registry.json'),scope='Two native two-loop scattering structures with fresh kinematics and new index batches; exact one-scale triangle blocks and their independent products through thirteen loops; separate compatibility requests. All new methods and previous_prepared receive the same checked master indices. The unmodified previous entry remains a separate practical control.')
 p['fixed_sha256']=sha(HERE/'trained_model/fixed.json');p['basis_validation_sha256']=sha(HERE/'basis_validation.json');p['basis_preparation_source_sha256']=sha(HERE/'s11_prepare_basis.py')
 p['native_binary_sha256']=sha(ROOT/'.tools/kira-sector-wide/kira');p['preceding_outer_model_sha256']=sha(old.PREVIOUS/'trained_model/freeze.json')
 p['benchmark_environment']=read(HERE/'benchmark_environment.json')
 p['application_validation_profile']=3041
 write(HERE/'protocol.json',p);print(json.dumps(receipt),flush=True)

def test(worker):
 p=read(HERE/'protocol.json');assert p['complete'] and sha(HERE/'trained_model/policy.json')==p['model_sha256'];assert all(sha(HERE/n)==digest for n,digest in p['source_sha256'].items());assert sha(HERE/'basis_registry.json')==p['additional_basis_sha256']
 assert sha(HERE/'trained_model/fixed.json')==p['fixed_sha256'];assert sha(HERE/'basis_validation.json')==p['basis_validation_sha256'];assert sha(HERE/'s11_prepare_basis.py')==p['basis_preparation_source_sha256']
 import platform
 assert platform.node().split('.')[0]==p['benchmark_environment']['host']
 cpu=next((line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name')),'unknown')
 write(HERE/f'test_worker_{worker}_environment.json',dict(host=platform.node(),cpu=cpu,python=sys.version,system=platform.platform(),allocated_cores=1,native_threads=1))
 for i,c in enumerate(p['cases']):
  if i%2!=worker:continue
  ref=prepare(c)
  for rep in range(p['repetitions']):
   methods=p['methods'];order=methods[(i+rep)%len(methods):]+methods[:(i+rep)%len(methods)]
   for method in order:
    if rep and not read(HERE/'model_test'/(c['id']+'_'+method+'_r0.json.gz'))['independently_verified']:continue
    r=measured(c,method,rep,ref,'model_test');print(json.dumps(dict(case=c['id'],method=method,rep=rep,verified=r['independently_verified'],seconds=r['complete_process_and_check_seconds'])),flush=True)
 write(HERE/f'test_{worker}_complete.json',dict(complete=True))
if __name__=='__main__':
 if sys.argv[1]=='admit':admit()
 elif sys.argv[1]=='validate':validate(int(sys.argv[2]))
 else:test(int(sys.argv[2]))
