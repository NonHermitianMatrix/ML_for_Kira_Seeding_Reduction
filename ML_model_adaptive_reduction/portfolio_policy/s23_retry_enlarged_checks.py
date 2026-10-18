"""Retry timed-out enlarged checks without changing the reference criterion."""
from s00_common import *

def main():
 code=(HERE/'s07_sector_checks.py').read_text().replace('timeout=60,margin=0','timeout=180 if check else 60,margin=0')
 g=dict(__name__='extended_check',__file__=str(HERE/'s07_sector_checks.py'));exec(compile(code,str(HERE/'s07_sector_checks.py'),'exec'),g);attempt=g['attempt']
 protocol=read(HERE/'integration/protocol.json');cases={c['id']:c for c in protocol['cases']};selected=[]
 for marker in (HERE/'integration/results').glob('*.json'):
  r=read(marker)
  if r['status']!='new_check_failed':continue
  ref=HERE/'integration/references'/(r['case']+'.json.gz');cp=ref.with_name(ref.stem+'_check.json.gz')
  if read(cp).get('status')=='time_limit':selected.append(r['case'])
 write(HERE/'integration/extended_check_protocol.json',dict(cases=selected,check_timeout_seconds=180,unchanged='Increased numerator bound, ordering two, and exact comparison with the original reference. Native and bounded application comparisons keep the original 60-second budget.'))
 for name in selected:
  c=cases[name];ref=HERE/'integration/references'/(name+'.json.gz');cp=ref.with_name(ref.stem+'_check.json.gz');marker=HERE/'integration/results'/(name+'.json');previous=read(cp)
  write(HERE/'integration/initial_check_failures'/(name+'.json.gz'),previous)
  result=attempt(c,read(ref)['masters'],True,True,ref);result['extended_check_budget_seconds']=180;write(cp,result)
  print('ENLARGED_CHECK',name,result['success'],result.get('status'),flush=True)
  if not result['success']:
   r=read(marker);r.update(extended_check_budget_seconds=180,extended_check_status=result.get('status'));write(marker,r);continue
  methods={False:[],True:[]};failed=set()
  for rep in range(3):
   for opt in ([False,True] if rep%2==0 else [True,False]):
    if opt in failed:continue
    r=attempt(c,read(ref)['masters'],False,opt,ref);write(HERE/'integration/model_test'/(name+'_'+str(int(opt))+'_'+str(rep)+'.json.gz'),r);methods[opt].append(r['complete_seconds'])
    if not r['success']:failed.add(opt)
  write(marker,dict(case=name,status='verified' if not failed else 'control_failed',failed_methods=list(failed),times={str(k):v for k,v in methods.items()},loops=len(c['definition']['loop_momenta']),indices=len(c['definition']['propagators']),extended_check_budget_seconds=180))
 write(HERE/'integration/extended_checks_complete.json',dict(complete=True,cases=len(selected)))
if __name__=='__main__':main()
