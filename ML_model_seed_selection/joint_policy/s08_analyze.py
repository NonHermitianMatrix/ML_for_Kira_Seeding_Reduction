"""Audit frozen tests and separate learned choices from exact scale reuse."""
import collections,random,statistics
from s00_engine import *

def compare(rows,left,right,repetitions=4000):
 ratio=sum(statistics.median(r[left]) for r in rows)/sum(statistics.median(r[right]) for r in rows)
 rng=random.Random(933);values=[]
 for _ in range(repetitions):
  a=b=0.
  for row in rows:
   ids=[rng.randrange(len(row[left])) for _ in row[left]]
   a+=statistics.median(row[left][i] for i in ids);b+=statistics.median(row[right][i] for i in ids)
  values.append(a/b)
 values.sort();return dict(ratio=ratio,paired_repetition_95_interval=[values[int(.025*repetitions)],values[int(.975*repetitions)]])

def main():
 methods=['native','previous','fixed','learned'];rows=[];total_checks=0;timings=0;peak_rss=0;peak_scratch=0
 models={}
 for graph in ['double_box','nonplanar_box']:
  done=rt.read(HERE/'model_test'/(graph+'_completion.json'));assert done['complete']
  for n,h in done['sources'].items():assert inputs.sha(HERE/n)==h,n
  f=rt.read(HERE/'trained_model'/(graph+'.json'));models[graph]={k:v for k,v in f.items() if k not in ['model','signature']}
  for c in rt.read(HERE/'protocols'/(graph+'.json'))['reserved']:
   times={};fallbacks={};choices={};prediction=0;workers=set()
   for method in methods:
    records=[rt.read(HERE/'model_test'/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')) for rep in range(5)]
    for r in records:
     workers.add(r['worker'])
     assert r['success'] and r['reference_checked'] and not r['mismatches']
     assert not r.get('reference_coefficients_supplied',False)
     if method in ['native','fixed']:assert not r['selection']['prediction_used']
     for a in r.get('attempts',[]):
      if method in ['native','fixed']:assert a.get('equation_mode','off')=='off' and not a.get('weights_sha256')
      peak_rss=max(peak_rss,a.get('peak_rss_bytes',0));peak_scratch=max(peak_scratch,a.get('peak_scratch_bytes',0))
     total_checks+=r['coefficient_checks'];timings+=1
    times[method]=[r['complete_seconds'] for r in records];fallbacks[method]=sum(r.get('fallbacks',0) for r in records);choices[method]=dict(collections.Counter(r.get('strategy',r.get('route','unknown')) for r in records))
    if method=='learned':prediction=sum(r['selection']['prediction_used'] for r in records)
   assert len(workers)==1,(c['id'],workers)
   rows.append(dict(case=c['id'],graph=graph,times=times,median_seconds={m:statistics.median(t) for m,t in times.items()},fallbacks=fallbacks,choices=choices,predictions=prediction))
 totals={m:sum(r['median_seconds'][m] for r in rows) for m in methods}
 pairs=[('learned','native'),('learned','previous'),('learned','fixed'),('fixed','native')]
 comparisons={a+'_to_'+b:compare([r['times'] for r in rows],a,b) for a,b in pairs}
 by_graph={g:dict(totals={m:sum(r['median_seconds'][m] for r in rows if r['graph']==g) for m in methods},comparisons={a+'_to_'+b:compare([r['times'] for r in rows if r['graph']==g],a,b) for a,b in pairs}) for g in models}
 application=[];app_methods=['previous','learned','fixed_reuse','learned_reuse'];app_checks=0;sequences=0;app_requests=0
 for graph in models:
  assert rt.read(HERE/'application_test'/(graph+'_completion.json'))['complete']
  for c in rt.read(HERE/'application_test'/(graph+'_protocol.json'))['cases']:
   times={};hits={};routes={};workers=set()
   for method in app_methods:
    rs=[rt.read(HERE/'application_test'/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')) for rep in range(3)]
    for r in rs:
     workers.add(r['worker'])
     assert r['all_exact'] and r['first_request_included'] and all(x['reference_checked'] and x['success'] for x in r['results'])
     sequences+=1;app_requests+=len(r['results']);app_checks+=r['coefficient_checks']
    times[method]=[r['complete_seconds'] for r in rs];hits[method]=sum(x.get('route')=='exact_scale_reuse' for r in rs for x in r['results']);routes[method]=dict(collections.Counter(x['route'] for r in rs for x in r['results']))
   assert len(workers)==1,(c['id'],workers)
   for method in ['previous','learned']:assert hits[method]==0,(c['id'],method,hits[method])
   for method in ['fixed_reuse','learned_reuse']:assert hits[method]==6,(c['id'],method,hits[method])
   application.append(dict(case=c['id'],times=times,median_seconds={m:statistics.median(t) for m,t in times.items()},reuse_hits=hits,routes=routes))
 app_totals={m:sum(r['median_seconds'][m] for r in application) for m in app_methods}
 app_pairs=[('learned_reuse','previous'),('learned_reuse','learned'),('learned_reuse','fixed_reuse')]
 out=dict(complete=True,all_exact=True,requests=len(rows),timings=timings,coefficient_checks=total_checks,totals=totals,comparisons=comparisons,by_graph=by_graph,rows=rows,models=models,peak_rss_bytes=peak_rss,peak_scratch_bytes=peak_scratch,application=dict(sequences=sequences,requests=app_requests,coefficient_checks=app_checks,rows=application,totals=app_totals,comparisons={a+'_to_'+b:compare([r['times'] for r in application],a,b) for a,b in app_pairs}),scope='Known planar and nonplanar massless two-loop boxes, numerator ranks 2--4, rational kinematics, symbolic dimension, supplied bases; no result cache in main tests. Scale tests include each first solve.')
 out['additional_attempts']={m:sum(row['fallbacks'][m] for row in rows) for m in methods}
 save(HERE/'summary.json',out);print('SUMMARY',json.dumps({k:v for k,v in out.items() if k not in ['rows','models','application','by_graph']}),flush=True)
 print('APPLICATION_SUMMARY',json.dumps({k:v for k,v in out['application'].items() if k!='rows'}),flush=True)

if __name__=='__main__':main()
