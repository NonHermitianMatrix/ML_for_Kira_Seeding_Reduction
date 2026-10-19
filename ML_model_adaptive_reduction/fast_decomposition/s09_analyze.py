"""Summarize frozen timings and every bounded coverage outcome."""
from s00_fast_common import *
from collections import Counter

def main():
 import numpy as np
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 for w in [0,1]:assert read(HERE/f'worker_{w}_complete.json')['complete']
 p=read(HERE/'protocol.json');rows=[];totals={m:dict(first_seconds=0.,all_seconds=0.,verified=0,failed_first_seconds=0.,coefficient_checks=0,model_requests=0,changed_pivot_requests=0) for m in p['methods']}
 for c in p['timing']:
  row=read(HERE/'coverage'/(c['id']+'.json'));row.update(times={},verified={},routes={},models={},pivots={})
  for m in p['methods']:
   rs=[read(q) for q in sorted((HERE/'model_test').glob(c['id']+'_'+m+'_r*.json.gz'))];assert rs
   ts=[r['complete_process_and_check_seconds'] for r in rs];ok=len(rs)==3 and all(r['independently_verified'] for r in rs)
   row['times'][m]=ts;row['verified'][m]=ok;row['models'][m]=any(r.get('model_used',False) for r in rs)
   row['routes'][m]=sorted({str(b['result'].get('route','native')) for r in rs for b in r.get('blocks',[])})
   row['pivots'][m]=sorted({b['result']['pivot'] for r in rs for b in r.get('blocks',[]) if 'pivot' in b['result']})
   t=totals[m];t['first_seconds']+=ts[0];t['all_seconds']+=sum(ts);t['verified']+=ok;t['failed_first_seconds']+=ts[0] if not rs[0]['independently_verified'] else 0
   t['coefficient_checks']+=sum(r['coefficient_checks'] for r in rs);t['model_requests']+=row['models'][m];t['changed_pivot_requests']+=any(a!='last' for a in row['pivots'][m])
  rows.append(row)
 def compare(control,selected):
  selected=[r for r in selected if r['verified']['learned'] and r['verified'][control]]
  if not selected:return dict(cases=0)
  x=np.array([r['times']['learned'] for r in selected]);y=np.array([r['times'][control] for r in selected]);a=float(np.median(x,axis=1).sum());b=float(np.median(y,axis=1).sum())
  ix=np.random.RandomState(2903).randint(0,3,(2000,len(selected),3));ii=np.arange(len(selected))[None,:,None];rat=np.median(x[ii,ix],axis=2).sum(1)/np.median(y[ii,ix],axis=2).sum(1)
  return dict(cases=len(selected),case_ids=[r['case'] for r in selected],learned_seconds=a,control_seconds=b,ratio=a/b,speedup=b/a,reduction_percent=100*(1-a/b),repeat_interval=list(map(float,np.quantile(rat,[.025,.975]))))
 groups={'all':rows,**{k:[r for r in rows if r['scope']==k] for k in sorted({r['scope'] for r in rows})}}
 groups['exact']=[r for r in rows if r['scope'] in ['finite_formula','products','recurrence','symbolic_formula']]
 groups['new_model_admitted']=[r for r in rows if r['models']['learned'] and r['pivots']['learned']]
 groups['new_model_changed']=[r for r in rows if any(a!='last' for a in r['pivots']['learned'])]
 comparisons={k:{m:compare(m,rr) for m in ['previous','native','fixed']} for k,rr in groups.items()}
 audit=[read(HERE/'audit'/(c['id']+'.json')) for c in p['coverage']]
 assert len(audit)==110 and len(rows)==65
 def audit_group(rr):
  return dict(requests=len(rr),paired_verified=sum(r['paired_verified'] for r in rr),methods={m:dict(successes=sum(r['methods'][m]['success'] for r in rr),seconds=sum(r['methods'][m]['seconds'] for r in rr),statuses=dict(Counter(r['methods'][m]['status'] for r in rr)),block_statuses=dict(Counter(x for r in rr for x in r['methods'][m]['block_statuses']))) for m in ['learned','previous']})
 coverage=dict(total=audit_group(audit),by_loop={str(L):audit_group([r for r in audit if r['loops']==L]) for L in range(1,14)},by_scope={s:audit_group([r for r in audit if r['scope']==s]) for s in sorted({r['scope'] for r in audit})},rows=audit)
 summary=dict(complete=True,requests=65,rows=rows,totals=totals,comparisons=comparisons,coverage=coverage,reference_seconds=sum(r['reference_seconds'] for r in rows),model_selection={k:v for k,v in read(HERE/'trained_model/recurrence.json').items() if k!='trees'},protocol_sha256=sha(HERE/'protocol.json'))
 write(HERE/'summary.json',summary)
 plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,axes=plt.subplots(1,2,figsize=(9.2,3.8))
 names=[('finite_formula','Vacuum and propagator formulas'),('symbolic_formula','Symbolic one-mass vacua'),('products','Distinct triangle products'),('recurrence','Scalar recurrence'),('learned_native','Nonplanar seed model'),('all','All matched requests')]
 for ax,control,title in [(axes[0],'previous','Complete time versus preceding application'),(axes[1],'fixed','Learned choices versus fast fixed choices')]:
  vals=[]
  for i,(key,name) in enumerate(names):
   v=comparisons[key][control]
   if not v['cases']:continue
   lo,hi=v['repeat_interval'];ax.plot([lo,hi],[i,i],color='#126478',lw=2);ax.scatter([v['ratio']],[i],color='#126478',s=24);vals.extend([lo,hi])
  ax.set_yticks(range(len(names)));ax.set_yticklabels([n for k,n in names] if ax==axes[0] else []);ax.invert_yaxis();ax.axvline(1,color='black',ls='--',lw=1);ax.set_xlim(max(0,min(vals)-.06),max(1,max(vals))+.06);ax.set_xlabel('Time ratio (less than one is faster)');ax.set_title(title,fontsize=9)
 fig.tight_layout();fig.savefig(ROOT/'report/paper_figures/fast_decomposition.pdf',bbox_inches='tight');plt.close(fig)
 # The grid displays unsupported outcomes as explicitly as successful ones.
 scopes=['coverage_vacuum_one_mass','coverage_vacuum_all_mass','coverage_propagator_massless','coverage_propagator_massive','coverage_ladder','coverage_bubble_box','coverage_scaleless']
 labels=['One-mass vacuum','All-mass vacuum','Massless propagator','Massive propagator','Scattering ladder','Box with bubble chain','Scaleless vacuum']
 matrix=np.full((len(scopes),13),-1.)
 for i,s in enumerate(scopes):
  for r in audit:
   if r['scope']==s:matrix[i,r['loops']-1]=2 if r['paired_verified'] else 1 if r['methods']['learned']['success'] else 0
 from matplotlib.colors import ListedColormap,BoundaryNorm
 from matplotlib.patches import Patch
 fig,ax=plt.subplots(figsize=(9,3.6));colors=['#e5e7eb','#ca6b51','#d6b85c','#237a82'];cmap=ListedColormap(colors);ax.imshow(matrix,cmap=cmap,norm=BoundaryNorm([-1.5,-.5,.5,1.5,2.5],4),aspect='auto')
 ax.set_xticks(range(13));ax.set_xticklabels(range(1,14));ax.set_yticks(range(len(scopes)));ax.set_yticklabels(labels);ax.set_xlabel('Number of loops');ax.set_title('Analytic families extend farther than general connected reductions')
 ax.legend(handles=[Patch(color=colors[3],label='Both complete; exact agreement'),Patch(color=colors[2],label='New application only'),Patch(color=colors[1],label='New application incomplete'),Patch(color=colors[0],label='Duplicate definition omitted')],loc='upper center',bbox_to_anchor=(.4,-.25),ncol=2,frameon=False,fontsize=8)
 fig.tight_layout();fig.savefig(ROOT/'report/paper_figures/fast_coverage.pdf',bbox_inches='tight');plt.close(fig)
 print(json.dumps(dict(requests=65,totals=totals,all=comparisons['all'],recurrence=comparisons['recurrence']['fixed'],coverage=coverage['total'])),flush=True)
if __name__=='__main__':main()
