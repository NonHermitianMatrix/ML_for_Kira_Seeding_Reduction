"""Summarize exact completion, elapsed costs, and matched controls."""
from s00_cost_common import *

def main():
 import numpy as np
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 for i in range(2):assert READ(HERE/('test_'+str(i)+'_complete.json'))['complete']
 p=READ(HERE/'test_protocol.json');label_method=lambda m:'native' if m=='raw_native' else m;rows=[];times={};totals={label_method(m):dict(all_attempt_seconds=0.,first_pass_seconds=0.,failed_native_attempts=0,native_calls=0,unverified_requests=0,verified_requests=0,model_requests=0,decision_seconds=0.) for m in p['methods']}
 for c in p['cases']:
  row=READ(HERE/'coverage/reserved'/(c['id']+'.json'));rts={};complete={};models={};actions={};checks=0
  for method in p['methods']:
   m=label_method(method)
   rs=[READ(q) for q in sorted((HERE/'model_test').glob(c['id']+'_'+method+'_r*.json.gz'))];assert rs
   complete[m]=len(rs)==3 and all(r['independently_verified'] for r in rs);rts[m]=[r['complete_process_and_check_seconds'] for r in rs];models[m]=any(r.get('model_used') for r in rs)
   actions[m]=[[b['result'].get('first_action',b['result'].get('route')) for b in r.get('blocks',[]) if not b.get('reused')] for r in rs]
   totals[m]['all_attempt_seconds']+=sum(rts[m]);totals[m]['first_pass_seconds']+=rts[m][0];totals[m]['verified_requests']+=int(complete[m]);totals[m]['unverified_requests']+=int(not complete[m]);totals[m]['model_requests']+=int(models[m]);checks+=sum(r.get('coefficient_checks',0) for r in rs)
   for r in rs:
    for b in r.get('blocks',[]):
     if b.get('reused'):continue
     ats=b['result'].get('attempts',[]);totals[m]['native_calls']+=len(ats);totals[m]['failed_native_attempts']+=sum(not a['success'] for a in ats);totals[m]['decision_seconds']+=b['result'].get('decision_seconds',0.)
  row.update(complete=complete,model_used=models,actions=actions,coefficient_checks=checks);rows.append(row);times[c['id']]=rts
 def comparison(control,selected):
  selected=[r for r in selected if r['complete']['learned'] and r['complete'][control]]
  if not selected:return dict(cases=0)
  pairs=[(times[r['case']]['learned'],times[r['case']][control]) for r in selected];a=sum(statistics.median(x) for x,y in pairs);b=sum(statistics.median(y) for x,y in pairs);rng=np.random.RandomState(2063);ratios=[]
  indices=rng.randint(0,3,(2000,len(pairs),3));ii=np.arange(len(pairs))[None,:,None]
  xx=np.asarray([x for x,y in pairs]);yy=np.asarray([y for x,y in pairs])
  aa=np.median(xx[ii,indices],axis=2).sum(1);bb=np.median(yy[ii,indices],axis=2).sum(1);ratios=aa/bb
  return dict(cases=len(pairs),case_ids=[r['case'] for r in selected],learned_seconds=a,control_seconds=b,ratio=a/b,speedup=b/a,reduction_percent=100*(1-a/b),repeat_interval=list(map(float,np.quantile(ratios,[.025,.975]))))
 groups=dict(all=rows,ml=[r for r in rows if r['model_used']['learned']],coupled=[r for r in rows if r['scope']=='coupled_family'],products=[r for r in rows if r['scope']=='independent_loop_blocks'],formula=[r for r in rows if r['scope']=='analytic_formula'],pentagon=[r for r in rows if 'pentagon' in r['family']])
 groups.update(coupled_ml=[r for r in groups['coupled'] if r['model_used']['learned']],products_ml=[r for r in groups['products'] if r['model_used']['learned']],pentagon_ml=[r for r in groups['pentagon'] if r['model_used']['learned']])
 comp={g:{m:comparison(m,rs) for m in ['native','fixed','previous']} for g,rs in groups.items()}
 by_loop={str(L):dict(requested=len([r for r in rows if r['loops']==L]),verified={m:sum(r['complete'][m] for r in rows if r['loops']==L) for m in totals},native=comparison('native',[r for r in rows if r['loops']==L]),fixed=comparison('fixed',[r for r in rows if r['loops']==L])) for L in range(1,14)}
 s=dict(complete=True,requested=len(rows),totals=totals,comparisons=comp,by_loop=by_loop,rows=rows,coefficient_checks=sum(r['coefficient_checks'] for r in rows),model_sha256=sha(HERE/'trained_model/freeze.json'),protocol_sha256=sha(HERE/'test_protocol.json'),reference_preparation_seconds=sum(r['reference_seconds'] for r in rows),training=READ(HERE/'trained_model/selection.json')['selected'])
 collection={}
 for phase in ['training','validation']:
  rs=[READ(q) for q in (HERE/phase).glob('*.json.gz') if q.name!='rows.json.gz']
  collection[phase]=dict(measurements=len(rs),timed_seconds=sum(r['complete_process_and_check_seconds'] for r in rs),verified=sum(r['independently_verified'] for r in rs))
 s['collection']=collection
 write(HERE/'summary.json',s)
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,ax=plt.subplots(1,2,figsize=(10,3.7),gridspec_kw={'width_ratios':[1.4,1]});labels=[];vals=[];intervals=[]
 for g,title in [('all','All completed requests'),('ml','Requests using ML')]:
  for m,name in [('native','native'),('fixed','fixed'),('previous','previous')]:
   v=comp[g][m]
   if not v['cases']:continue
   labels.append(title+' / '+name);vals.append(v['ratio']);intervals.append(v['repeat_interval'])
 for i,(v,(lo,hi)) in enumerate(zip(vals,intervals)):
  ax[0].plot([lo,hi],[i,i],color='#155e75',linewidth=2);ax[0].scatter([v],[i],color='#155e75',s=24)
 ax[0].axvline(1,color='black',ls='--',lw=1);ax[0].set_yticks(range(len(labels)));ax[0].set_yticklabels(labels);ax[0].invert_yaxis();ax[0].set_xlabel('Total-time ratio (smaller is faster)');ax[0].set_title('Matched targets and exact checks')
 allx=[1]+vals+[v for pair in intervals for v in pair];lo,hi=min(allx),max(allx);pad=max(.025,(hi-lo)*.12);ax[0].set_xlim(max(0,lo-pad),hi+pad)
 methods=['previous','native','fixed','learned'];ts=[totals[m]['first_pass_seconds'] for m in methods];bars=ax[1].bar(methods,ts,color=['#9ca3af','#64748b','#94a3b8','#155e75']);ax[1].set_ylabel('Seconds');ax[1].set_title('One attempt for every request');ax[1].set_ylim(0,max(ts)*1.22)
 for bar,m in zip(bars,methods):ax[1].text(bar.get_x()+bar.get_width()/2,bar.get_height()+max(ts)*.02,f"{bar.get_height():.1f}\n{totals[m]['verified_requests']}/{len(rows)}",ha='center',va='bottom',fontsize=8)
 fig.tight_layout();fig.savefig(ROOT/'report/paper_figures/refined_time_selection.pdf',bbox_inches='tight');plt.close(fig)
 print(json.dumps(dict(requested=len(rows),totals=totals,comparisons={g:{m:{k:v for k,v in r.items() if k!='case_ids'} for m,r in cs.items()} for g,cs in comp.items()})),flush=True)
if __name__=='__main__':main()
