"""Summarize all outcomes and paired completed timings without hiding failures."""
from s00_common import *
import numpy as np

def comparison(rows,a,b,scope=None,ml_only=False):
 matched=[r for r in rows if r['nontrivial'] and (scope is None or r['scope']==scope) and (not ml_only or r['model_used']) and r['complete'].get(a) and r['complete'].get(b)]
 if not matched:return dict(cases=0)
 totals={m:sum(r['medians'][m] for r in matched) for m in [a,b]};rng=np.random.default_rng(1313)
 # Resample repetitions within each fixed request. This is not a population interval.
 take=rng.integers(0,3,(2000,len(matched),3));axis=np.arange(len(matched))[None,:,None]
 A=np.array([r['times'][a] for r in matched]);B=np.array([r['times'][b] for r in matched])
 values=np.median(A[axis,take],axis=2).sum(axis=1)/np.median(B[axis,take],axis=2).sum(axis=1)
 ratio=totals[a]/totals[b]
 return dict(cases=len(matched),case_ids=[r['case'] for r in matched],summed_median_seconds=totals,ratio=ratio,speedup=1/ratio,percent_less_time=100*(1-ratio),repeat_interval=np.quantile(values,[.025,.975]).tolist())

def study(base):
 protocol=READ(base/'protocol.json');rows=[];methods=set();checks=0;trials=0;attempts=0;failures=0;maxrss=0;maxscratch=0;attempts_by_method={};failures_by_method={};timed_by_method={};unverified_time_by_method={}
 for c in protocol['cases']:
  cover=READ(base/'coverage'/(c['id']+'.json'));times={};complete={};statuses={};first={};used=False;choices=[];active=False
  for m,record in cover['methods'].items():
   methods.add(m);records=[]
   for rep in range(3):
    f=base/'model_test'/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz')
    if not f.exists():continue
    r=READ(f);records.append(r);trials+=1;checks+=r.get('coefficient_checks',0)
    elapsed=r['complete_process_and_check_seconds'];timed_by_method[m]=timed_by_method.get(m,0)+elapsed
    if not r['independently_verified']:unverified_time_by_method[m]=unverified_time_by_method.get(m,0)+elapsed
    for block in r.get('blocks',[]):
     if block.get('reused'):continue
     br=block['result']
     if m=='learned' and not rep:active=active or nontrivial(br)
     for a in br.get('attempts',[]):
      attempts+=1;failures+=not a.get('success',False);attempts_by_method[m]=attempts_by_method.get(m,0)+1;failures_by_method[m]=failures_by_method.get(m,0)+int(not a.get('success',False));maxrss=max(maxrss,a.get('peak_rss_bytes',0));maxscratch=max(maxscratch,a.get('peak_scratch_bytes',0))
     if m=='learned' and not rep and br.get('model_used'):choices.append(br.get('first_action'))
   complete[m]=len(records)==3 and all(r['independently_verified'] for r in records)
   times[m]=[r['complete_process_and_check_seconds'] for r in records];statuses[m]=[r.get('status') for r in records];first[m]=record
   if m=='learned':used=record['model_used']
  rows.append(dict(case=c['id'],loops=cover['loops'],scope=cover['scope'],family=cover['family'],reference=cover['reference_success'],reference_status=cover['reference_status'],model_used=used,nontrivial=active,first=first,complete=complete,times=times,medians={m:statistics.median(t) for m,t in times.items() if complete[m]},statuses=statuses,learned_actions=choices))
 counts={m:dict(total_timed_seconds=timed_by_method.get(m,0),unverified_timed_seconds=unverified_time_by_method.get(m,0),native_attempts=attempts_by_method.get(m,0),failed_native_attempts=failures_by_method.get(m,0),first_completed=sum(r['first'].get(m,{}).get('completed',False) for r in rows),first_verified=sum(r['first'].get(m,{}).get('verified',False) for r in rows),three_verified=sum(r['complete'].get(m,False) for r in rows),first_unverified_completed=sum(r['first'].get(m,{}).get('completed',False) and not r['first'].get(m,{}).get('verified',False) for r in rows)) for m in sorted(methods)}
 comparisons={}
 for control in sorted(methods-{'learned'}):
  for scope in [None,'coupled_family','independent_loop_blocks','analytic_vacuum','analytic_massless']:
   for ml_only in [False,True]:
    name='learned/'+control+':'+(scope or 'all')+(':ml' if ml_only else '')
    comparisons[name]=comparison(rows,'learned',control,scope,ml_only)
 by_loop={str(L):dict(requested=sum(r['loops']==L for r in rows),coupled=sum(r['loops']==L and r['scope']=='coupled_family' for r in rows),products=sum(r['loops']==L and r['scope']=='independent_loop_blocks' for r in rows),reference=sum(r['loops']==L and r['reference'] for r in rows),verified={m:sum(r['loops']==L and r['complete'].get(m,False) for r in rows) for m in sorted(methods)}) for L in range(1,14)}
 for L,record in by_loop.items():
  subset=[r for r in rows if r['loops']==int(L)]
  record['ml_comparisons']={control:comparison(subset,'learned',control,ml_only=True) for control in ['native','fixed']}
 fixed_action=READ((base/'deployment/fixed.json') if base.name=='extension' else HERE/'trained_model/fixed.json')['action']
 matched_ml=[r for r in rows if r['nontrivial'] and r['complete'].get('learned') and r['complete'].get('fixed') and r['model_used']]
 action_counts=dict(matched_ml_requests=len(matched_ml),changed_from_fixed=sum(any(a!=fixed_action for a in r['learned_actions']) for r in matched_ml),changed_from_native=sum(any(a!='native' for a in r['learned_actions']) for r in matched_ml),fixed_action=fixed_action)
 return dict(action_counts=action_counts,complete=True,requested=len(rows),rows=rows,counts=counts,comparisons=comparisons,by_loop=by_loop,trials=trials,coefficient_checks=checks,native_attempts=attempts,failed_native_attempts=failures,max_native_rss_bytes=maxrss,max_native_scratch_bytes=maxscratch,protocol_sha256=sha(base/'protocol.json'))

def main():
 assert all(READ(HERE/('worker_'+str(i)+'_complete.json'))['complete'] for i in range(2))
 assert all(READ(HERE/'extension'/('worker_'+str(i)+'_complete.json'))['complete'] for i in range(2))
 write(HERE/'extension/complete.json',dict(complete=True,protocol_sha256=sha(HERE/'extension/protocol.json'),model_sha256=sha(HERE/'extension/deployment/freeze.json')))
 initial=study(HERE);final=study(HERE/'extension');selection=READ(HERE/'trained_model/selection.json')
 result=dict(deployment=READ(HERE/'extension/deployment/selection.json'),complete=True,initial=initial,final=final,selection=selection,formulas=READ(HERE/'extension/formula_checks/summary.json'),massless_formulas=READ(HERE/'extension/massless_formula_checks/summary.json'),calibration=READ(HERE/'extension/basis_calibration/summary.json'))
 write(HERE/'summary.json',result)
 report=ROOT/'report';(report/'factorized_data.json').write_text(json.dumps(result,indent=2)+'\n')
 plots(result)
 print(json.dumps(dict(initial_requests=initial['requested'],final_requests=final['requested'],final_counts=final['counts'],final_comparisons={k:v for k,v in final['comparisons'].items() if k.endswith(':all') or k.endswith(':all:ml')},formulas=result['formulas'])),flush=True)

def plots(result):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})
 p=ROOT/'report/paper_figures';p.mkdir(exist_ok=True)
 final=result['final'];fig,axes=plt.subplots(1,2,figsize=(9.6,4.8),gridspec_kw={'width_ratios':[1.5,1]})
 records=[]
 for scope,title in [('all','All ML requests'),('coupled_family','Coupled families'),('independent_loop_blocks','Independent blocks')]:
  for control in ['native','fixed']:
   r=final['comparisons']['learned/'+control+':'+scope+':ml']
   if r['cases']:records.append((title+' / '+control+' ('+str(r['cases'])+')',r))
 ax=axes[0]
 for j,(name,r) in enumerate(records):
  lo,hi=r['repeat_interval'];v=r['ratio'];ax.errorbar(v,j,xerr=[[max(0,v-lo)],[max(0,hi-v)]],fmt='o',capsize=3,color='#235b83')
 ax.set_yticks(range(len(records)));ax.set_yticklabels([r[0] for r in records]);ax.invert_yaxis();ax.axvline(1,color='.5',lw=1,ls='--');ax.set_xlabel('Learned / control time');ax.set_title('Timings when ML is used',fontsize=12)
 bounds=[v for _,r in records for v in [r['ratio'],*r['repeat_interval']]]+[1];pad=max(.025,(max(bounds)-min(bounds))*.12);ax.set_xlim(min(bounds)-pad,max(bounds)+pad)
 ax=axes[1];loops=np.arange(1,14);bottom=np.zeros(13)
 total=np.array([sum(r['loops']==L for r in final['rows']) for L in loops])
 ax.bar(loops,total,width=.78,color='none',edgecolor='.6',linewidth=.8,label='Requested total')
 for scope,label,color in [('independent_loop_blocks','Independent blocks','#235b83'),('coupled_family','Coupled families','#a54b2a'),('analytic_vacuum','One-mass formula','#47734b'),('analytic_massless','Massless formula','#76558a')]:
  values=np.array([sum(r['loops']==L and r['scope']==scope and r['complete']['learned'] for r in final['rows']) for L in loops])
  ax.bar(loops,values,bottom=bottom,width=.62,label=label,color=color);bottom+=values
 ax.set_xticks([1,3,5,7,9,11,13]);ax.set_ylim(0,max(total)+3);ax.set_ylabel('Requests with three exact completions');ax.set_xlabel('Total number of loops');ax.set_title('Coverage through 13 loops',fontsize=12);ax.legend(fontsize=10.5,loc='upper right');fig.tight_layout();fig.savefig(p/'factorized_results.pdf');plt.close(fig)
 # Main grid preserves unsupported coupled high-loop requests explicitly.
 fig,ax=plt.subplots(figsize=(7,3.3));x=np.arange(1,14)
 for shift,scope,title,color in [(-.18,'coupled_family','Coupled families','#a54b2a'),(.18,'independent_loop_blocks','Independent blocks','#235b83')]:
  rs=result['initial']['rows'];values=[];totals=[]
  for L in x:
   selected=[r for r in rs if r['loops']==L and r['scope']==scope];totals.append(len(selected));values.append(sum(r['complete']['learned'] for r in selected))
  ax.bar(x+shift,totals,width=.33,color=color,alpha=.18);ax.bar(x+shift,values,width=.33,color=color,label=title)
 ax.set_xticks(x);ax.set_xlabel('Total number of loops');ax.set_ylabel('Requests');ax.set_ylim(0,max(sum(r['loops']==L and r['scope']==scope for r in result['initial']['rows']) for L in x for scope in ['coupled_family','independent_loop_blocks'])+.7);ax.set_title('Initial coverage: solid bars pass all three exact checks');ax.legend();fig.tight_layout();fig.savefig(p/'factorized_coverage.pdf');plt.close(fig)

if __name__=='__main__':main()
