"""Confirm proposed learned gains on an additional validation profile."""
from s02_collect import *
import statistics

def confirm():
 start=time.perf_counter();cfg=read(HERE/'trained_model/fixed.json');rows=[];cases=make(1113,'validation');records={}
 for signature,entry in cfg['domains'].items():
  if not entry['enabled']:continue
  cs=[c for c in cases if inputs.signature(c)==signature];totals={m:0. for m in ['fixed','learned','previous']};individual=[];valid=True
  for c in cs:
   ref=reference(c)
   if ref is None:valid=False;continue
   basis=read(ref)['masters'];times={m:[] for m in totals}
   for rep in range(3):
    ms=list(totals);shift=(sum(c['id'].encode())+rep)%3
    for m in ms[shift:]+ms[:shift]:
     r=call(c,m,HERE/'confirmation'/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz'),basis,ref)
     valid=valid and r['success'];times[m].append(r['complete_seconds'])
   medians={m:statistics.median(v) for m,v in times.items()};individual.append(dict(case=c['id'],medians=medians));rows.append(c['id'])
   for m,v in medians.items():totals[m]+=v
  retained=valid and len(individual)==2 and totals['learned']<.97*totals['fixed'] and all(r['medians']['learned']<=1.03*r['medians']['fixed'] for r in individual)
  entry['enabled']=retained;selected=totals['learned'] if retained else totals['fixed'];entry['deploy']=valid and len(individual)==2 and selected<.97*totals['previous']
  entry['confirmation_ratio']=totals['learned']/totals['fixed'] if totals['fixed'] else None
  records[entry['graph']]=dict(valid=valid,enabled=retained,deploy=entry['deploy'],totals=totals,individual=individual)
 write(HERE/'trained_model/fixed.json',cfg);write(HERE/'confirmation/selection.json',dict(complete=True,records=records,cases=rows,seconds=time.perf_counter()-start,condition='At least three percent summed improvement and no target-shape median more than three percent slower than fixed.'))
 return rows,time.perf_counter()-start
if __name__=='__main__':confirm()
