"""Resolve reference bases and freeze the development-selected algebra actions."""
from s00_reconstruction_common import *
from s20_reference import repair_pilot
from s10_cases import cases
from fractions import Fraction

def main():
 assert os.environ.get('JOB_ID')
 for name in ['pilot_complete','bunch_pilot_complete','structure_pilot_complete']:
  assert read(HERE/(name+'.json'))['complete']
 assert read(HERE/'bunch_pilot_complete.json').get('bunch_sizes')==[1,2,4,8,16]
 assert read(HERE/'structure_pilot_complete.json').get('bunch_sizes')==[1,2,4,8,16]
 if not (HERE/'pilot_basis_checks.json').exists():repair_pilot()
 checks=read(HERE/'pilot_basis_checks.json')
 assert all(v['reference_success'] and all(x['verified'] for x in v['checks']) for v in checks['checks'].values())
 sets={}
 kinematic_checks=0
 for phase in ['training','validation','reserved']:
  cs=cases(phase)
  for c in cs:
   if c['topology_group'] not in ['double_box','nonplanar_box']:continue
   orientation=1 if c['topology_group']=='double_box' else -1
   g={tuple(pair):Fraction(value) for pair,value in c['definition']['scalarproduct_rules']}
   assert all(g[(p,p)]==0 for p in ['p1','p2','p3'])
   assert g[('p1','p2')]+orientation*(g[('p1','p3')]+g[('p2','p3')])==0
   params=c['definition']['parameters'];values=params.get('values',params)
   assert Fraction(values['s'])==2*g[('p1','p2')]
   assert Fraction(values['t'])==2*orientation*g[('p1','p3')]
   kinematic_checks+=1
  sets[phase]={json.dumps([c['definition'],c['targets']],sort_keys=True) for c in cs}
  assert len(sets[phase])==len(cs)
 for a in sets:
  for b in sets:
   if a!=b:assert not sets[a]&sets[b]
 cfg=dict(actions=['previous']+['firefly'+str(b) for b in [1,2,4,8,16]],settings={'previous':['previous',1],**{'firefly'+str(b):['firefly',b] for b in [1,2,4,8,16]}},deadline=50,selection_reason='Full reconstruction beats reconstructed back-substitution on all four original development batches. Retain symbolic algebra and five finite-field evaluation batch sizes for cost training.',split_counts={p:len(v) for p,v in sets.items()},split_rule='Different complete physical inputs in every split. The high-rank box batches also have disjoint index sets. Low-rank and raised-power shapes recur at distinct kinematic points.',cases_source_sha256=sha(HERE/'s10_cases.py'))
 write(HERE/'actions.json',cfg)
 write(HERE/'kinematic_checks.json',dict(complete=True,checked_inputs=kinematic_checks,conditions=['Three listed external legs are massless.','The fourth leg is massless in the stated momentum convention.','Invariant metadata agree with the scalar-product rules.'],cases_source_sha256=sha(HERE/'s10_cases.py')))
 print('algebra actions frozen',cfg['actions'],cfg['split_counts'],flush=True)
if __name__=='__main__':main()
