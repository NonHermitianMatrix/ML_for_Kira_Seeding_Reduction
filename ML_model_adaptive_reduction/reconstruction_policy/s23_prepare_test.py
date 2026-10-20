"""Freeze the deployed method and reserve tests before measuring outcomes."""
from s00_reconstruction_common import *
from s10_cases import cases

def main():
 assert read(HERE/'training_summary.json')['complete']
 policy=read(HERE/'trained_model/policy.json')
 checked=read(HERE/'entry_checks.json');assert checked['complete']
 assert all(sha(HERE/n)==digest for n,digest in checked['source_sha256'].items())
 assert all(sha(HERE/'trained_model'/n)==digest for n,digest in checked['model_sha256'].items())
 assert policy['cases_source_sha256']==sha(HERE/'s10_cases.py')
 assert policy['actions_sha256']==sha(HERE/'actions.json')
 exact=[c for c in read(PREVIOUS/'final_protocol.json.gz')['cases'] if c['test_group']!='native']
 test=cases('reserved')+exact
 model_files=['policy.json','fixed.json','deployment.json']
 protocol=dict(cases=test,repetitions=3,methods=['before_formulas','previous','integrated','fixed'],seconds_per_application=90,prior_commit=PREVIOUS_COMMIT,analytic_predecessor_commit='250d88aabb9d622b87f0f9bffdd2dc64f0fa12b7',source_sha256={f.name:sha(f) for f in HERE.glob('s*.py') if int(f.name[1:3])<=24},model_sha256={n:sha(HERE/'trained_model'/n) for n in model_files},binary_sha256=sha(TOOLS/'kira'),preceding_binary_sha256=sha(ROOT/'.tools/kira-sector-wide/kira'),exact_grid='Previously verified analytic regression inputs, unchanged and excluded from model training.',native_grid='Fresh complete physical inputs from the reserved split.',control='The fixed comparator uses a separately chosen setting for each propagator structure and loads no new model weights. The preceding native seed policy is shared. The before_formulas control also removes the preceding direct analytic additions, allowing a matched cumulative comparison.')
 write(HERE/'test_protocol.json.gz',protocol)
 print('test frozen',len(test),'requests,',len(test)-len(exact),'fresh native requests',flush=True)
if __name__=='__main__':main()
