"""Check reserved reductions and plot complete-time comparisons."""
import collections,json,math,statistics,os
from pathlib import Path
import numpy as np
from s05_study import HERE,ROOT,KINDS,CONFIGS,read,write,sha

def main():
 manifest=json.loads((HERE/'cases.json').read_text());frozen=json.loads((HERE/'trained_model/freeze.json').read_text())
 methods=['native','fixed','best_fixed','learned'];cases=[];workflows=0;checks=0;applications=0;fallbacks=collections.Counter();choices=collections.Counter()
 peaks=collections.Counter();hosts=set();stage_by_method={m:collections.Counter() for m in methods}
 for c in manifest['cases']:
  if c['split']!='reserved':continue
  times={};first={};decisions={}
  for method in methods:
   rows=[read(HERE/'model_test'/f'{c["id"]}_{method}_{r}.json.gz') for r in range(5)]
   assert all(r['success'] for r in rows)
   times[method]=statistics.median(r['complete_seconds'] for r in rows);first[method]=sum(r['fallback_count']==0 for r in rows)
   decisions[method]=sorted({r['configuration'] for r in rows})
   for r in rows:
    workflows+=1;fallbacks[method]+=r['fallback_count']
    if method=='learned':choices[r['configuration']]+=1
    a=r['attempts'][-1];assert a['reference_checked'];checks+=sum(len(v) for v in a['coefficients'].values())
    for a in r['attempts']:
     hosts.add(a['worker_host'])
     peaks['rss_bytes']=max(peaks['rss_bytes'],a.get('peak_rss_bytes',0));peaks['scratch_bytes']=max(peaks['scratch_bytes'],a.get('peak_scratch_bytes',0))
     for s in a['stage_metrics']:stage_by_method[method][s['stage']]+=s['seconds']
  app=read(HERE/'model_test'/f'{c["id"]}_application.json.gz');assert app['success'] and app['answers_withheld'];applications+=1
  cases.append(dict(case=c['id'],topology=c['topology_group'],loops=len(c['definition']['loop_momenta']),symbolic=bool(c['definition']['invariants']),targets=c['size'],median_seconds=times,first_attempts=first,decisions=decisions,
   ratios={m:times[m]/times['native'] for m in methods[1:]},learned_to_fixed=times['learned']/times['fixed'],learned_to_best_fixed=times['learned']/times['best_fixed']))
 by_kind={k:{} for k in KINDS}
 for k in KINDS:
  cs=[c for c in cases if c['topology']==k]
  for m in methods[1:]:by_kind[k][m]=math.exp(statistics.mean(math.log(c['ratios'][m]) for c in cs))
  by_kind[k]['learned_to_fixed']=math.exp(statistics.mean(math.log(c['learned_to_fixed']) for c in cs))
  by_kind[k]['learned_to_best_fixed']=math.exp(statistics.mean(math.log(c['learned_to_best_fixed']) for c in cs))
 aggregate={};rng=np.random.default_rng(91027);indices=rng.integers(0,len(KINDS),(10000,len(KINDS)))
 for m in methods[1:]+['learned_to_fixed','learned_to_best_fixed']:
  x=np.log([by_kind[k][m] for k in KINDS]);interval=np.quantile(np.exp(x[indices].mean(axis=1)),[.025,.975]).tolist()
  aggregate[m]=dict(ratio=float(np.exp(x.mean())),interval=interval)
 out=dict(complete=True,all_exact=True,workflows=workflows,applications=applications,coefficient_entries_checked=checks,cases=cases,by_topology=by_kind,aggregate=aggregate,
  fallbacks=dict(fallbacks),learned_choices=dict(choices),resource_peaks=dict(peaks),worker_hosts=sorted(hosts),stage_totals={m:dict(v) for m,v in stage_by_method.items()},
  selected_model=frozen['model']['name'],validation_ratio=frozen['validation']['ratio'],best_fixed=frozen['best_fixed'],
  training_cases=sum(c['split']=='training' for c in manifest['cases']),validation_cases=sum(c['split']=='validation' for c in manifest['cases']),test_cases=len(cases),
  timing='Input preparation, model prediction, full native IBP generation and reduction, exact checks, cleanup and all fallback. References and offline training excluded.',
  scope=manifest['scope'],source_sha256=sha(Path(__file__)),freeze_sha256=sha(HERE/'trained_model/freeze.json'))
 assert workflows==len(cases)*20
 write(HERE/'model_test/summary.json',out)
 os.environ.setdefault('MPLCONFIGDIR',os.path.join(os.environ.get('TMPDIR','/tmp'),'kira_workflow_mpl'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 names={'sunrise':'Sunrise (2 loops)','double_box':'Planar box (2 loops)','vacuum3':'Vacuum (3 loops)','ladder3':'Ladder (3 loops)','nonplanar_box':'Nonplanar box (2 loops)','pentagon':'Pentagon (1 loop)','one_mass_box':'Box with virtuality (1 loop)'}
 fig,ax=plt.subplots(figsize=(8,4.4));colors=['#497799','#df8934','#278264']
 allvalues=[]
 for j,(m,label) in enumerate(zip(methods[1:],['Integrated native choices','Best fixed strategy','Learned strategy'])):
  values=[by_kind[k][m] for k in KINDS];allvalues+=values
  ax.scatter(values,np.arange(len(KINDS))+(j-1)*.18,label=label,color=colors[j],s=34)
 ax.axvline(1,color='.45',linestyle='--',linewidth=1);ax.set_yticks(range(len(KINDS)));ax.set_yticklabels([names[k] for k in KINDS]);ax.invert_yaxis()
 lo=min(allvalues+[1]);hi=max(allvalues+[1]);pad=max(.04,.1*(hi-lo));ax.set_xlim(max(0,lo-pad),hi+pad);ax.grid(axis='x',alpha=.2)
 ax.set_xlabel('Full reduction time / previous native time (lower is faster)');ax.legend(loc='upper center',bbox_to_anchor=(.5,-.16),ncol=3,frameon=False,fontsize=8)
 fig.tight_layout();dest=ROOT/'report/paper_figures/workflow_time.pdf';fig.savefig(dest,bbox_inches='tight');plt.close(fig)
 write(ROOT/'report/workflow_figure_data.json',out)
 print(json.dumps({k:v for k,v in out.items() if k not in ['cases','stage_totals']}),flush=True)
if __name__=='__main__':main()
