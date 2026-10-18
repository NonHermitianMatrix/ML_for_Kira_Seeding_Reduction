"""Deploy exact storage changes only in their checked physical domains."""
from s00_common import *
import statistics

def main():
 rules=[];cases={}
 for folder,width in [('integration',64),('wide_integration',128)]:
  protocol=read(HERE/folder/'protocol.json');byid={c['id']:c for c in protocol['cases']}
  for p in (HERE/folder/'results').glob('*.json'):
   result=read(p);c=byid[result['case']];L=len(c['definition']['loop_momenta']);measure={}
   for opt in [False,True]:
    rs=[read(q) for q in (HERE/folder/'model_test').glob(c['id']+'_'+str(int(opt))+'_*.json.gz')]
    if len(rs)==3 and all(r['success'] and r.get('reference_checked') for r in rs):measure[opt]=statistics.median(r['complete_seconds'] for r in rs)
   if True not in measure:continue
   if width==64:
    if False not in measure or measure[True]>=.97*measure[False]:continue
    bounded=True
   else:
    if L<5:continue
    bounded=False not in measure or measure[True]<measure[False]
   signature=inputs.signature(c);rules=[r for r in rules if r['signature']!=signature]
   rules.append(dict(signature=signature,width=width,bounded=bounded,validation_case=c['id'],folder=folder,reference=str(HERE/folder/'references'/(c['id']+'.json.gz')),times={str(k):v for k,v in measure.items()}));cases[c['id']]=c
 policy=HERE/'integration/deployment.json';write(policy,dict(complete=True,rules=rules,source='Checked exact validation comparisons. Low-loop bounded storage needs a three-percent gain; higher-loop wide weights require exact completion.'))
 app=module('storage_application_check',HERE/'s13_optimized.py');valid=[]
 for rule in rules:
  c=cases[rule['validation_case']];ref=Path(rule['reference'])
  try:r=app.reduce(c,read(ref)['masters'],'application',ref)
  except Exception as error:r=dict(success=False,error=str(error))
  write(HERE/'integration/application_checks'/(c['id']+'.json.gz'),r)
  if r['success'] and r.get('reference_checked'):valid.append(rule)
  print('EXACT_ROUTE',c['id'],r['success'],flush=True)
 write(policy,dict(complete=True,rules=valid,rejected_validation_routes=[r['validation_case'] for r in rules if r not in valid],source='Checked exact validation comparisons and complete application checks.'))
 write(HERE/'integration/application_completion.json',dict(complete=True,routes=len(valid),checked=len(rules)))
if __name__=='__main__':main()
