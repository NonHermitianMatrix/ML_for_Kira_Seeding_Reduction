"""Read complete records and produce comparisons without changing the model."""
from s00_common import *
import collections,random
METHODS=['native','fixed','learned','previous']
def aggregate(rows):
 if not rows:return dict(cases=0)
 sums={m:sum(r['medians'][m] for r in rows) for m in METHODS};ratios={b:sums['learned']/sums[b] for b in ['native','fixed','previous']};rng=random.Random(1213);samples={b:[] for b in ratios}
 for _ in range(2000):
  total={m:0. for m in METHODS}
  for r in rows:
   ids=[rng.randrange(3) for j in range(3)]
   for m in METHODS:total[m]+=statistics.median(r['times'][m][j] for j in ids)
  for b in ratios:samples[b].append(total['learned']/total[b])
 return dict(cases=len(rows),summed_median_seconds=sums,ratios=ratios,intervals={b:[sorted(v)[49],sorted(v)[1949]] for b,v in samples.items()},changed_native=sum(r['actions']['learned'][0]!='native' for r in rows),changed_fixed=sum(r['actions']['learned']!=r['actions']['fixed'] for r in rows))
def read_trial(base):
 protocol=READ(base/'protocol.json');coverage=[];rows=[];checks=0;all_seconds=0;completed=0
 for c in protocol['reserved']:
  cp=base/'coverage'/(c['id']+'.json');assert cp.exists(),str(cp)
  info=READ(cp);info['group']=c['topology_group'];coverage.append(info)
  if info['status']!='verified':continue
  ts={};actions={};counts=0;fallbacks={};decisions=[];generated={}
  for m in METHODS:
   rs=[READ(base/'model_test'/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz')) for rep in range(3)]
   assert all(r['success'] and r['reference_checked'] and r['process_timer_complete'] for r in rs)
   ts[m]=[r['complete_seconds'] for r in rs];actions[m]=[r.get('first_action') for r in rs];fallbacks[m]=sum(r.get('fallbacks',0) for r in rs)
   counts+=sum(r.get('coefficient_checks',0) for r in rs)
   if m=='learned':decisions=[r.get('selection') for r in rs]
   generated[m]=[sum(sum(a.get('counters',{}).get('generated_equations',[])) for a in r.get('attempts',[])) for r in rs]
  ref=READ(base/'references'/(c['id']+'.json.gz'))
  nontrivial=any(bool(v) and v!={t:'1'} for t,v in ref.get('coefficients',{}).items())
  info['nontrivial']=nontrivial
  if not nontrivial:info['status']='identity_only';continue
  checks+=counts
  rows.append(dict(id=c['id'],group=c['topology_group'],loops=len(c['definition']['loop_momenta']),physical_holdout=held_out(c),times=ts,medians={m:statistics.median(v) for m,v in ts.items()},actions=actions,fallbacks=fallbacks,decisions=decisions,coefficient_checks=counts,generated_equations=generated))
 for p in (base/'model_test').glob('*.json.gz'):
  r=READ(p);all_seconds+=r['complete_seconds'];completed+=bool(r['success'])
 discovery=sum(READ(p)['complete_seconds'] for p in (base/'references').glob('*.json.gz') if '_check.' not in p.name)
 independent=sum(READ(p)['complete_seconds'] for p in (base/'references').glob('*_check.json.gz'))
 result=dict(complete=True,requested=len(coverage),coverage=coverage,counts=dict(collections.Counter(r['status'] for r in coverage)),rows=rows,overall=aggregate(rows),held_out=aggregate([r for r in rows if r['physical_holdout']]),known=aggregate([r for r in rows if not r['physical_holdout']]),coefficient_checks=checks,all_timed_seconds=all_seconds,completed_runs=completed,discovery_seconds=discovery,independent_check_seconds=independent)
 result['by_loop']={str(L):dict(requested=sum(r['loops']==L for r in coverage),counts=dict(collections.Counter(r['status'] for r in coverage if r['loops']==L)),timing=aggregate([r for r in rows if r['loops']==L])) for L in range(1,13)}
 result['by_group']={g:aggregate([r for r in rows if r['group']==g]) for g in sorted({r['group'] for r in rows})}
 result['by_family_class']={g:aggregate([r for r in rows if re.sub(r'_L[0-9]+$', '', r['group'])==g]) for g in sorted({re.sub(r'_L[0-9]+$', '', r['group']) for r in rows})}
 return result

def main():
 for base in [HERE,HERE/'refit']:
  for w in [0,1]:assert READ(base/('test_'+str(w)+'_complete.json'))['complete']
 initial=read_trial(HERE);final=read_trial(HERE/'refit');final['initial_trial']={k:v for k,v in initial.items() if k not in ['rows','coverage']};final['training']=READ(HERE/'refit/trained_model/selection.json');final['gradient_check']=READ(HERE/'refit/gradient_check.json')
 write(HERE/'summary.json',final);write(ROOT/'report/general_policy_data.json',final)
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,axes=plt.subplots(1,2,figsize=(7.3,3.7));labels=['All matched','Training domains','Held-out families / loops'];groups=[final['overall'],final['known'],final['held_out']]
 for ax,control,title in zip(axes,['native','fixed'],['Shared model / native choices','Shared model / one fixed setting']):
  limits=[1.]
  for i,(label,g) in enumerate(zip(labels,groups)):
   if not g['cases']:continue
   x=g['ratios'][control];ci=g['intervals'][control];ax.plot(ci,[i,i],color='#245a81',lw=2);ax.plot(x,i,'o',color='#245a81');limits+=ci+[x]
  ax.axvline(1,color='0.35',ls='--');ax.set_yticks(range(3));ax.set_yticklabels(labels if ax is axes[0] else ['']*3);ax.set_ylim(2.5,-.5);ax.set_xlim(max(0,min(limits)-.04),max(limits)+.04);ax.set_xlabel('Complete time ratio');ax.set_title(title,fontsize=10);ax.grid(axis='x',alpha=.2)
 fig.tight_layout();fig.savefig(ROOT/'report/paper_figures/general_policy_times.pdf');plt.close(fig)
 fig,ax=plt.subplots(figsize=(7.3,3.4));bottom=[0]*12
 statuses=[('verified','#326b8e','Checked reductions'),('reference_failed','#cf923c','Reference failed'),('independent_check_failed','#a65b40','Reference check failed'),('method_failed','#8e548e','Method failed'),('identity_only','#83b49b','Identity only'),('unsupported_native_index_count','#b5b5b5','Native input unsupported')]
 for status,col,label in statuses:
  v=[final['by_loop'][str(L)]['counts'].get(status,0) for L in range(1,13)]
  if sum(v):ax.bar(range(1,13),v,bottom=bottom,color=col,label=label);bottom=[a+b for a,b in zip(bottom,v)]
 ax.set_xlabel('Number of loops');ax.set_ylabel('Requests');ax.set_xticks(range(1,13));ax.set_ylim(0,max(bottom)*1.38);ax.legend(fontsize=8,ncol=2,loc='upper right',frameon=False);ax.set_title('Coverage distinguishes a prediction from a checked reduction',fontsize=10);fig.tight_layout();fig.savefig(ROOT/'report/paper_figures/general_policy_coverage.pdf');plt.close(fig)
 seed=READ(ROOT/'report/seed_geometry_data.json')['adaptive']['comparisons']
 equation=READ(ROOT/'report/equation_refinement_data.json')['index_transfer']
 row=READ(ROOT/'report/paper_figure_data.json')['later_native']['row']
 fig,ax=plt.subplots(figsize=(7.3,2.9));data=[('Sparse seeds / native',seed['learned_to_native']['ratio'],seed['learned_to_native']['paired_repetition_95_interval']),('Sparse seeds / fixed sparse',seed['learned_to_fixed']['ratio'],seed['learned_to_fixed']['paired_repetition_95_interval']),('Equation filter / ML off',equation['ratio'],equation['repeat_interval']),('Compiled row policy / native',row['ratio'],row['descriptive_interval'])]
 for i,(label,x,ci) in enumerate(data):ax.plot(ci,[i,i],color='#245a81',lw=2);ax.plot(x,i,'o',color='#245a81')
 ax.set_yticks(range(4));ax.set_yticklabels([v[0] for v in data]);ax.set_ylim(3.5,-.5);ax.set_xlim(.73,1.035);ax.axvline(1,color='0.35',ls='--');ax.set_xlabel('Complete time ratio on each stated workload');ax.grid(axis='x',alpha=.2);fig.tight_layout();fig.savefig(ROOT/'report/paper_figures/paper_local_results.pdf');plt.close(fig)
 print(json.dumps({k:final[k] for k in ['requested','counts','overall','held_out','coefficient_checks']}),flush=True)
if __name__=='__main__':main()
