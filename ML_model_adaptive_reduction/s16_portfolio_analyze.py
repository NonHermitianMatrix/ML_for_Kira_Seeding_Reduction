"""Audit the frozen portfolio and plot each gain against its matched control."""
import collections, datetime, json, statistics
import s15_portfolio_study as model
study, rt, HERE, ROOT, OUT = model.study, model.rt, model.HERE, model.ROOT, model.OUT
METHODS=['native','adaptive','published','fixed','selected']
NAMES={'one_mass_box':'Virtuality box','nonplanar_box':'Nonplanar box','double_box':'Planar double box',
    'sunrise':'Sunrise','pentagon':'Pentagon','vacuum3':'Three-loop vacuum',
    'ladder3':'Three-loop two-point ladder','bubble_box3':'Three-loop bubble box','bubble_box4':'Four-loop bubble box'}

def main():
    protocol=json.loads((OUT/'protocol.json').read_text());frozen=json.loads((OUT/'trained_model/freeze.json').read_text())
    assert frozen['protocol_sha256']==study.sha(OUT/'protocol.json')
    assert frozen['candidates_sha256']==study.sha(OUT/'trained_model/candidates.json')
    for name,digest in protocol['source_hashes'].items():assert study.sha(HERE/name)==digest
    first=min(p.stat().st_mtime for p in (OUT/'references').glob('*.gz'))
    assert datetime.datetime.fromisoformat(frozen['frozen_utc']).timestamp()<first
    cases=protocol['cases'];assert model.freeze(cases)==frozen
    splits={s:{c['group'] for c in cases if c['split']==s} for s in ['training','validation','reserved']}
    assert not (splits['training']&splits['validation'] or splits['training']&splits['reserved'] or splits['validation']&splits['reserved'])
    training_rows=0;offline=0.;coefficients=0;max_rss=0.
    def check(r):
        nonlocal coefficients,max_rss
        assert r['success'] and r['reference_checked'] and not r['mismatches']
        coefficients+=r['coefficient_checks']
        for attempt in r['attempts']:
            assert attempt['binary_sha256']==protocol['binary_sha256']
            assert attempt['parallel_evaluation'] and attempt['shared_evaluation']
            assert attempt['compact_back_substitution'] and attempt['worker_threads'] in [1,2]
            assert attempt['pair_fastpath'] and attempt['sparse_row_features']
            max_rss=max(max_rss,attempt.get('peak_rss_bytes',0)/1024**2)
    for split,repetitions in [('training',1),('validation',2)]:
        for c in (c for c in cases if c['split']==split):
            for action in model.ACTIONS:
                for rep in range(repetitions):
                    r=rt.read(OUT/split/f'{c["id"]}_{action}_{rep}.json.gz');check(r)
                    training_rows+=1;offline+=r['complete_seconds']
    rows=[];unfinished=[]
    for c in (c for c in cases if c['split']=='reserved'):
        ref=OUT/'references'/(c['id']+'.json.gz');second=OUT/'references'/(c['id']+'_check.json.gz')
        if not ref.exists() or not rt.read(ref)['success'] or not second.exists() or not rt.read(second)['success']:
            unfinished.append(dict(case=c['id'],reference_status=rt.read(ref)['status'] if ref.exists() else 'missing',
                check_status=rt.read(second)['status'] if second.exists() else 'missing'));continue
        assert rt.read(second)['reference_checked']
        methods={}
        for method in METHODS:
            records=[rt.read(OUT/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz') for rep in range(3)]
            for r in records:check(r)
            if method=='selected':assert all(r['action']==model.select(frozen,c)[0] for r in records)
            if method=='fixed':assert all(r['action']==frozen['graphs'][c['topology_group']]['fixed'] for r in records)
            methods[method]=dict(median_seconds=statistics.median(r['complete_seconds'] for r in records),
                median_cpu_seconds=statistics.median(r['cpu_seconds'] for r in records),
                seconds=[r['complete_seconds'] for r in records],cpu_seconds=[r['cpu_seconds'] for r in records],
                actions=[r['action'] for r in records],fallbacks=sum(r['fallback_count'] for r in records),
                decisions=[r.get('portfolio_decision_seconds',0) for r in records],
                seed_bounds=[a.get('seed_bounds') for a in records[0]['attempts']],
                worker_threads=[a.get('worker_threads') for a in records[0]['attempts']],
                generated_equations=[sum(sum(a.get('counters',{}).get('generated_equations',[])) for a in r['attempts']) for r in records],
                selected_equations=[sum(sum(a.get('counters',{}).get('selected_equations',[])) for a in r['attempts']) for r in records])
        application=rt.read(OUT/'applications'/(c['id']+'.json.gz'));check(application)
        assert not application['reference_coefficients_supplied']
        rows.append(dict(case=c['id'],graph=c['topology_group'],loops=len(c['definition']['loop_momenta']),
            symbolic=bool(c['definition']['invariants']),targets=c['size'],methods=methods))
    groups={}
    for graph in sorted({c['graph'] for c in rows}):
        cs=[c for c in rows if c['graph']==graph]
        groups[graph]=dict(batches=len(cs),loops=cs[0]['loops'],
            seconds={m:sum(c['methods'][m]['median_seconds'] for c in cs) for m in METHODS},
            cpu_seconds={m:sum(c['methods'][m]['median_cpu_seconds'] for c in cs) for m in METHODS})
    totals={m:sum(c['methods'][m]['median_seconds'] for c in rows) for m in METHODS}
    trial_totals={m:sum(sum(c['methods'][m]['seconds']) for c in rows) for m in METHODS}
    candidates=json.loads((OUT/'trained_model/candidates.json').read_text())
    guard={g:{k:v for k,v in p.items() if k not in ['model','definitions']}|{
        'model_name':p['model']['name'],'trees':len(p['model']['trees'])} for g,p in frozen['graphs'].items()}
    public=json.loads((OUT/'application_test/validation.json').read_text())
    assert public['complete'] and public['all_exact'] and public['matched_loading_checks']==6
    assert public['source_sha256']==study.sha(HERE/'s17_reduce.py')
    loading={}
    for method in ['eager','deferred']:
        records=[rt.read(OUT/'application_loading'/f'{method}_{rep}.json.gz') for rep in range(3)]
        for r in records:
            check(r)
            assert r['action']=='adaptive1' and not r['reference_coefficients_supplied']
        loading[method]=dict(request_seconds=[r['request_seconds'] for r in records],
            median_request_seconds=statistics.median(r['request_seconds'] for r in records),
            median_loading_seconds=statistics.median(r['model_loading_seconds'] for r in records),
            timing=records[0]['timing'])
    loading['checks']=6
    loading['case']='sunrise_p306_dots'
    loading['ratio']=loading['deferred']['median_request_seconds']/loading['eager']['median_request_seconds']
    out=dict(complete=True,all_exact=True,cases=rows,unfinished=unfinished,by_graph=groups,totals=totals,
        application_loading=loading,
        cpu_totals={m:sum(c['methods'][m]['median_cpu_seconds'] for c in rows) for m in METHODS},
        all_trial_totals=trial_totals,
        ratios={m:totals['selected']/totals[m] for m in METHODS if m!='selected'},
        all_trial_ratios={m:trial_totals['selected']/trial_totals[m] for m in METHODS if m!='selected'},
        training_cases=sum(c['split']=='training' for c in cases),validation_cases=sum(c['split']=='validation' for c in cases),
        test_cases=len(rows),timed_test_workflows=15*len(rows),applications=len(rows),training_validation_workflows=training_rows,
        coefficient_checks=coefficients,guard=guard,enabled_graphs=[g for g,p in guard.items() if p['enabled']],
        model_candidates=len(candidates['global_models'])+sum(map(len,candidates['local_models'].values())),
        training_seconds=candidates['training_seconds'],offline_label_seconds=offline,
        decisions=dict(collections.Counter(c['methods']['selected']['actions'][0] for c in rows)),
        median_decision_seconds=statistics.median(c['methods']['selected']['decisions'][1] for c in rows),
        fallbacks={m:sum(c['methods'][m]['fallbacks'] for c in rows) for m in METHODS},
        max_recorded_rss_mib=max_rss,protocol_sha256=study.sha(OUT/'protocol.json'),freeze_sha256=study.sha(OUT/'trained_model/freeze.json'),
        source_hashes=protocol['source_hashes'],timing=protocol['timing'],scope=protocol['split'],controls=protocol['controls'])
    study.write(OUT/'summary.json',out);study.write(ROOT/'report/portfolio_data.json',out)
    plot(out);print(json.dumps({k:out[k] for k in ['test_cases','totals','ratios','enabled_graphs','decisions']}),flush=True)

def plot(data):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    rows=list(data['by_graph'].items());ys=list(range(len(rows)))
    fig,axs=plt.subplots(1,2,figsize=(7.4,4.8),constrained_layout=True,sharey=True)
    for ax,control,title in zip(axs,['published','fixed'],['Compared with the\nprevious workflow','Added benefit beyond a\nfixed choice per graph']):
        ratios=[v['seconds']['selected']/v['seconds'][control] for g,v in rows]
        ax.axvline(1,color='#555555',linestyle='--',linewidth=1)
        for i,((graph,v),ratio) in enumerate(zip(rows,ratios)):
            cs=[c for c in data['cases'] if c['graph']==graph]
            rep=[sum(c['methods']['selected']['seconds'][r] for c in cs)/sum(c['methods'][control]['seconds'][r] for c in cs) for r in range(3)]
            ax.hlines(i,min(rep+[ratio]),max(rep+[ratio]),color='#176e8d',alpha=.5,linewidth=2)
            ax.plot(ratio,i,'o',color='#176e8d',markersize=5)
        values=ratios+[1];pad=max(.03,(max(values)-min(values))*.15)
        # Include all descriptive ranges as well as the central ratios.
        ranges=[]
        for g,v in rows:
            cs=[c for c in data['cases'] if c['graph']==g]
            ranges.extend(sum(c['methods']['selected']['seconds'][r] for c in cs)/sum(c['methods'][control]['seconds'][r] for c in cs) for r in range(3))
        ax.set_xlim(max(0,min(values+ranges)-pad),max(values+ranges)+pad)
        ax.set_title(title,fontsize=10);ax.set_xlabel('Selected time / control time');ax.grid(axis='x',alpha=.2)
    axs[0].set_yticks(ys);axs[0].set_yticklabels([NAMES[g] for g,v in rows]);axs[0].invert_yaxis()
    fig.savefig(ROOT/'report/paper_figures/portfolio_controls.pdf');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.5),constrained_layout=True)
    names=['Native','Earlier cost policy','Previous workflow','Fixed per graph','Selected portfolio']
    for ax,key,label in zip(axs,['totals','cpu_totals'],['Complete wall time (s)','Process CPU time (s)']):
        values=[data[key][m] for m in METHODS]
        bars=ax.barh(range(len(METHODS)),values,color=['#b7c5cb','#86aaba','#6c90a2','#bdad93','#176e8d'])
        ax.set_yticks(range(len(METHODS)));ax.set_yticklabels(names if ax==axs[0] else ['']*len(names));ax.invert_yaxis()
        ax.set_xlabel(label);ax.set_xlim(0,max(values)*1.2);ax.bar_label(bars,fmt='%.1f',padding=3,fontsize=9)
        ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    fig.savefig(ROOT/'report/paper_figures/portfolio_totals.pdf');plt.close(fig)

if __name__=='__main__':main()
