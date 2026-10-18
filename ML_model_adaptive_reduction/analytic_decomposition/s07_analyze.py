"""Summarize complete costs without discarding failed requests."""
from s01_common import *
import statistics

def main():
 import numpy as np
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 for i in range(2):assert READ(HERE/f'test_{i}_complete.json')['complete']
 p=READ(HERE/'test_protocol.json');rows=[];totals={m:dict(first_seconds=0.,all_seconds=0.,verified=0,failed_native_calls=0,native_calls=0,analytic_requests=0,model_requests=0) for m in p['methods']}
 for c in p['cases']:
  row=READ(HERE/'coverage'/(c['id']+'.json'));row['times']={};row['verified']={};row['analytic']={};row['model']={}
  for m in p['methods']:
   rs=[READ(q) for q in sorted((HERE/'model_test').glob(c['id']+'_'+m+'_r*.json.gz'))];assert rs
   ts=[r['complete_process_and_check_seconds'] for r in rs];ok=len(rs)==3 and all(r['independently_verified'] for r in rs)
   analytic=any(b['result'].get('route')=='one_loop_cayley_recurrence' for r in rs for b in r.get('blocks',[]));ml=any(r.get('model_used') for r in rs)
   row['times'][m]=ts;row['verified'][m]=ok;row['analytic'][m]=analytic;row['model'][m]=ml
   totals[m]['first_seconds']+=ts[0];totals[m]['all_seconds']+=sum(ts);totals[m]['verified']+=ok;totals[m]['analytic_requests']+=analytic;totals[m]['model_requests']+=ml
   attempts=[a for r in rs for b in r.get('blocks',[]) if not b.get('reused') for a in b['result'].get('attempts',[]) if a.get('native_called',True)]
   totals[m]['native_calls']+=len(attempts);totals[m]['failed_native_calls']+=sum(not a['success'] for a in attempts)
  rows.append(row)
 def comparison(control,selected):
  selected=[r for r in selected if r['verified']['learned'] and r['verified'][control]]
  if not selected:return dict(cases=0)
  x=np.array([r['times']['learned'] for r in selected]);y=np.array([r['times'][control] for r in selected]);a=float(np.median(x,axis=1).sum());b=float(np.median(y,axis=1).sum())
  ix=np.random.RandomState(2503).randint(0,3,(2000,len(selected),3));ii=np.arange(len(selected))[None,:,None];rat=np.median(x[ii,ix],axis=2).sum(1)/np.median(y[ii,ix],axis=2).sum(1)
  return dict(cases=len(selected),learned_seconds=a,control_seconds=b,ratio=a/b,speedup=b/a,reduction_percent=100*(1-a/b),repeat_interval=list(map(float,np.quantile(rat,[.025,.975]))))
 groups={'all':rows,**{s:[r for r in rows if r['scope']==s] for s in ['one_loop','products','ml_compatibility','other_compatibility']}}
 groups['analytic']=[r for r in rows if r['analytic']['learned']]
 comparisons={g:{m:comparison(m,rs) for m in ['native','fixed','previous']} for g,rs in groups.items()}
 summary=dict(complete=True,requests=len(rows),rows=rows,totals=totals,comparisons=comparisons,reference_seconds=sum(r['reference_seconds'] for r in rows),protocol_sha256=sha(HERE/'test_protocol.json'),basis_sha256=sha(HERE/'basis_registry.json'),source_sha256=p['runtime_sources'],scope=p['scope'])
 write(HERE/'summary.json',summary)
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,axes=plt.subplots(1,2,figsize=(9,4.1))
 labels=[];values=[];intervals=[]
 for group,name in [('one_loop','One-loop polygons'),('products','Independent products'),('ml_compatibility','Coupled ML cases'),('other_compatibility','Other compatibility cases'),('all','All matched requests')]:
  x=comparisons[group]['native']
  if x['cases']:labels.append(name);values.append(x['ratio']);intervals.append(x['repeat_interval'])
 for i,(v,(lo,hi)) in enumerate(zip(values,intervals)):
  axes[0].plot([lo,hi],[i,i],color='#146b7d',lw=2);axes[0].scatter([v],[i],color='#146b7d',s=28)
 axes[0].set_yticks(range(len(labels)));axes[0].set_yticklabels(labels);axes[0].invert_yaxis();axes[0].axvline(1,color='black',ls='--',lw=1);axes[0].set_xlim(max(0,min(lo for lo,hi in intervals)-.08),max([1]+[hi for lo,hi in intervals])+.08);axes[0].set_xlabel('Time / matched native-control time');axes[0].set_title('Gains differ across tested structures')
 methods=['previous','native','fixed','learned'];seconds=[totals[m]['first_seconds'] for m in methods]
 bars=axes[1].bar(range(4),seconds,color=['#9ca3af','#64748b','#94a3b8','#146b7d']);axes[1].set_xticks(range(4));axes[1].set_xticklabels(['Prior','Native','Exact\nfixed','Exact\nML']);axes[1].set_ylabel('Seconds');axes[1].set_ylim(0,max(seconds)*1.22);axes[1].set_title('All requested first attempts')
 for bar,m in zip(bars,methods):axes[1].text(bar.get_x()+bar.get_width()/2,bar.get_height()+max(seconds)*.02,f"{bar.get_height():.1f}\n{totals[m]['verified']}/{len(rows)}",ha='center',fontsize=8)
 fig.tight_layout();fig.savefig(ROOT/'report/paper_figures/analytic_decomposition.pdf',bbox_inches='tight');plt.close(fig)
 print(json.dumps({k:v for k,v in summary.items() if k!='rows'}),flush=True)
if __name__=='__main__':main()
