"""Freeze target-shape deployment from confirmation costs before a fresh test."""
from s00_common import *
def pattern(c):
 return [max(sum(max(0,a-1) for a in t) for t in c['targets']),max(sum(max(0,-a) for a in t) for t in c['targets'])]
def main():
 out=HERE/'trained_model/deployment.json'
 if out.exists():return
 cfg=read(HERE/'trained_model/fixed.json');confirm=read(HERE/'confirmation/selection.json');cases={c['id']:c for c in make(1113,'validation')};rules=[]
 for group,record in confirm['records'].items():
  if not record['valid'] or not record['enabled']:continue
  for row in record['individual']:
   t=row['medians'];c=cases[row['case']]
   if t['learned']<.97*t['fixed'] and t['learned']<.97*t['previous']:
    rules.append(dict(signature=inputs.signature(c),pattern=pattern(c),graph=group,model_file=cfg['domains'][inputs.signature(c)]['model_file'],validation_case=c['id'],learned_over_fixed=t['learned']/t['fixed'],learned_over_previous=t['learned']/t['previous']))
 write(out,dict(complete=True,rules=rules,confirmation_sha256=inputs.sha(HERE/'confirmation/selection.json'),fixed_sha256=inputs.sha(HERE/'trained_model/fixed.json'),source='Confirmation profile only. Require three percent gain against both fixed and previous for a target-complexity pattern.',reserved_profile=1151))
 print('DEPLOYMENT_PATTERNS',len(rules),flush=True)
if __name__=='__main__':main()
