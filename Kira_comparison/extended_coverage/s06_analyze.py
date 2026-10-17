"""Summarize fixed-workload paired times and all coverage limits."""
import collections,json,random,statistics
from s00_protocol import HERE,ROOT,read,write,sha

def median_time(paths):return statistics.median(read(p)['complete_seconds'] for p in paths)
def interval(rows,numerator,denominator):
 rng=random.Random(21017);ratios=[]
 for _ in range(2000):
  chosen=[rng.choices(range(3),k=3) for r in rows]
  sums={m:sum(statistics.median(r['samples'][m][i] for i in choice) for r,choice in zip(rows,chosen)) for m in [numerator,denominator]}
  ratios.append(sums[numerator]/sums[denominator])
 return [sorted(ratios)[49],sorted(ratios)[1949]]
def paired(ident,folder,methods):
 samples={}
 for m in methods:
  ps=[HERE/folder/f'{ident}_{m}_{i}.json.gz' for i in range(3)]
  if not all(p.exists() and read(p)['success'] and read(p).get('reference_checked',False) for p in ps):return None
  samples[m]=[read(p)['complete_seconds'] for p in ps]
 return dict(id=ident,samples=samples,medians={m:statistics.median(v) for m,v in samples.items()})
def summarize(rows,methods):
 if not rows:return dict(cases=0)
 sums={m:sum(r['medians'][m] for r in rows) for m in methods};base=methods[0]
 return dict(cases=len(rows),summed_median_seconds=sums,ratios={m:sums[m]/sums[base] for m in methods[1:]},intervals={m:interval(rows,m,base) for m in methods[1:]})
def main():
 protocol=read(HERE/'protocol.json');assert all(read(HERE/f'completion_{i}.json')['complete'] for i in range(2))
 for n,h in protocol['models'].items():assert sha(ROOT/n)==h,n
 for n,h in protocol['sources'].items():assert sha(ROOT/n)==h,n
 coverage=[read(HERE/'coverage'/(c['id']+'.json')) for c in protocol['cases']];matched=[];identity=[]
 for c in coverage:
  row=paired(c['id'],'model_test',protocol['methods'])
  if row:
   row.update({k:c[k] for k in ['loops','coverage_type','kinematics','nontrivial','reference_seconds','check_seconds']})
   (matched if c['nontrivial'] else identity).append(row)
 analytic=read(HERE/'analytic_completion.json');scale=read(HERE/'scale_completion.json');assert analytic['complete'] and scale['complete']
 ar=[]
 for c in analytic['cases']:
  row=paired(c['id'],'analytic',['direct_exact','previous','selected'])
  if row:row.update(c);ar.append(row)
 sr=[]
 for c in scale['cases']:
  row=paired(c['id'],'scale',['previous','selected','selected_reuse'])
  if row:
   row['cache_hits']=[read(HERE/'scale'/f'{c["id"]}_selected_reuse_{i}.json.gz').get('cache_hits',0) for i in range(3)]
   sr.append(row)
 byloop={str(L):dict(collections.Counter(c['status'] for c in coverage if c['loops']==L)) for L in range(1,13)}
 bytype={k:summarize([r for r in matched if r['coverage_type']==k],protocol['methods']) for k in sorted({c['coverage_type'] for c in coverage})}
 routes=collections.Counter();filters=0;active_filters=0;learned_cases=0
 for c in matched:
  r=read(HERE/'model_test'/f'{c["id"]}_selected_0.json.gz');routes[r.get('route','unknown')]+=1;filters+=bool(r.get('filter_enabled',False));active=any(a.get('equation_mode')=='learned' for a in r.get('attempts',[]));active_filters+=active;learned_cases+=bool(active or r.get('scores') is not None or r.get('selection',{}).get('prediction_used') or r.get('route')=='cost_trained_sparse_seeds')
 reasons=collections.Counter(c.get('reason','unspecified') for c in coverage if c['status'].startswith('reference_'))
 native=summarize(matched,protocol['methods'])
 native['discovery_seconds']=sum(r['reference_seconds'] for r in matched);native['independent_reference_check_seconds']=sum(r['check_seconds'] for r in matched)
 native['discovery_plus_application_seconds']={m:native['discovery_seconds']+native.get('summed_median_seconds',{}).get(m,0) for m in protocol['methods']}
 successful=failed=checks=0
 for folder in ['model_test','analytic','scale']:
  for p in (HERE/folder).glob('*.json.gz'):
   r=read(p)
   if 'method' not in r or r['method'] in ['reference','check']:continue
   successful+=bool(r['success']);failed+=not r['success'];checks+=r.get('coefficient_checks',0)+sum(x.get('coefficient_checks',0) for x in r.get('results',[]))
 summary=dict(complete=True,selected_routes=dict(routes),requested_filter_cases=filters,active_filter_cases=active_filters,active_learned_cases=learned_cases,reference_failure_reasons=dict(reasons),coverage=coverage,coverage_counts=dict(collections.Counter(c['status'] for c in coverage)),by_loop=byloop,by_type=bytype,native=native,native_rows=matched,identity_only=identity,analytic=summarize(ar,['direct_exact','previous','selected']),analytic_rows=ar,analytic_all_exact=analytic['all_exact'],scale=summarize(sr,['previous','selected','selected_reuse']),scale_rows=sr,scale_coverage=scale['cases'],successful_calls=successful,failed_calls=failed,coefficient_checks=checks,scope='Frozen current application. Finite 1--12-loop family grid. Exact analytic checks are separate from native IBP completion and ML timing gains.')
 write(HERE/'summary.json',summary)
 import os
 os.environ['MPLCONFIGDIR']=str(ROOT/'.tools/cache/matplotlib')
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 import numpy as np
 plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,(ax,bx)=plt.subplots(1,2,figsize=(9,4.8),gridspec_kw={'width_ratios':[1.2,1]},constrained_layout=True)
 Ls=list(range(1,13));bottom=np.zeros(12)
 for state,label,color in [('verified','All methods verified','#39835b'),('method_failed','Application failure','#ca8951'),('reference_failed','Reference limit / failure','#aa5860'),('reference_check_failed','Check failure','#9c759e'),('unsupported_index_count','Index limit','#bbbbbb')]:
  values=np.array([byloop[str(L)].get(state,0) for L in Ls]);ax.bar(Ls,values,bottom=bottom,label=label,color=color,width=.75);bottom+=values
 ax.set(xlabel='Loop order',ylabel='Number of requested native families',xticks=Ls,title='Native completion has a finite range');ax.legend(fontsize=10,loc='upper right')
 rows=[(k,v) for k,v in bytype.items() if v.get('cases')]
 rows.append(('All matched',native))
 names=[k.replace('propagator_','two-point ').replace('_',' ')+f" ({v['cases']})" for k,v in rows]
 vals=[v['ratios']['selected'] for k,v in rows];cis=[v['intervals']['selected'] for k,v in rows]
 for i,(x,ci) in enumerate(zip(vals,cis)):
  bx.plot(ci,[i,i],color='#436da5' if i<len(rows)-1 else '#222222',lw=2)
  bx.scatter([x],[i],color='#436da5' if i<len(rows)-1 else '#222222',s=25,zorder=3)
 bx.axvline(1,color='black',ls='--',lw=1)
 bx.set(yticks=range(len(names)),yticklabels=names,xlabel='Selected / native complete time',title='No resolved overall time saving',xlim=(min([.95]+[ci[0] for ci in cis])*.94,max([1.05]+[ci[1] for ci in cis])*1.06))
 bx.invert_yaxis()
 fig.savefig(ROOT/'report/paper_figures/extended_coverage.pdf');plt.close(fig)
 write(ROOT/'report/extended_coverage_data.json',summary)
 print(json.dumps({k:v for k,v in summary.items() if k in ['coverage_counts','native','analytic','scale','successful_calls','failed_calls','coefficient_checks']}),flush=True)
if __name__=='__main__':main()
