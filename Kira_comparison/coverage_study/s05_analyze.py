"""Audit coverage and compare only matched completed reductions."""
import collections,gzip,hashlib,json,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPORT=ROOT/'report'
def read(p):
    raw=p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
NAMES={'vacuum_one_mass':'One-mass vacuum','vacuum_all_mass':'Massive vacuum','propagator_massless':'Massless two-point','propagator_massive':'Massive two-point','ladder':'Four-point ladder','bubble_box':'Box with bubbles','nonplanar_box':'Nonplanar box','pentagon':'Pentagon','one_mass_box':'Virtuality box'}
PAIRS={'full_original':['full_original','full_revised'],'full_previous':['full_previous','full_revised'],'application_previous':['previous','selected'],'application_native':['native','selected']}
def main():
    import sympy as sp
    equality_cache=set()
    def same(a,b):
        if a==b:return
        key=(a,b)
        if key not in equality_cache:
            assert sp.cancel(sp.sympify(a.replace('^','**'),rational=True)-sp.sympify(b.replace('^','**'),rational=True))==0,key
            equality_cache.add(key)
    def exact_rows(got,want):
        assert set(got)==set(want)
        for t,row in got.items():
            for m in set(row)|set(want[t]):same(row.get(m,'0'),want[t].get(m,'0'))
    assert read(HERE/'completion.json')['complete'] and read(HERE/'vacuum_completion.json')['complete']
    follow=HERE/'nontrivial_followup';assert read(follow/'completion.json')['complete']
    supplemental=read(follow/'protocol.json')
    assert sha(HERE/'s08_nontrivial.py')==supplemental['source_sha256']
    assert sha(HERE/'s01_study.py')==supplemental['base_study_sha256']
    protocol=read(HERE/'protocol.json');cases=protocol['cases']+supplemental['cases'];records=[];checks=0;peak=0;timed=0;success=0;limits=collections.Counter()
    def scan_limits(d):
        if isinstance(d,dict):
            if isinstance(d.get('limits'),dict):
                limit=d['limits'].get('complete_timeout_seconds')
                if limit is not None:limits[str(limit)]+=1
            for v in d.values():scan_limits(v)
        elif isinstance(d,list):
            for v in d:scan_limits(v)
    for n,h in protocol['sources'].items():assert sha(HERE/n)==h,n
    for n,h in protocol['application_sources'].items():assert sha(ROOT/'ML_model_adaptive_reduction'/n)==h,n
    for n,h in protocol['models'].items():assert sha(ROOT/n)==h,n
    for n,h in protocol['binaries'].items():assert sha(ROOT/'.tools'/n/'kira')==h,n
    for c in cases:
        folder=follow if c.get('coverage_stage')=='nontrivial_followup' else HERE
        coverage=read(folder/'coverage'/(c['id']+'.json'))
        r=dict(case=c['id'],kind=c['coverage_type'],loops=c['loops'],kinematics=c['kinematics'],indices=c['scalar_product_count'],coverage=coverage,methods={})
        ref=folder/'references'/(c['id']+'.json.gz');check=folder/'references'/(c['id']+'_check.json.gz')
        r['reference_verified']=ref.exists() and check.exists() and read(ref)['success'] and read(check)['success'] and read(check).get('reference_checked',False)
        if check.exists():checks+=read(check).get('coefficient_checks',0)
        if r['reference_verified']:exact_rows(read(check)['coefficients'],read(ref)['coefficients'])
        for method in protocol['methods']:
            samples=[]
            for rep in range(3):
                p=folder/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz'
                if not p.exists():continue
                d=read(p);assert d['method']==method and d['repetition']==rep;scan_limits(d)
                timed+=1;checks+=d.get('coefficient_checks',0);success+=int(d['success'])
                peak=max(peak,d.get('peak_rss_bytes',0),max([a.get('peak_rss_bytes',0) for a in d.get('attempts',[])]+[0]))
                if d['success']:
                    assert d['reference_checked'] and not d['mismatches']
                    exact_rows(d['coefficients'],read(ref)['coefficients'])
                samples.append(dict(seconds=d['complete_seconds'],success=d['success'],status=d.get('status'),fallbacks=d.get('fallback_count',0),action=d.get('action'),reason=d.get('selection_reason'),decision_seconds=d.get('decision_seconds',0.),resolution_seconds=d.get('family_resolution_seconds',0.)))
            r['methods'][method]=dict(samples=samples,complete=len(samples)==3 and all(x['success'] for x in samples))
            if r['methods'][method]['complete']:r['methods'][method]['median']=statistics.median(x['seconds'] for x in samples)
        records.append(r)
    names=HERE/'family_names';assert read(names/'completion.json')['complete']
    name_protocol=read(names/'protocol.json')
    assert sha(HERE/'s09_family_names.py')==name_protocol['source_sha256']
    assert sha(ROOT/'ML_model_adaptive_reduction/selective_expansion/trained_model/freeze.json')==name_protocol['model_sha256']
    for c in name_protocol['cases']:
        r=next(r for r in records if r['case']==c['id']);r['supplied_name_methods']={m:r['methods'][m] for m in name_protocol['methods']}
        ref=HERE/'references'/(c['id']+'.json.gz')
        for method in name_protocol['methods']:
            samples=[]
            for rep in range(3):
                d=read(names/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz');scan_limits(d)
                timed+=1;success+=int(d['success']);checks+=d.get('coefficient_checks',0)
                peak=max(peak,max([a.get('peak_rss_bytes',0) for a in d.get('attempts',[])]+[0]))
                assert d['success'] and d['reference_checked']
                exact_rows(d['coefficients'],read(ref)['coefficients'])
                samples.append(dict(seconds=d['complete_seconds'],success=d['success'],status=d.get('status'),fallbacks=d.get('fallback_count',0),action=d.get('action'),reason=d.get('selection_reason'),decision_seconds=d.get('decision_seconds',0.),resolution_seconds=d.get('family_resolution_seconds',0.)))
            r['methods'][method]=dict(samples=samples,complete=True,median=statistics.median(x['seconds'] for x in samples),family_name_resolved=True)
        r['family_name_resolved']=True
    paired={}
    for name,(a,b) in PAIRS.items():
        group=[r for r in records if r['reference_verified'] and r['coverage'].get('nontrivial') and r['methods'][a]['complete'] and r['methods'][b]['complete']]
        old=sum(r['methods'][a]['median'] for r in group);new=sum(r['methods'][b]['median'] for r in group)
        allold=sum(x['seconds'] for r in group for x in r['methods'][a]['samples']);allnew=sum(x['seconds'] for r in group for x in r['methods'][b]['samples'])
        by={}
        for kind in NAMES:
            items=[r for r in group if r['kind']==kind]
            if items:by[kind]=dict(cases=len(items),previous=sum(r['methods'][a]['median'] for r in items),revised=sum(r['methods'][b]['median'] for r in items))
        paired[name]=dict(baseline=a,revised=b,cases=[r['case'] for r in group],count=len(group),previous=old,revised_seconds=new,ratio=new/old if old else None,all_repetitions_ratio=allnew/allold if allold else None,by_type=by,slower_cases=[r['case'] for r in group if r['methods'][b]['median']>r['methods'][a]['median']])
    vp=read(HERE/'vacuum_protocol.json');assert sha(HERE/'s03_vacuum.py')==vp['source_sha256']
    high=ROOT/'ML_model_equation_selection/higher_loops';exact=ROOT/'ML_model_equation_selection/exact_backend'
    assert sha(high/'trained_model'/vp['model'])==vp['model_sha256']
    assert sha(high/'s02_reduce.py')==vp['previous_source_sha256']
    assert sha(exact/'trained_model/cost_tree.json')==vp['exact_model_sha256']
    assert sha(ROOT/'.tools/kira/bin/kira')==vp['original_binary_sha256']
    vf=list((HERE/'vacuum_test').glob('*.json.gz'));assert len(vf)==read(HERE/'vacuum_completion.json')['requests']
    vacuum=[]
    for c in vp['cases']:
        for loops in [[L] for L in range(1,13)]+[list(range(1,13))]:
            label=str(loops[0]) if len(loops)==1 else 'shared';row=dict(case=c['id'],loops=loops,methods={})
            for mode in vp['modes']:
                ds=[read(HERE/'vacuum_test'/f'{c["id"]}_{label}_{mode}_{rep}.json.gz') for rep in range(3)]
                checks+=sum(d.get('coefficient_checks',0) for d in ds)
                row['methods'][mode]=dict(success=all(d['success'] for d in ds),seconds=[d['complete_seconds'] for d in ds])
                if all(d['success'] for d in ds):row['methods'][mode]['median']=statistics.median(d['complete_seconds'] for d in ds)
            vacuum.append(row)
    vt={}
    for group in ['individual','shared']:
        rs=[r for r in vacuum if (len(r['loops'])==1)==(group=='individual') and all(v['success'] for v in r['methods'].values())]
        vt[group]=dict(cases=len(rs),totals={m:sum(r['methods'][m]['median'] for r in rs) for m in vp['modes']})
    statuses=dict(collections.Counter(r['coverage']['status'] for r in records))
    completion={}
    for m in protocol['methods']:
        first=[r['methods'][m]['samples'][0] for r in records if r['methods'][m]['samples']]
        completion[m]=dict(first_requests=len(first),first_successes=sum(x['success'] for x in first),first_complete_seconds=sum(x['seconds'] for x in first),all_three_successes=sum(r['methods'][m]['complete'] for r in records))
    result=dict(complete=True,all_successful_outputs_exact=True,native_cases=len(cases),eligible=sum(c['preflight']=='eligible' for c in cases),status_counts=statuses,native_timed=timed,native_successful=success,native_failed=timed-success,reference_verified=sum(r['reference_verified'] for r in records),full_revised_verified=sum(r['methods']['full_revised']['complete'] for r in records),selected_verified=sum(r['methods']['selected']['complete'] for r in records),coefficient_checks=checks,peak_timed_rss_bytes=peak,paired=paired,method_completion=completion,cases=records,vacuum=vacuum,vacuum_totals=vt,vacuum_requests=len(vf),vacuum_successful=sum(read(p)['success'] for p in vf),scope='Finite quadratic-propagator families through twelve loops; no claim of all integral types or arbitrary loop order.')
    result['recorded_attempt_limits']=dict(limits)
    result['initial_cases']=len(protocol['cases']);result['followup_cases']=len(supplemental['cases'])
    result['resolved_family_cases']=len(name_protocol['cases'])
    result['nontrivial_full_revised_verified']=sum(r['methods']['full_revised']['complete'] and bool(r['coverage'].get('nontrivial')) for r in records)
    result['identity_only_full_revised_verified']=sum(r['methods']['full_revised']['complete'] and not r['coverage'].get('nontrivial') for r in records)
    result['independent_native_equality_pairs']=len(equality_cache)
    result['saved_native_coefficients_rechecked']=True
    result['vacuum_coefficient_audit']=read(HERE/'coefficient_audit.json')
    assert result['vacuum_coefficient_audit']['all_successful_saved_outputs_verified']
    group=[r for r in records if r['case'] in paired['application_native']['cases']]
    optimistic=sum(statistics.median(max(0.,x['seconds']-x['decision_seconds']-x['resolution_seconds']) for x in r['methods']['native']['samples']) for r in group)
    result['native_control_sensitivity']=dict(optimistic_seconds=optimistic,selected_over_optimistic=paired['application_native']['revised_seconds']/optimistic,maximum_removed_seconds=max(x['decision_seconds']+x['resolution_seconds'] for r in group for x in r['methods']['native']['samples']),note='Remove the entire recorded input-check/proposal interval and exact family lookup from native controls; retain all selected costs. This is an optimistic bound, not a separately measured native implementation.')
    write(HERE/'summary.json',result);write(REPORT/'coverage_data.json',result)
    plot(result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['cases','vacuum','paired']},indent=2),flush=True)
def plot(data):
    import os
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.tools/paper-mpl'))
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap,BoundaryNorm
    from matplotlib.patches import Patch
    import numpy as np
    plt.rcParams.update({'font.size':12,'pdf.fonttype':42,'ps.fonttype':42})
    kinds=list(NAMES);grid=np.zeros((len(kinds),12),dtype=int)
    for r in data['cases']:
        if r['kinematics']!='rational':continue
        code=3 if r['coverage']['status']=='unsupported_index_count' else (1 if r['coverage'].get('nontrivial') else 4) if r['methods']['full_revised']['complete'] else 2
        i,j=kinds.index(r['kind']),r['loops']-1
        priority={0:0,3:1,2:2,4:3,1:4}
        if priority[code]>priority[int(grid[i,j])]:grid[i,j]=code
    cmap=ListedColormap(['#f2f2f2','#2471a3','#e8a044','#9b9b9b','#b9d5c5'])
    fig,ax=plt.subplots(figsize=(9.2,4.8),constrained_layout=True)
    ax.imshow(grid,cmap=cmap,norm=BoundaryNorm([-.5,.5,1.5,2.5,3.5,4.5],5),aspect='auto')
    ax.set_xticks(range(12));ax.set_xticklabels(range(1,13));ax.set_xlabel('Number of loops')
    ax.set_yticks(range(len(kinds)));ax.set_yticklabels([NAMES[k] for k in kinds])
    ax.set_title('Native IBP coverage: successful calculations and remaining limits')
    ax.set_xticks(np.arange(-.5,12,1),minor=True);ax.set_yticks(np.arange(-.5,len(kinds),1),minor=True);ax.grid(which='minor',color='white',linewidth=2);ax.tick_params(which='minor',bottom=False,left=False)
    ax.legend(handles=[Patch(color=cmap(i),label=l) for i,l in enumerate(['Not in this grid','Nontrivial full reduction verified','Reference or calculation failed','Current index limit','Only identity outputs verified'])],loc='upper center',bbox_to_anchor=(.5,-.13),ncol=2,frameon=False,fontsize=10)
    fig.savefig(REPORT/'paper_figures/coverage_grid.pdf');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9.2,4.8),constrained_layout=True)
    pairs=[('full_original','Full: original Kira'),('full_previous','Full: previous build'),('application_previous','Basis supplied: previous'),('application_native','Basis supplied: native')]
    ax=axes[0];ys=np.arange(len(pairs))
    for i,(k,label) in enumerate(pairs):
        p=data['paired'][k]
        ax.scatter(p['ratio'],i,color='#2471a3',s=45)
    ax.axvline(1,color='black',ls='--',lw=1)
    ax.set_xlim(0,max(1.1,max(data['paired'][k]['ratio'] for k,_ in pairs)*1.12));ax.set_ylim(-.5,len(pairs)-.5)
    ax.set_yticks(ys);ax.set_yticklabels([f'{label}\n(n={data["paired"][k]["count"]})' for k,label in pairs],fontsize=10);ax.set_xlabel('Revised / control time');ax.set_title('Matched native requests');ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
    ax=axes[1];rs=[r for r in data['vacuum'] if len(r['loops'])==1 and all(v['success'] for v in r['methods'].values())]
    for mode,label,color in [('original','Original Kira','#999999'),('learned','Learned equation choice','#ad7a20'),('extreme','Fixed equation choice','#188a70'),('recurrence','Exact recurrence','#2471a3')]:
        points=[sum(r['methods'][mode]['median'] for r in rs if r['loops']==[L]) for L in range(1,13)]
        ax.plot(range(1,13),points,'o-',markersize=3,label=label,color=color)
    ax.set_yscale('log');ax.set_xlabel('Number of loops');ax.set_ylabel('Sum of batch medians (seconds)');ax.set_title('Restricted vacuum identities');ax.set_xticks([1,3,5,7,9,12]);ax.grid(alpha=.2);ax.legend(fontsize=9)
    fig.savefig(REPORT/'paper_figures/coverage_times.pdf');plt.close(fig)
if __name__=='__main__':main()
