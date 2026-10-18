"""Compare full preparation workflows, including every failed first request."""
from s00_common import *
from s14_prepare import P,equal
import collections,random

def paired(rows,a,b):
 selected=[r for r in rows if r['complete'][a] and r['complete'][b] and r['pairs'][a+'/'+b]['agree']]
 if not selected:return dict(cases=0)
 totals={m:sum(statistics.median(r['times'][m]) for r in selected) for m in [a,b]}
 rng=random.Random(1237);samples=[]
 for _ in range(2000):
  t={a:0.,b:0.}
  for r in selected:
   ids=[rng.randrange(3) for _ in range(3)]
   for m in t:t[m]+=statistics.median(r['times'][m][j] for j in ids)
  samples.append(t[a]/t[b])
 return dict(cases=len(selected),case_ids=[r['id'] for r in selected],summed_median_seconds=totals,ratio=totals[a]/totals[b],interval=[sorted(samples)[49],sorted(samples)[1949]],changed_from_native=sum(r['first_action'][a]!='native' for r in selected),actions=dict(collections.Counter(r['first_action'][a] for r in selected)))

def main():
 protocol=READ(P/'protocol.json');methods=protocol['methods'];rows=[];checks=0
 formula=module('preparation_scalar_scope',ROOT/'ML_model_adaptive_reduction/massless_banana/s00_formula.py')
 assert inputs.sha(P/'trained_model/freeze.json')==protocol['risk_sha256']
 assert inputs.sha(HERE/'refit/trained_model/freeze.json')==protocol['model_sha256']
 assert inputs.sha(P/'basis_cache.json')==protocol['cache_sha256']
 for w in [0,1]:assert READ(P/('worker_'+str(w)+'_complete.json'))['complete']
 for c in protocol['cases']:
  rs={};times={};complete={};within={};first={};attempts={};failed_cost={};elapsed={};cache={};inference={}
  for m in methods:
   first[m]=READ(P/'model_test'/(c['id']+'_'+m+'_r0.json.gz'))
   n=3 if first[m]['success'] else 1
   rs[m]=[READ(P/'model_test'/(c['id']+'_'+m+'_r'+str(j)+'.json.gz')) for j in range(n)]
   assert all(r['process_timer_complete'] and r['complete_seconds']>0 for r in rs[m])
   complete[m]=len(rs[m])==3 and all(r['success'] for r in rs[m]);within[m]=True
   for r in rs[m][1:]:
    if r['success']:
     same={tuple(x) for x in r['masters']}=={tuple(x) for x in first[m]['masters']}
     agree,num=equal(r['coefficients'],first[m]['coefficients']);checks+=num
     within[m]&=same and agree
   assert within[m],('repeat coefficients differ',c['id'],m)
   times[m]=[r['complete_seconds'] for r in rs[m]]
   attempts[m]=sum(not a['result']['success'] for a in first[m].get('attempts',[]))
   failed_cost[m]=sum(a['result']['complete_seconds'] for a in first[m].get('attempts',[]) if not a['result']['success'])
   elapsed[m]=first[m]['complete_seconds'];cache[m]=first[m].get('cache_hit',False)
   inference[m]=first[m].get('inference_seconds',0.)
   checks+=sum(r.get('coefficient_checks',0) for r in rs[m])
  pairs={}
  for a in methods:
   for b in methods:
    if a==b:continue
    same=complete[a] and complete[b] and {tuple(x) for x in first[a]['masters']}=={tuple(x) for x in first[b]['masters']}
    agree,num=equal(first[a]['coefficients'],first[b]['coefficients']) if same else (False,0)
    if same:assert agree,('cross-method mismatch',c['id'],a,b)
    checks+=num;pairs[a+'/'+b]=dict(same_basis=bool(same),agree=bool(agree),checks=num)
  n=c['definition']['physical_propagators'];N=len(c['definition']['propagators']);analytic=formula.reduce(c,[[1]*n+[0]*(N-n)]) is not None
  rows.append(dict(id=c['id'],loops=len(c['definition']['loop_momenta']),group=c['topology_group'],analytic_formula_eligible=analytic,complete=complete,first_success={m:r['success'] for m,r in first.items()},status={m:r['status'] for m,r in first.items()},times=times,first_elapsed=elapsed,first_failed_attempts=attempts,first_failed_seconds=failed_cost,cache_hit=cache,inference_seconds=inference,first_action={m:r.get('first_action') for m,r in first.items()},pairs=pairs))
 comparisons={a+'/'+b:paired(rows,a,b) for a,b in [('cached_native','expanded'),('cached_learned','expanded'),('cached_risk','expanded'),('cached_learned','cached_native'),('cached_risk','cached_native'),('cached_risk','cached_learned')]}
 counts={m:dict(first_completed=sum(r['first_success'][m] for r in rows),three_completed=sum(r['complete'][m] for r in rows),first_failed_attempts=sum(r['first_failed_attempts'][m] for r in rows),first_failed_seconds=sum(r['first_failed_seconds'][m] for r in rows),first_elapsed_seconds=sum(r['first_elapsed'][m] for r in rows),cache_hits=sum(r['cache_hit'][m] for r in rows),inference_seconds=sum(r['inference_seconds'][m] for r in rows),statuses=dict(collections.Counter(r['status'][m] for r in rows))) for m in methods}
 cache=READ(P/'basis_cache.json')['entries'];cache_seconds=0.
 for entry in cache.values():
  reference=ROOT/entry['reference'];check=reference.with_name(entry['source_case']+'_check.json.gz')
  assert inputs.sha(reference)==entry['reference_sha256'] and inputs.sha(check)==entry['check_sha256']
  cache_seconds+=READ(reference)['complete_seconds']+READ(check)['complete_seconds']
 shared_attempts=[a for f in (HERE/'refit/model_test').glob('*_learned_r*.json.gz') for a in READ(f).get('attempts',[])]
 summary=dict(complete=True,requests=len(rows),profile=1237,methods=methods,counts=counts,comparisons=comparisons,rows=rows,coefficient_checks=checks,all_same_basis_matched_outputs_exact=True,training=READ(P/'trained_model/selection.json'),cached_structures=len(cache),selected_cache_source_seconds=cache_seconds,earlier_shared_attempts=len(shared_attempts),earlier_shared_failed_attempts=sum(not a['success'] for a in shared_attempts),by_loop={str(L):{m:sum(r['complete'][m] for r in rows if r['loops']==L) for m in methods} for L in sorted({r['loops'] for r in rows})},timing=protocol['timing'])
 numerical=[r for r in rows if not r['analytic_formula_eligible']]
 remaining={m:paired(numerical,m,'cached_native') for m in ['cached_learned','cached_risk']}
 summary['outside_scalar_formula']=dict(requests=len(numerical),comparisons=remaining,scope='Physical applicability of the existing exact scalar formula defines this subset; no timing threshold selects its requests.')
 neural=remaining['cached_learned'];retain=bool(neural['cases'] and neural['interval'][1]<1 and all(not r['complete']['cached_native'] or r['complete']['cached_learned'] for r in numerical))
 deployment=dict(preparation_method='learned' if retain else 'native',supplied_basis_method='learned',exact_scalar_formula_first=True,reason='Retain neural preparation only if the matched interval is below one and every completed native request outside the exact-formula domain also completes with the neural model.',scope='Post-comparison deployment decision. The paper reports the frozen candidates separately; it does not claim an independent timing test of this selection rule.',neural_preparation_comparison=neural)
 write(P/'deployment.json',deployment);summary['deployment']=deployment
 write(P/'summary.json',summary);write(ROOT/'report/preparation_data.json',summary)
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,axes=plt.subplots(1,2,figsize=(7.3,3.2));names=['Expanded','Compact, no ML','Compact, neural','Compact, cost + risk']
 ax=axes[0];ax.barh(range(4),[counts[m]['first_failed_seconds'] for m in methods],color=['#9d9d9d','#5b8ca4','#275978','#d1913f']);ax.set_yticks(range(4));ax.set_yticklabels(names);ax.invert_yaxis();ax.set_xlabel('Failed-attempt time (s), first pass');ax.set_title('Failed work across all requests',fontsize=10);ax.grid(axis='x',alpha=.2)
 ax=axes[1];pairs=['cached_learned/cached_native','cached_risk/cached_native'];limits=[1.]
 for i,k in enumerate(pairs):
  g=comparisons[k]
  if not g['cases']:continue
  ax.plot(g['interval'],[i,i],color='#275978',lw=2);ax.plot(g['ratio'],i,'o',color='#275978');limits+=g['interval']+[g['ratio']]
 ax.axvline(1,color='.4',ls='--');ax.set_yticks([0,1]);ax.set_yticklabels(['Neural / no ML','Cost + risk / no ML']);ax.set_ylim(1.5,-.5);ax.set_xlim(max(0,min(limits)-.04),max(limits)+.04);ax.set_xlabel('Complete time ratio');ax.set_title('ML within the compact workflow',fontsize=10);ax.grid(axis='x',alpha=.2)
 fig.tight_layout();fig.savefig(ROOT/'report/paper_figures/preparation_results.pdf');plt.close(fig)
 print(json.dumps({k:summary[k] for k in ['requests','counts','comparisons','coefficient_checks']}),flush=True)

if __name__=='__main__':main()
