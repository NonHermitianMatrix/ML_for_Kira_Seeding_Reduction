"""Summarize frozen complete-time comparisons and preserve failed requests."""
import collections,json,math,statistics
import numpy as np
from s00_policy import *

METHODS=['native','fixed','learned']
def analyze(folder,graphs):
 methods_list=METHODS+(['previous'] if folder=='model_test' else [])
 records=[];failed_references=[];failed_trials=[];checks=0;peak=0
 for graph in graphs:
  assert (HERE/folder/(graph+'_completion.json')).exists(),(folder,graph)
  for p in sorted((HERE/folder).glob(graph+'_h*_r*.json.gz')):
   r=rt.read(p);records.append(r);checks+=r.get('coefficient_checks',0)
   for a in r.get('attempts',[]):peak=max(peak,a.get('peak_rss_bytes',0))
   if not r['success']:failed_trials.append(p.name)
  proto=rt.read(HERE/'protocols'/((('cost_' if folder=='model_test' else '')+graph)+'.json'))
  for c in proto['reserved']:
   p=HERE/'references'/(c['id']+'.json.gz')
   if p.exists() and not rt.read(p)['success']:failed_references.append(c['id'])
 bycase=collections.defaultdict(lambda:collections.defaultdict(list))
 for r in records:bycase[r['case']][r['method']].append(r)
 rows=[];identity=[]
 for case,methods in sorted(bycase.items()):
  if any(len(methods[m])!=7 or not all(r['success'] and r['reference_checked'] for r in methods[m]) for m in methods_list):continue
  if any(all(row=={t:'1'} for t,row in r['coefficients'].items()) for r in methods['native']):identity.append(case);continue
  assert len({r['worker'] for rs in methods.values() for r in rs})==1,case
  times={m:[r['complete_seconds'] for r in sorted(methods[m],key=lambda x:x['repetition'])] for m in methods_list}
  median={m:statistics.median(t) for m,t in times.items()}
  rows.append(dict(case=case,graph=case.split('_h')[0],times=times,median_seconds=median,ratios={m:median[m]/median['native'] for m in methods_list},prediction_calls=sum(r.get('selection',{}).get('prediction_used',False) for r in methods['learned']),fallbacks={m:sum(r['fallbacks'] for r in methods[m]) for m in methods_list}))
 assert rows,'No matched complete nontrivial comparisons'
 total={m:sum(r['median_seconds'][m] for r in rows) for m in methods_list}
 rng=np.random.RandomState(903);intervals={}
 for a,b in [('learned','native'),('learned','fixed'),('fixed','native')]+([('learned','previous')] if folder=='model_test' else []):
  samples=[]
  for k in range(4000):
   top=bottom=0
   for r in rows:
    ids=rng.randint(0,7,7);top+=float(np.median(np.array(r['times'][a])[ids]));bottom+=float(np.median(np.array(r['times'][b])[ids]))
   samples.append(top/bottom)
  intervals[a+'_to_'+b]=dict(ratio=total[a]/total[b],paired_repetition_95_interval=np.quantile(samples,[.025,.975]).tolist())
 return dict(complete=True,matched=len(rows),timings=len(records),coefficient_checks=checks,all_successful_outputs_exact=all(r.get('reference_checked',False) for r in records if r['success']),failed_trials=failed_trials,failed_references=failed_references,identity_cases=identity,totals=total,comparisons=intervals,rows=rows,peak_rss_bytes=peak,scope='Known planar and nonplanar two-loop boxes; rational kinematics, symbolic dimension, supplied basis; no universal loop-order claim.')

def main():
 out=dict(initial=analyze('initial_test',['double_box']),adaptive=analyze('model_test',['double_box','nonplanar_box']))
 out['models']={p.stem:rt.read(p) for p in (HERE/'trained_model').glob('*.json')}
 out['sources']={p.name:inputs.sha(p) for p in HERE.glob('*.py')}
 inputs.write(HERE/'summary.json',out)
 print(json.dumps({name:{k:v for k,v in d.items() if k in ['matched','timings','coefficient_checks','comparisons','failed_trials','failed_references']} for name,d in out.items() if name in ['initial','adaptive']}),flush=True)
if __name__=='__main__':main()
