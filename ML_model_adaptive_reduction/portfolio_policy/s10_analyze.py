"""Analyze all frozen reserved results, including incomplete requests."""
from s00_common import *
import statistics,random,collections
METHODS=['native','fixed','learned','previous','production']
def aggregate(rows):
 if not rows:return dict(cases=0)
 sums={m:sum(r['medians'][m] for r in rows) for m in METHODS};ratios={m:sums[m]/sums['native'] for m in METHODS};rng=random.Random(1147);intervals={}
 for a,b in [('learned','fixed'),('production','previous'),('learned','native'),('production','native')]:
  vals=[]
  for k in range(2000):
   sums0=[0.,0.]
   for row in rows:
    ids=[rng.randrange(len(row['times'][a])) for _ in row['times'][a]]
    for j,m in enumerate([a,b]):sums0[j]+=statistics.median(row['times'][m][i] for i in ids)
   vals.append(sums0[0]/sums0[1])
  vals.sort();intervals[a+'_over_'+b]=[vals[50],vals[1949]]
 return dict(cases=len(rows),active_cases=sum(any(d.get('prediction_used') for d in r.get('learned_decisions',[])) for r in rows),changed_cases=sum(r.get('changed_action',False) for r in rows),deployed_cases=sum('validated_target_pattern' in r.get('routes',[]) for r in rows),summed_median_seconds=sums,ratios_to_native=ratios,learned_over_fixed=sums['learned']/sums['fixed'],production_over_previous=sums['production']/sums['previous'],intervals=intervals)
def main():
 protocol=read(HERE/'protocol.json');freeze=read(HERE/'trained_model/freeze.json');rows=[];coverage=[];checks=0;failed=0;active=0
 for c in protocol['splits']['reserved']:
  p=HERE/'coverage'/(c['id']+'.json');v=read(p);coverage.append(dict(v,graph=c['topology_group'],loops=len(c['definition']['loop_momenta'])))
  if v['status']!='verified' or not v['nontrivial']:continue
  times={};decisions=[];production=[];equations={};fallbacks={};actions={}
  for m in METHODS:
   rs=[read(HERE/'model_test'/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz')) for rep in range(5)]
   assert all(r['success'] and r['reference_checked'] for r in rs);checks+=sum(r.get('coefficient_checks',0) for r in rs)
   times[m]=[r['complete_seconds'] for r in rs]
   if m=='learned':decisions=[r['selection'] for r in rs];active+=any(r['selection']['prediction_used'] for r in rs)
   if m=='production':production=[dict(route=r.get('route'),selection=r.get('selection',{})) for r in rs]
   equations[m]=[sum(sum(a.get('counters',{}).get('generated_equations',[])) for a in r.get('attempts',[])) for r in rs]
   fallbacks[m]=[r.get('fallbacks',0) for r in rs]
   actions[m]=[r.get('first_action') for r in rs]
  changed=actions['fixed']!=actions['learned'] and any(d.get('prediction_used') for d in decisions)
  rows.append(dict(id=c['id'],graph=c['topology_group'],loops=len(c['definition']['loop_momenta']),times=times,medians={m:statistics.median(v) for m,v in times.items()},learned_decisions=decisions,production=production,equations=equations,fallbacks=fallbacks,actions=actions,changed_action=changed))
 bygraph={g:aggregate([r for r in rows if r['graph']==g]) for g in sorted({r['graph'] for r in rows})}
 active_rows=[r for r in rows if any(d['prediction_used'] for d in r['learned_decisions'])]
 def storage_rows(folder):
  records=[]
  for p in sorted((HERE/folder/'results').glob('*.json')):
   v=read(p);v['measurements']={}
   for opt in [False,True]:
    rs=[read(q) for q in (HERE/folder/'model_test').glob(v['case']+'_'+str(int(opt))+'_*.json.gz')]
    if rs:v['measurements'][str(opt)]=dict(success=all(r['success'] for r in rs),median_seconds=statistics.median(r['complete_seconds'] for r in rs),peak_rss_bytes=max(r.get('peak_rss_bytes',0) for r in rs))
   rp=HERE/folder/'references'/(v['case']+'.json.gz')
   if rp.exists():
    q=read(rp);v['loops']=q.get('loops',v.get('loops'));v['targets']=len(q.get('coefficients',{}));v['nontrivial_targets']=sum(bool(row) and row!={target:'1'} for target,row in q.get('coefficients',{}).items());v['master_count']=len(q.get('masters',[]));v['reference_status']=q.get('status');v['reference_reason']=q.get('error') or q.get('log_tail','')[-450:]
   records.append(v)
  return records
 storage=storage_rows('integration')
 summary=dict(complete=True,requested=len(coverage),coverage_counts=dict(collections.Counter(v['status'] for v in coverage)),coverage=coverage,rows=rows,overall=aggregate(rows),by_graph=bygraph,active_learned=aggregate(active_rows),active_cases=active,coefficient_checks=checks,training_cases=freeze['training_count'],enabled_domains=freeze['enabled_domains'],sector_storage=storage,wide_sector_storage=storage_rows('wide_integration'),scalar=read(HERE/'scalar_test/summary.json'))
 discovery=sum(read(HERE/'references'/(r['id']+'.json.gz'))['complete_seconds'] for r in rows)
 independent=sum(read(HERE/'references'/(r['id']+'_check.json.gz'))['complete_seconds'] for r in rows)
 summary['master_discovery_seconds']=discovery;summary['independent_check_seconds']=independent
 summary['discovery_plus_application_seconds']={m:discovery+summary['overall']['summed_median_seconds'][m] for m in METHODS}
 offline=0.;measured=0
 for phase in ['training','validation','confirmation']:
  for p in (HERE/phase).glob('*.json.gz'):
   r=read(p)
   if not r.get('identical_configuration_from'):offline+=r['complete_seconds'];measured+=1
 summary['new_cost_collection_seconds']=offline;summary['new_cost_measurements']=measured
 combined=[];combined_failures=[]
 mapping={'native':'native','previous':'previous','fixed':'optimized_fixed','learned':'optimized_learned','production':'optimized_application'}
 combined_protocol=read(HERE/'combined_protocol.json');combined_coverage=[]
 for c in combined_protocol['cases']:
  status=read(HERE/'combined_coverage'/(c['id']+'.json'));combined_coverage.append(status)
  if status['status']!='verified' or not status['nontrivial']:continue
  row=dict(id=c['id'],graph=c['topology_group'],loops=len(c['definition']['loop_momenta']))
  ts={};bad=[];decisions=[];counts=0;routes=[];generated={};storage=[];widths=[];actions={}
  for m,label in mapping.items():
   rs=[read(HERE/'combined_test'/(row['id']+'_'+label+'_r'+str(rep)+'.json.gz')) for rep in range(5)]
   if not all(r['success'] and r.get('reference_checked') and r.get('process_timer_complete') for r in rs):bad.append(m)
   ts[m]=[r['complete_seconds'] for r in rs]
   actions[m]=[r.get('first_action') for r in rs]
   if m=='learned':decisions=[r.get('selection',{}) for r in rs]
   if m=='production':
    routes=[r.get('route') if r.get('route')!='validated_target_pattern' or r.get('selection',{}).get('prediction_used') else 'pattern_without_model' for r in rs];storage=[r.get('bounded_sector_storage',False) for r in rs];widths=[r.get('integral_weight_bits') for r in rs]
   if m in ['native','fixed','learned']:
    values=[]
    for r in rs:
     attempts=r.get('attempts',[])
     values.append(sum(sum(a['counters']['generated_equations']) for a in attempts) if attempts and all('generated_equations' in a.get('counters',{}) for a in attempts) else None)
    generated[m]=values
   counts+=sum(r.get('coefficient_checks',0) for r in rs)
  if bad:combined_failures.append(dict(case=row['id'],failed=bad));continue
  changed=actions['fixed']!=actions['learned'] and any(d.get('prediction_used') for d in decisions)
  combined.append(dict(id=row['id'],graph=row['graph'],loops=row['loops'],times=ts,medians={m:statistics.median(v) for m,v in ts.items()},learned_decisions=decisions,coefficient_checks=counts,routes=routes,generated_equations=generated,bounded_storage=storage,weight_widths=widths,actions=actions,changed_action=changed))
 summary['deployment']=read(HERE/'trained_model/deployment.json');summary['storage_deployment']=read(HERE/'integration/deployment.json')
 summary['combined']=dict(coverage=combined_coverage,requested=len(combined_protocol['cases']),reserved_profile=1151,coverage_counts=dict(collections.Counter(c['status'] for c in combined_coverage)),overall=aggregate(combined),rows=combined,failures=combined_failures,by_graph={g:aggregate([r for r in combined if r['graph']==g]) for g in sorted({r['graph'] for r in combined})},coefficient_checks=sum(r['coefficient_checks'] for r in combined),active=aggregate([r for r in combined if any(d.get('prediction_used') for d in r['learned_decisions'])]))
 summary['combined']['deployed']=aggregate([r for r in combined if 'validated_target_pattern' in r['routes']])
 summary['combined']['changed']=aggregate([r for r in combined if r['changed_action']])
 assert all(r['changed_action'] for r in combined if 'validated_target_pattern' in r['routes']), 'A deployed model must change the selected action before its timing is attributed to ML'
 summary['combined']['master_discovery_seconds']=sum(read(HERE/'references'/(r['id']+'.json.gz'))['complete_seconds'] for r in combined)
 summary['combined']['independent_check_seconds']=sum(read(HERE/'references'/(r['id']+'_check.json.gz'))['complete_seconds'] for r in combined)
 summary['combined']['failures'].extend(dict(case=c['case'],failed=c.get('failed_methods',[])) for c in combined_coverage if c['status']=='method_failed')
 write(HERE/'summary.json',summary);write(ROOT/'report/family_cost_data.json',summary)
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,ax=plt.subplots(1,2,figsize=(7.4,7.2),sharey=True);names=list(bygraph);ys=list(range(len(names)))
 for a,key,interval,title in [(ax[0],'learned_over_fixed','learned_over_fixed','Learned / tuned fixed'),(ax[1],'production_over_previous','production_over_previous','Combined / previous')]:
  for i,g in enumerate(names):
   r=bygraph[g];v=r[key];lo,hi=r['intervals'][interval];colour='#33658a' if key!='learned_over_fixed' or r['changed_cases'] else '0.6';a.plot([lo,hi],[i,i],color=colour,linewidth=1.5);a.plot(v,i,'o',color=colour,markersize=4)
  a.axvline(1,color='0.4',linestyle='--',linewidth=1);a.set_xlabel('Complete time ratio');a.set_title(title,fontsize=10);a.grid(axis='x',alpha=.2)
  values=[1.]+[bygraph[g][key] for g in names]+[v for g in names for v in bygraph[g]['intervals'][interval]];a.set_xlim(max(0,min(values)-.04),max(values)+.04)
 ax[0].set_yticks(ys);ax[0].set_yticklabels([g.replace('_L','; L=').replace('_',' ') for g in names]);ax[0].invert_yaxis();fig.tight_layout()
 fig.savefig(ROOT/'report/paper_figures/family_cost.pdf');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(7.4,3.2))
 final=summary['combined']['overall'];active=summary['combined']['deployed']
 panels=[[("vs native",final['ratios_to_native']['production'],final['intervals']['production_over_native']),("vs previous",final['production_over_previous'],final['intervals']['production_over_previous'])],[("all / fixed",final['learned_over_fixed'],final['intervals']['learned_over_fixed'])]]
 if active.get('cases'):
  panels[1].append(("deployed / fixed",active['learned_over_fixed'],active['intervals']['learned_over_fixed']))
  panels[1].append(("deployed / native",active['ratios_to_native']['learned'],active['intervals']['learned_over_native']))
 for ax,data,title in zip(axes,panels,['Final application time','Extra effect of learned choice']):
  endpoints=[]
  for i,(label,v,ci) in enumerate(data):
   ax.plot(ci,[i,i],color='#33658a',linewidth=2);ax.plot(v,i,'o',color='#1b4965',markersize=6);endpoints.extend(ci)
  ax.set_yticks(list(range(len(data))));ax.set_yticklabels([v[0] for v in data]);ax.invert_yaxis();ax.axvline(1,color='0.4',linestyle='--');ax.set_title(title,fontsize=11);ax.set_xlabel('Complete time ratio');ax.set_xlim(max(0,min(endpoints+[1])-.025),max(endpoints+[1])+.025);ax.set_ylim(len(data)-.5,-.5);ax.grid(axis='x',alpha=.2)
 fig.tight_layout();fig.savefig(ROOT/'report/paper_figures/family_combined.pdf');plt.close(fig)
 print(json.dumps(summary['overall']),flush=True)
if __name__=='__main__':main()
