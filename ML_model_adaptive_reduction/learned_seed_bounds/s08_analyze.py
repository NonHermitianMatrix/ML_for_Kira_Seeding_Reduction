"""Summarize all reserved requests and draw complete-cost comparisons."""
import collections,json,math,statistics
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from s00_inputs import *
import s01_runtime as rt
NAMES={'sunrise':'Massive sunrise','double_box':'Planar double box','vacuum3':'Massive vacuum','ladder3':'Massive three-loop ladder','nonplanar_box':'Nonplanar box','pentagon':'Pentagon','one_mass_box':'Box with virtual leg','bubble_box3':'Box with bubbles, 3 loops','bubble_box4':'Box with bubbles, 4 loops','massless4':'Massless two-point, 4 loops'}

def equations(r):return sum(sum(a.get('counters',{}).get('generated_equations',[])) for a in r['attempts'])
def allseconds(split,allowed=None):
 total=0.;n=0
 for p in (HERE/split).glob('*.json.gz'):
  if allowed is not None and not any(p.name in [c+'.json.gz',c+'_check.json.gz'] for c in allowed):continue
  r=rt.read(p)
  if 'identical_configuration_from' not in r:total+=r['complete_seconds'];n+=1
 return dict(seconds=total,calculations=n)
def main():
 protocol=rt.read(HERE/'protocol.json');fit=rt.read(HERE/'trained_model/selection.json');assert rt.read(HERE/'model_test/completion.json')['complete']
 cases=[];records=[];identity=[];incomplete=[];excluded=[];checks=0;peak=0
 for c in protocol['splits']['reserved']:
  methods={m:[rt.read(p) for j in range(protocol['repetitions']) if (p:=HERE/'model_test'/(c['id']+'_'+m+f'_r{j}.json.gz')).exists()] for m in protocol['methods']}
  runs=[r for v in methods.values() for r in v];records+=runs
  for r in runs:
   checks+=r.get('coefficient_checks',0);peak=max([peak]+[a.get('peak_rss_bytes',0) for a in r['attempts']])
   if r['success']:assert r['reference_checked'] and not r['mismatches']
   assert all(a['learned_algebra_disabled'] and a['equation_mode']=='off' and a['policy']=='native' for a in r['attempts'])
   if r['method']!='learned':assert r['scores'] is None and r['model_loading_seconds']==r['decision_seconds']==0
  if not runs:excluded.append(c['id']);continue
  if not all(len(v)==protocol['repetitions'] and all(r['success'] for r in v) for v in methods.values()):incomplete.append(c['id']);continue
  coeff=methods['native'][0]['coefficients']
  if all(v=={t:'1'} for t,v in coeff.items()):identity.append(c['id']);continue
  med={m:statistics.median(r['complete_seconds'] for r in v) for m,v in methods.items()}
  cases.append(dict(id=c['id'],graph=c['topology_group'],loops=len(c['definition']['loop_momenta']),shape=c['shape'],seconds=med,ratios={m:med['learned']/med[m] for m in ['native','fixed']},times={m:[r['complete_seconds'] for r in v] for m,v in methods.items()},equations={m:statistics.median(equations(r) for r in v) for m,v in methods.items()},fallbacks={m:sum(r['fallbacks'] for r in v) for m,v in methods.items()},learned_action=methods['learned'][0]['first_action'],fixed_action=methods['fixed'][0]['first_action']))
 assert cases
 inputs={c['id']:c for c in protocol['splits']['reserved']}
 for c in cases:
  request=inputs[c['id']]
  c['different_from_fixed']=(bounds(request,c['learned_action']),truncation(request,c['learned_action']))!=(bounds(request,c['fixed_action']),truncation(request,c['fixed_action']))
 totals={m:sum(c['seconds'][m] for c in cases) for m in protocol['methods']};graph={}
 for g in GRAPHS:
  group=[c for c in cases if c['graph']==g]
  if not group:continue
  graph[g]=dict(cases=len(group),seconds={m:sum(c['seconds'][m] for c in group) for m in protocol['methods']},equations={m:sum(c['equations'][m] for c in group) for m in protocol['methods']})
  graph[g]['ratios']={m:graph[g]['seconds']['learned']/graph[g]['seconds'][m] for m in ['native','fixed']}
 rng=np.random.default_rng(4921);intervals={};graphs=list(graph)
 for control in ['native','fixed']:
  # Resample complete graph blocks, preserving targets and parameter profiles.
  cluster=[];repeated=[]
  for _ in range(5000):
   sample=rng.integers(len(graphs),size=len(graphs));cluster.append(sum(graph[graphs[i]]['seconds']['learned'] for i in sample)/sum(graph[graphs[i]]['seconds'][control] for i in sample))
   nums=[];dens=[]
   for c in cases:
    idx=rng.integers(protocol['repetitions'],size=protocol['repetitions']);nums.append(float(np.median(np.array(c['times']['learned'])[idx])));dens.append(float(np.median(np.array(c['times'][control])[idx])))
   repeated.append(sum(nums)/sum(dens))
  intervals[control]=dict(graph_bootstrap=np.percentile(cluster,[2.5,97.5]).tolist(),repeat_bootstrap=np.percentile(repeated,[2.5,97.5]).tolist())
 learned=[r for r in records if r['method']=='learned'];offline={s:allseconds(s) for s in ['development','training','validation']}
 reference_ids=[c['id'] for s in ['training','validation'] for c in protocol['splits'][s]]+[c['id'] for c in rt.read(HERE/'development/protocol.json')['cases']]
 offline['references']=allseconds('references',reference_ids);offline_time=sum(v['seconds'] for v in offline.values())+fit['training_seconds']
 out=dict(complete=True,cases=cases,graphs=graph,totals=totals,ratios={m:totals['learned']/totals[m] for m in ['native','fixed']},intervals=intervals,requested=len(protocol['splits']['reserved']),matched=len(cases),identity_only=identity,reference_failed=excluded,incomplete=incomplete,timed=len(records),successful=sum(r['success'] for r in records),coefficient_checks=checks,peak_rss_mib=peak/1024**2,all_successful_outputs_exact=all(r['reference_checked'] for r in records if r['success']),model=fit['selected'],gate=fit['gate'],loading_mean_seconds=statistics.mean(r['model_loading_seconds'] for r in learned),prediction_mean_seconds=statistics.mean(r['decision_seconds'] for r in learned),all_run_seconds={m:sum(r['complete_seconds'] for r in records if r['method']==m) for m in protocol['methods']},all_run_successes={m:sum(r['success'] for r in records if r['method']==m) for m in protocol['methods']},learned_actions=dict(collections.Counter(r['first_action'] for r in learned)),fallbacks={m:sum(r['fallbacks'] for r in records if r['method']==m) for m in protocol['methods']},offline=offline,offline_seconds=offline_time,model_bytes=(HERE/'trained_model/freeze.json').stat().st_size,protocol_sha256=sha(HERE/'protocol.json'),model_sha256=sha(HERE/'trained_model/freeze.json'))
 out['amortization_requests']={m:math.ceil(offline_time/((totals[m]-totals['learned'])/len(cases))) if totals[m]>totals['learned'] else None for m in ['native','fixed']}
 out['new_ml_predictions']=sum(r['scores'] is not None for r in learned)
 out['guarded_native_requests']=sum(r['scores'] is None for r in learned)
 out['batches_with_changed_fixed_configuration']=sum(c['different_from_fixed'] for c in cases)
 write(HERE/'summary.json',out);write(ROOT/'report/learned_bounds_data.json',out)
 plot(out)
 print(json.dumps({k:v for k,v in out.items() if k not in ['cases','graphs']}),flush=True)

def plot(d):
 plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 dest=ROOT/'report/paper_figures';dest.mkdir(exist_ok=True)
 fig,axes=plt.subplots(1,2,figsize=(9.0,5.0),gridspec_kw={'width_ratios':[1.6,1]},constrained_layout=True)
 graphs=list(d['graphs']);y=np.arange(len(graphs));ax=axes[0]
 for m,shift,color,label in [('native',-.12,'#176b95','ML / native-bound control'),('fixed',.12,'#c66118','ML / tuned fixed control')]:
  vals=[d['graphs'][g]['ratios'][m] for g in graphs];ax.scatter(vals,y+shift,s=32,color=color,label=label,zorder=3)
 ax.axvline(1,color='.35',linestyle='--',linewidth=1);ax.set_yticks(y);ax.set_yticklabels([NAMES[g] for g in graphs]);ax.invert_yaxis();ax.set_xlabel('Complete-time ratio (smaller is faster)');ax.grid(axis='x',alpha=.2);ax.legend(loc='best',fontsize=9)
 vals=[d['graphs'][g]['ratios'][m] for g in graphs for m in ['native','fixed']];ax.set_xlim(max(0,min(vals)-.08),max(1.05,max(vals)+.08));ax.set_title('Tuned seed bounds explain\nmost of the saving',fontsize=11)
 ax=axes[1];methods=['native','fixed','learned'];values=[d['totals'][m] for m in methods];bars=ax.bar(range(3),values,color=['#909da4','#d68b4b','#176b95']);ax.set_xticks(range(3));ax.set_xticklabels(['Native\nbounds','Tuned\nfixed','Learned\nchoice']);ax.set_ylabel('Sum of median times (s)');ax.set_ylim(0,max(values)*1.19);[ax.annotate(f'{v:.1f}',(i,v),xytext=(0,3),textcoords='offset points',ha='center',va='bottom') for i,v in enumerate(values)];ax.set_title(f"Matched workload\n({d['matched']} target batches)",fontsize=11);ax.grid(axis='y',alpha=.18)
 fig.savefig(dest/'learned_bounds_times.pdf',bbox_inches='tight');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(9.0,4.5),constrained_layout=True)
 for m,color,label in [('native','#176b95','Native-bound control'),('fixed','#c66118','Tuned fixed control')]:
  q=np.sort([c['ratios'][m] for c in d['cases']]);axes[0].plot(q,np.arange(1,len(q)+1)/len(q),marker='.',markersize=3,color=color,label=label)
 axes[0].axvline(1,color='.35',linestyle='--',linewidth=1);axes[0].set_xlabel('ML / control complete-time ratio');axes[0].set_ylabel('Fraction of matched target batches');axes[0].set_ylim(0,1.04);axes[0].legend(fontsize=9);axes[0].grid(alpha=.2);axes[0].set_title('Both gains and slower targets remain visible',fontsize=11)
 ax=axes[1];x=[c['equations']['native'] for c in d['cases']];y=[c['equations']['learned'] for c in d['cases']];ax.scatter(x,y,color='#176b95',s=25,edgecolors='white',linewidth=.3);top=max(x+y)*1.15;ax.plot([1,top],[1,top],color='.4',linestyle='--');ax.set_xscale('symlog',linthresh=100);ax.set_yscale('symlog',linthresh=100);ax.set_xlim(0,top);ax.set_ylim(0,top);ax.set_xlabel('Generated equations: native bounds');ax.set_ylabel('Generated equations: learned choice');ax.set_title('Equation counts include unsuccessful attempts',fontsize=11);ax.grid(alpha=.15)
 fig.savefig(dest/'learned_bounds_effects.pdf');plt.close(fig)
if __name__=='__main__':main()
