"""Audit new results and plot complete costs against native and fixed controls."""
import collections,datetime,hashlib,json,statistics
from pathlib import Path
import s05_study as study
import s12_graph_policy as graph_policy
rt=study.rt;HERE=rt.HERE;ROOT=rt.ROOT
def main():
    p=json.loads((HERE/'cases.json').read_text());f=json.loads((HERE/'trained_model/freeze.json').read_text())
    protocol=json.loads((HERE/'graph_control_protocol.json').read_text())
    registered=datetime.datetime.fromisoformat(protocol['sources_registered_utc']).timestamp()
    first_reserved=min(path.stat().st_mtime for path in (HERE/'model_test').glob('*.json.gz'))
    assert registered<first_reserved
    def check_binary(record):
        for attempt in record.get('attempts',[record]):
            if 'binary_sha256' in attempt:assert attempt['binary_sha256']==f['binary_sha256']
    for path,key in [(HERE/'cases.json','cases_sha256'),(HERE/'s02_runtime.py','runtime_sha256'),(HERE/'s05_study.py','study_sha256'),(ROOT/'.tools/kira-adaptive/kira','binary_sha256')]:assert study.sha(path)==f[key]
    if (HERE/'followup_cases.json').exists():p['cases']+=json.loads((HERE/'followup_cases.json').read_text())['cases']
    cases=[];unfinished=[];workflows=applications=checks=0
    for c in p['cases']:
        if c['split']!='reserved':continue
        ref=HERE/'references'/(c['id']+'.json.gz');check=HERE/'references'/(c['id']+'_check.json.gz')
        if not ref.exists() or not rt.read(ref)['success'] or not check.exists() or not rt.read(check)['success']:
            unfinished.append(dict(case=c['id'],reference_status=rt.read(ref)['status'] if ref.exists() else 'not_started',check_status=rt.read(check)['status'] if check.exists() else 'not_started'));continue
        methods={}
        for method in ['native','fixed','learned']:
            records=[rt.read(HERE/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz') for rep in range(3)]
            assert all(r['success'] and r['reference_checked'] and not r['mismatches'] for r in records)
            if method=='learned':assert all(r['action']==study.select(f,c) for r in records)
            methods[method]=dict(median_seconds=statistics.median(r['complete_seconds'] for r in records),
                seconds=[r['complete_seconds'] for r in records],fallbacks=sum(r['fallback_count'] for r in records),
                decisions=[r['action'] for r in records],median_decision_seconds=statistics.median(r['decision_seconds'] for r in records))
            workflows+=len(records);checks+=sum(r['coefficient_checks'] for r in records)
        app=rt.read(HERE/'model_test'/f'{c["id"]}_application.json.gz')
        assert app['success'] and app['reference_checked'] and app['answers_withheld'];applications+=1;checks+=app['coefficient_checks']
        cases.append(dict(case=c['id'],graph=c['topology_group'],loops=len(c['definition']['loop_momenta']),symbolic=bool(c['definition']['invariants']),targets=c['size'],methods=methods,conditional_confirmation=c.get('conditional_confirmation',False)))
    assert cases
    totals={m:sum(c['methods'][m]['median_seconds'] for c in cases) for m in ['native','fixed','learned']}
    trial_totals={m:sum(sum(c['methods'][m]['seconds']) for c in cases) for m in totals}
    groups={}
    for key in sorted({c['graph'] for c in cases}):
        rows=[c for c in cases if c['graph']==key];groups[key]=dict(cases=len(rows),loops=rows[0]['loops'],seconds={m:sum(c['methods'][m]['median_seconds'] for c in rows) for m in totals},
            learned_actions=dict(collections.Counter(c['methods']['learned']['decisions'][0] for c in rows)))
    splits={s:[c for c in p['cases'] if c['split']==s] for s in ['training','validation','reserved']}
    for a,b in [('training','validation'),('training','reserved'),('validation','reserved')]:
        assert not ({c['group'] for c in splits[a]} & {c['group'] for c in splits[b]})
    counts={s:sum(study.available(c,s,1 if s=='training' else 2) for c in splits[s]) for s in ['training','validation']}
    offline_seconds=0.
    for folder in ['training','validation']:
        offline_seconds+=sum(rt.read(path)['complete_seconds'] for path in (HERE/folder).glob('*.json.gz'))
        for c in splits[folder]:
            path=HERE/'references'/(c['id']+'.json.gz')
            if path.exists():offline_seconds+=rt.read(path)['complete_seconds']
    fitting_seconds=json.loads((HERE/'trained_model/candidates.json').read_text())['training_seconds']
    all_records=[]
    for folder in ['training','validation','model_test']:
        for path in (HERE/folder).glob('*.json.gz'):
            r=rt.read(path);assert r['success'] and r['reference_checked'] and not r['mismatches'];check_binary(r);all_records.append(r)
    public=[];integration=[]
    for graph in sorted({c['graph'] for c in cases}):
        example=next(c for c in cases if c['graph']==graph)
        path=HERE/'application_test'/(example['case']+'.json.gz');r=rt.read(path)
        assert r['success'] and r['reference_checked'] and not r['answers_supplied']
        public.append(dict(case=example['case'],action=r['action'],seconds=r['application_seconds'],
            policy_supported=r['policy_supported'],choice_seconds=r['choice_seconds']))
        if graph in ['bubble_box3','bubble_box4']:
            methods={}
            for method in ['previous','files','projected','learned']:
                paths=[HERE/'integration_test'/f'{example["case"]}_{method}_{i}.json.gz' for i in range(3)]
                rows=[rt.read(p) for p in paths if p.exists()]
                complete=all(r['success'] and r['reference_checked'] for r in rows) and len(rows)==3
                if not complete:
                    continuation=json.loads((HERE/'integration_completion.json').read_text())
                    assert continuation['complete'] and example['case']+':'+method in continuation['failed_controls']
                    assert any(not r['success'] for r in rows)
                good=[r for r in rows if r['success'] and r['reference_checked']]
                for r in rows:check_binary(r)
                methods[method]=dict(complete=complete,seconds=[r['complete_seconds'] for r in good],
                    median_seconds=statistics.median(r['complete_seconds'] for r in good) if complete else None,
                    failed_seconds=[r['complete_seconds'] for r in rows if not r['success']],
                    failed_statuses=[[a['status'] for a in r['attempts']] for r in rows if not r['success']],
                    omitted_repetitions=3-len(rows))
            integration.append(dict(case=example['case'],loops=example['loops'],methods=methods))
    guard=rt.read(HERE/'application_test/unsupported_graph_guard.json.gz')
    assert guard['success'] and guard['reference_checked'] and not guard['policy_supported'] and guard['action']=='native'
    graph_guard=graph_policy.freeze(p['cases'],f)
    graph_cases=[]
    for c in cases:
        original=next(q for q in p['cases'] if q['id']==c['case'])
        methods={}
        for method in ['graph_fixed','learned','guarded']:
            rows=[rt.read(HERE/'graph_control_test'/f'{c["case"]}_{method}_{rep}.json.gz') for rep in range(3)]
            expected=graph_guard['graphs'][c['graph']]['fixed'] if method=='graph_fixed' else study.select(f,original) if method=='learned' else graph_policy.select(f,graph_guard,original)
            assert all(r['success'] and r['reference_checked'] and r['action']==expected for r in rows)
            for r in rows:check_binary(r)
            methods[method]=dict(median_seconds=statistics.median(r['complete_seconds'] for r in rows),
                seconds=[r['complete_seconds'] for r in rows],action=expected,
                median_decision_seconds=statistics.median(r['decision_seconds'] for r in rows),
                fallbacks=sum(r['fallback_count'] for r in rows))
        graph_cases.append(dict(case=c['case'],graph=c['graph'],methods=methods))
    graph_totals={m:sum(c['methods'][m]['median_seconds'] for c in graph_cases) for m in ['graph_fixed','learned','guarded']}
    graph_trials={m:sum(sum(c['methods'][m]['seconds']) for c in graph_cases) for m in graph_totals}
    graph_groups={g:{m:sum(c['methods'][m]['median_seconds'] for c in graph_cases if c['graph']==g) for m in graph_totals} for g in groups}
    guard_summary={g:({k:v for k,v in row.items() if k!='model'} | {'model_name':row['model']['name'],'trees':len(row['model']['trees'])}) for g,row in graph_guard['graphs'].items()}
    feature_names=json.loads((HERE/'trained_model/graph_candidates.json').read_text())['features']
    for g,row in graph_guard['graphs'].items():
        used=sorted({i for tree in row['model']['trees'] for i in tree['feature'] if i>=0})
        guard_summary[g]['split_features']=[feature_names[i] for i in used]
    experts=json.loads((HERE/'trained_model/graph_candidates.json').read_text())
    out=dict(complete=True,all_exact=True,cases=cases,unfinished=unfinished,by_graph=groups,totals=totals,
        graph_procedure_recorded_before_reserved_timings=True,
        unsupported_graph_guard=dict(complete=True,all_exact=True,action=guard['action'],seconds=guard['application_seconds']),
        graph_controls=dict(cases=graph_cases,totals=graph_totals,all_trial_totals=graph_trials,by_graph=graph_groups,
            guard=dict(graphs=guard_summary,minimum_saving=.02,selection_data='validation only'),
            expert_candidates=experts['candidates'],expert_fitting_seconds=experts['training_seconds'],
            workflows=9*len(graph_cases),all_exact=True,
            fallback_totals={m:sum(c['methods'][m]['fallbacks'] for c in graph_cases) for m in graph_totals},
            learned_to_fixed=graph_totals['learned']/graph_totals['graph_fixed'],
            guarded_to_fixed=graph_totals['guarded']/graph_totals['graph_fixed'],
            enabled_graphs=[g for g,v in graph_guard['graphs'].items() if v['enabled']]),
        all_trial_totals=trial_totals,
        all_trial_learned_to_native=trial_totals['learned']/trial_totals['native'],
        all_trial_learned_to_fixed=trial_totals['learned']/trial_totals['fixed'],
        learned_to_native=totals['learned']/totals['native'],learned_to_fixed=totals['learned']/totals['fixed'],
        workflows=workflows,applications=applications,coefficient_checks=checks,all_checked_records=len(all_records),
        training_cases=counts['training'],validation_cases=counts['validation'],test_cases=len(cases),
        offline_recorded_reduction_seconds=offline_seconds,fitting_seconds=fitting_seconds,
        model=f['model']['name'],trees=len(f['model']['trees']),gate=f['gate'],best_fixed=f['best_fixed'],
        validation=f['validation'],validation_fixed_seconds=f['validation_fixed_seconds'],
        timing=p['timing'],scope=p['split_rule'],freeze_sha256=study.sha(HERE/'trained_model/freeze.json'),
        comparison='Same improved native executable and exact basis for all methods. Thus learned/fixed isolates the learned choice from deterministic preprocessing.',
        inference_median_seconds=statistics.median(c['methods']['learned']['median_decision_seconds'] for c in cases),
        fallback_totals={m:sum(c['methods'][m]['fallbacks'] for c in cases) for m in totals},
        learned_actions=dict(collections.Counter(c['methods']['learned']['decisions'][0] for c in cases)),
        public_applications=public,integration=integration,
        conditional_confirmation=any(c['conditional_confirmation'] for c in cases),
        uncertainty='Three repetitions per test method. Per-case ranges are descriptive; no confidence-level or universal-speedup claim.')
    study.write(HERE/'summary.json',out);study.write(ROOT/'report/adaptive_reduction_data.json',out)
    plot(out);print(json.dumps({k:out[k] for k in ['complete','model','training_cases','validation_cases','test_cases','totals','learned_to_native','learned_to_fixed']}),flush=True)
def plot(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    names={'one_mass_box':'Virtuality box','nonplanar_box':'Nonplanar box','double_box':'Planar double box','sunrise':'Sunrise','pentagon':'Pentagon','vacuum3':'Three-loop vacuum','ladder3':'Three-loop two-point ladder','bubble_box3':'Three-loop bubble box','bubble_box4':'Four-loop bubble box'}
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axs=plt.subplots(2,1,figsize=(7.2,6.5),constrained_layout=True)
    rows=list(d['by_graph'].items());y=list(range(len(rows)))
    for ax,den,title in zip(axs,['native','fixed'],['Complete reduction time relative to native choices','Added effect relative to the validation-selected fixed setting']):
        x=[v['seconds']['learned']/v['seconds'][den] for k,v in rows]
        ax.axvline(1,color='#555555',linestyle='--',lw=1)
        ax.scatter(x,y,color='#176e8d',s=34,zorder=3)
        ax.set_yticks(y);ax.set_yticklabels([names.get(k,k) for k,v in rows]);ax.invert_yaxis()
        low=min(x+[1]);high=max(x+[1]);pad=max(.025,(high-low)*.15)
        ax.set_xlim(max(0,low-pad),high+pad);ax.set_xlabel('Learned time / control time (smaller is faster)');ax.set_title(title,fontsize=11)
        ax.grid(axis='x',alpha=.2)
    fig.savefig(ROOT/'report/paper_figures/adaptive_reduction.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.2,4.1),constrained_layout=True)
    graph_rows=list(d['graph_controls']['by_graph'].items());ys=list(range(len(graph_rows)));ratios=[]
    for method,offset,label,color in [('learned',-.12,'Cost model','#176e8d'),('guarded',.12,'Validated policy','#b45e22')]:
        x=[v[method]/v['graph_fixed'] for g,v in graph_rows];ratios+=x
        ax.scatter(x,[v+offset for v in ys],label=label,s=32,color=color,zorder=3)
    ax.axvline(1,color='#555555',linestyle='--',lw=1)
    ax.set_yticks(ys);ax.set_yticklabels([names.get(g,g) for g,v in graph_rows]);ax.invert_yaxis()
    low=min(ratios+[1]);high=max(ratios+[1]);pad=max(.025,(high-low)*.15)
    ax.set_xlim(max(0,low-pad),high+pad);ax.set_xlabel('Time / best fixed setting for this graph')
    ax.grid(axis='x',alpha=.2);ax.legend(frameon=False,fontsize=9)
    fig.savefig(ROOT/'report/paper_figures/adaptive_graph_controls.pdf');plt.close(fig)
    if d['integration']:
        fig,ax=plt.subplots(figsize=(7.1,3.4),constrained_layout=True)
        methods=['previous','files','projected','learned'];labels=['Previous preparation','Existing files only','Projected criterion','Validated policy']
        for k,row in enumerate(d['integration']):
            v=[row['methods'][m]['median_seconds'] if row['methods'][m]['median_seconds'] is not None else float('nan') for m in methods]
            ax.plot(range(4),v,'o-',label=str(row['loops'])+' loops',color=['#176e8d','#b45e22'][k])
            for i,x in enumerate(v):
                if x==x:ax.annotate(f'{x:.2f} s',(i,x),xytext=(0,7),textcoords='offset points',ha='center',fontsize=9)
        ax.set_xticks(range(4));ax.set_xticklabels(labels,fontsize=9);ax.set_yscale('log');ax.set_ylabel('Complete reduction time (s, log scale)')
        ax.margins(x=.08,y=.2);ax.grid(axis='y',which='both',alpha=.18);ax.legend(frameon=False)
        fig.savefig(ROOT/'report/paper_figures/adaptive_integration.pdf');plt.close(fig)
if __name__=='__main__':main()
