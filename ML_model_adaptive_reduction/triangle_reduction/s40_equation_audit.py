"""Explain the rejected equation-filter attempts from preserved native records."""
from s00_triangle_common import *
def main():
 counts={};candidates=skipped=0
 for f in (HERE/'equation_validation').glob('*.json.gz'):
  for z in read(f)['results']['on']:
   for b in z.get('blocks',[]):
    for a in b['result'].get('attempts',[]):
     if not a.get('added_equation_filter'):continue
     reason='additional masters' if 'found additional master integrals' in a.get('log_tail','') else a.get('status')
     counts[reason]=counts.get(reason,0)+1;e=a.get('equation_metrics',{});candidates+=e.get('candidate_calls',0);skipped+=e.get('construction_skipped_calls',0)
 write(HERE/'equation_failure_analysis.json',dict(attempts_by_reason=counts,candidate_calls=candidates,construction_skipped_calls=skipped))
 assert counts=={'additional masters':10}
 print('Equation filter: ten prescribed-basis failures; skipped',skipped,'of',candidates,'candidate calls',flush=True)
if __name__=='__main__':main()
