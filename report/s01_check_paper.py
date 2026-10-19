"""Bounded checks of the paper and preserved notes, with no research reruns."""
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

HERE=Path(__file__).resolve().parent
def main():
    def expanded(name,seen=None):
        seen=set() if seen is None else seen
        assert name not in seen,('Repeated or cyclic input',name)
        seen.add(name)
        text=(HERE/name).read_text()
        return re.sub(r'\\input\{([^}]+)\}',lambda m:expanded(m.group(1)+'.tex',seen),text)
    source=expanded('report.tex')
    notes_source=expanded('notes.tex')
    bib=(HERE/'paper_references.bib').read_text()
    cites={x.strip() for group in re.findall(r'\\cite\{([^}]+)\}',source) for x in group.split(',')}
    keys=set(re.findall(r'@\w+\{([^,]+),',bib))
    labels=re.findall(r'\\label\{([^}]+)\}',source)
    refs=set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',source))
    assert cites<=keys,cites-keys
    assert refs<=set(labels),refs-set(labels)
    assert len(labels)==len(set(labels))
    assert not re.search(r'NonHermitianMatrix|ML_for_Kira_Seeding_Reduction',source+bib)
    assert not re.search(r'SHA[- ]?256|checksum|git commit|scratch directory|source hash',source,re.I)
    assert not re.search(r'System\s*1',source,re.I)
    for label in ['app:derivation','app:sparse','app:shared','app:families-new','app:statistics']:
        assert label in labels,label
    notes_labels=re.findall(r'\\label\{([^}]+)\}',notes_source)
    notes_refs=set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',notes_source))
    assert notes_refs<=set(notes_labels),notes_refs-set(notes_labels)
    assert len(notes_labels)==len(set(notes_labels))
    notes_bib=''.join((HERE/n).read_text() for n in ['references.bib','type_specialist_references.bib','notes_additional_references.bib'])
    notes_keys=set(re.findall(r'@\w+\{([^,]+),',notes_bib))
    notes_cites={x.strip() for group in re.findall(r'\\cite\{([^}]+)\}',notes_source) for x in group.split(',')}
    assert notes_cites<=notes_keys,notes_cites-notes_keys
    figs=re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',source)
    for f in figs:assert (HERE/f).read_bytes().startswith(b'%PDF'),f
    for name in ['report','notes']:
        assert (HERE/(name+'.pdf')).read_bytes().startswith(b'%PDF')
        log=HERE/(name+'.log')
        if log.exists():
            s=log.read_text(errors='replace')
            assert not re.search(r'(?:Citation|Reference) .+ undefined|There were undefined|^! ',s,re.M),name
    notes=(HERE/'notes.tex').read_text()
    assert not re.search(r'System\s*1',notes,re.I)
    revision=json.loads((HERE/'notes_revision.json').read_text())
    restored=notes
    restored=re.sub(r'% BEGIN CURRENT WORKFLOW UPDATE\n.*?% END CURRENT WORKFLOW UPDATE\n','',restored,flags=re.S)
    for new,old in revision['reverse_replacements']:
        assert restored.count(new)==1,new
        restored=restored.replace(new,old)
    abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',restored,re.S).group(1)
    archive=json.loads((HERE/'notes_preservation.json').read_text())
    assert hashlib.sha256(abstract.encode()).hexdigest()==archive['abstract_sha256']
    restored=restored.replace('Notes on Machine Learning for Kira IBP Reduction','Machine Learning for Kira IBP Reduction')
    assert hashlib.sha256(restored.encode()).hexdigest()==archive['original_source_sha256']
    for n,digest in archive['supporting_files'].items():
        assert hashlib.sha256((HERE/n).read_bytes()).hexdigest()==digest,n
    data=json.loads((HERE/'paper_figure_data.json').read_text())
    for name,record in data['sources'].items():
        path=HERE.parent/name
        if path.exists():assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256'],name
    adaptation=json.loads((HERE/'scattering_figure_data.json').read_text())
    assert adaptation['complete'] and adaptation['all_exact']
    assert adaptation['workflows']==180 and adaptation['application_checks']==18
    assert len(adaptation['training'])==6
    for task in ['seed','equation']:
        assert adaptation['aggregate'][task]['first_attempt_successes']==sum(
            c['first_attempt_successes'][task] for c in adaptation['cases'])
    for record in adaptation['cases']:
        for task,ratio in record['ratios'].items():
            expected=record['median_seconds'][task]/record['median_seconds']['native']
            assert abs(ratio-expected)<1e-12
    workflow=json.loads((HERE/'workflow_figure_data.json').read_text())
    batching=json.loads((HERE/'batching_figure_data.json').read_text())
    audit=json.loads((HERE/'workflow_validation.json').read_text())
    assert audit['complete'] and audit['all_exact']
    applications=audit['basis_only_applications']+sum(r['applications'] for r in audit['public_checks'].values())
    assert applications==61
    for data,number,baseline in [(workflow,620,'native'),(batching,200,'separate_native')]:
        assert data['complete'] and data['all_exact'] and data['workflows']==number
        for record in data['cases']:
            for task,ratio in record['ratios'].items():
                expected=record['median_seconds'][task]/record['median_seconds'][baseline]
                assert abs(ratio-expected)<1e-12
        for task,record in data['aggregate'].items():
            expected=math.exp(statistics.mean(math.log(v[task]) for v in data['by_topology'].values()))
            assert abs(record['ratio']-expected)<1e-12
            assert len(record['interval'])==2 and record['interval'][0]<=record['interval'][1]
    assert workflow['applications']==31
    assert workflow['training_cases']==31 and workflow['validation_cases']==17 and workflow['test_cases']==31
    assert len(batching['cases'])==10
    # On Hoffman, compare the compact report copies with the saved scientific summaries.
    for name,data in [('model_test/summary.json',workflow),('request_batching/summary.json',batching),('evidence_validation.json',audit)]:
        source_path=HERE.parent/'ML_model_workflow_selection'/name
        if source_path.exists():assert json.loads(source_path.read_text())==data,name
    specialist=json.loads((HERE/'type_specialist_figure_data.json').read_text())
    specialist_audit=json.loads((HERE/'type_specialist_validation.json').read_text())
    assert specialist['complete'] and specialist['all_exact'] and specialist_audit['complete']
    assert specialist['workflows']==720 and specialist['applications']==36
    assert specialist['model_candidates']==70
    assert specialist_audit['public_applications']==7
    for record in specialist['cases']:
        for method,ratio in record['ratios'].items():
            expected=record['median_seconds'][method]/record['median_seconds']['native']
            assert abs(ratio-expected)<1e-12
    for method,record in specialist['aggregate'].items():
        expected=math.exp(statistics.mean(math.log(v[method]) for v in specialist['by_topology'].values()))
        assert abs(record['ratio']-expected)<1e-12
    for name,data in [('model_test/summary.json',specialist),('evidence_validation.json',specialist_audit)]:
        path=HERE.parent/'ML_model_workflow_selection/type_specialists'/name
        if path.exists():assert json.loads(path.read_text())==data
    completion=json.loads((HERE/'basis_completion_figure_data.json').read_text())
    completion_audit=json.loads((HERE/'basis_completion_validation.json').read_text())
    assert completion['complete'] and completion['all_exact'] and completion_audit['complete']
    assert completion['workflows']==720 and completion['applications']==36
    assert completion_audit['public_applications']==7
    denominators={'selected_to_native':('selected','native'),'selected_to_previous':('selected','previous'),'selected_to_fixed':('selected','family_fixed'),'previous_to_native':('previous','native'),'fixed_to_previous':('family_fixed','previous')}
    for row in completion['cases']:
        for key,(a,b) in denominators.items():assert abs(row['ratios'][key]-row['median_seconds'][a]/row['median_seconds'][b])<1e-12
    for key,row in completion['aggregate'].items():
        expected=math.exp(statistics.mean(math.log(r[key]) for r in completion['by_topology'].values()))
        assert abs(row['ratio']-expected)<1e-12
    for name,data in [('model_test/summary.json',completion),('evidence_validation.json',completion_audit)]:
        path=HERE.parent/'ML_model_workflow_selection/basis_completion'/name
        if path.exists():assert json.loads(path.read_text())==data
    ordering=json.loads((HERE/'ordering_policy_figure_data.json').read_text())
    ordering_audit=json.loads((HERE/'ordering_policy_validation.json').read_text())
    assert ordering['complete'] and ordering['all_exact'] and ordering_audit['complete']
    assert ordering['workflows']==720 and ordering['applications']==36 and ordering_audit['public_applications']==7
    for row in ordering['cases']:
        for key,(a,b) in denominators.items():assert abs(row['ratios'][key]-row['median_seconds'][a]/row['median_seconds'][b])<1e-12
    for key,row in ordering['aggregate'].items():
        expected=math.exp(statistics.mean(math.log(r[key]) for r in ordering['by_topology'].values()))
        assert abs(row['ratio']-expected)<1e-12
    for name,data in [('model_test/summary.json',ordering),('evidence_validation.json',ordering_audit)]:
        path=HERE.parent/'ML_model_workflow_selection/ordering_policy'/name
        if path.exists():assert json.loads(path.read_text())==data
    thread=json.loads((HERE/'thread_policy_figure_data.json').read_text())
    thread_audit=json.loads((HERE/'thread_policy_validation.json').read_text())
    assert thread['complete'] and thread['all_exact'] and thread_audit['complete']
    assert thread['workflows']==900 and thread['applications']==36 and thread_audit['public_applications']==7 and thread_audit['persistent_worker_applications']==7
    thread_denominators=dict(denominators,selected_to_four=('selected','previous_four'),four_to_previous=('previous_four','previous'))
    for row in thread['cases']:
        for key,(a,b) in thread_denominators.items():assert abs(row['ratios'][key]-row['median_seconds'][a]/row['median_seconds'][b])<1e-12
    for key,row in thread['aggregate'].items():
        expected=math.exp(statistics.mean(math.log(r[key]) for r in thread['by_topology'].values()))
        assert abs(row['ratio']-expected)<1e-12
    assert thread['allocated_cores']==4 and all(v>0 for v in thread['cpu_totals'].values())
    for name,data in [('model_test/summary.json',thread),('evidence_validation.json',thread_audit)]:
        path=HERE.parent/'ML_model_workflow_selection/thread_policy'/name
        if path.exists():assert json.loads(path.read_text())==data
    general=json.loads((HERE/'general_policy_data.json').read_text())
    assert general['complete'] and general['gradient_check']['complete']
    assert sum(general['counts'].values())==general['requested']==110
    assert set(general['by_loop'])==set(map(str,range(1,13)))
    for row in general['rows']:
        for method,values in row['times'].items():
            assert len(values)==3 and min(values)>0
            assert abs(statistics.median(values)-row['medians'][method])<1e-10
    for selection in ['overall','known','held_out']:
        record=general[selection]
        if not record['cases']:continue
        for control,ratio in record['ratios'].items():
            assert abs(ratio-record['summed_median_seconds']['learned']/record['summed_median_seconds'][control])<1e-10
    gp=HERE.parent/'ML_model_adaptive_reduction/general_policy/summary.json'
    if gp.exists():assert json.loads(gp.read_text())==general
    preparation=json.loads((HERE/'preparation_data.json').read_text())
    assert preparation['complete'] and preparation['all_same_basis_matched_outputs_exact']
    assert preparation['requests']==len(preparation['rows'])==33
    assert 'app:risk' in labels and 'tab:preparation-times' in labels
    for method in preparation['methods']:
        total=preparation['counts'][method]
        assert total['first_completed']==sum(r['first_success'][method] for r in preparation['rows'])
        assert total['three_completed']==sum(r['complete'][method] for r in preparation['rows'])
        assert abs(total['first_failed_seconds']-sum(r['first_failed_seconds'][method] for r in preparation['rows']))<1e-8
    for key,value in preparation['comparisons'].items():
        if not value['cases']:continue
        a,b=key.split('/')
        matched=[r for r in preparation['rows'] if r['complete'][a] and r['complete'][b] and r['pairs'][key]['agree']]
        assert value['cases']==len(matched)==len(value['case_ids'])
        for method in [a,b]:
            assert abs(value['summed_median_seconds'][method]-sum(statistics.median(r['times'][method]) for r in matched))<1e-8
        assert abs(value['ratio']-value['summed_median_seconds'][a]/value['summed_median_seconds'][b])<1e-10
    gp=HERE.parent/'ML_model_adaptive_reduction/general_policy/preparation/summary.json'
    if gp.exists():assert json.loads(gp.read_text())==preparation
    recovery=json.loads((HERE/'recovery_data.json').read_text())
    assert recovery['complete'] and recovery['all_matched_exact'] and recovery['requests']==len(recovery['rows'])==6
    for method,n in recovery['completed'].items():assert n==sum(r['complete'][method] for r in recovery['rows'])
    for key,v in recovery['comparisons'].items():
        if not v['cases']:continue
        a,b=key.split('/')
        assert abs(v['ratio']-v['summed_median_seconds'][a]/v['summed_median_seconds'][b])<1e-10
    gp=HERE.parent/'ML_model_adaptive_reduction/general_policy/recovery/summary.json'
    if gp.exists():assert json.loads(gp.read_text())==recovery
    factorized=json.loads((HERE/'factorized_data.json').read_text())
    assert factorized['complete'] and factorized['initial']['requested']==131
    assert set(factorized['initial']['by_loop'])==set(map(str,range(1,14)))
    assert 'app:blocks13' in labels and 'sec:blocks13' in labels
    for phase in ['initial','final']:
        d=factorized[phase]
        assert d['requested']==len(d['rows'])
        for v in d['comparisons'].values():
            if not v['cases']:continue
            totals=v['summed_median_seconds'];b=next(k for k in totals if k!='learned')
            assert abs(v['ratio']-totals['learned']/totals[b])<1e-12
    q=HERE.parent/'ML_model_adaptive_reduction/factorized_policy/summary.json'
    if q.exists():assert json.loads(q.read_text())==factorized
    total_time=json.loads((HERE/'total_time_data.json').read_text())
    assert total_time['complete'] and total_time['requested']==len(total_time['rows'])
    assert 'sec:total-time' in labels and 'app:total-time' in labels
    for group in total_time['comparisons'].values():
        for v in group.values():
            if v['cases']:assert abs(v['ratio']-v['learned_seconds']/v['control_seconds'])<1e-12
    q=HERE.parent/'ML_model_adaptive_reduction/total_time_policy/summary.json'
    if q.exists():assert json.loads(q.read_text())==total_time
    refined_time=json.loads((HERE/'refined_time_data.json').read_text())
    assert refined_time['complete'] and refined_time['requested']==len(refined_time['rows'])
    assert 'sec:refined-time' in labels and 'app:refined-time' in labels
    for group in refined_time['comparisons'].values():
        for v in group.values():
            if v['cases']:assert abs(v['ratio']-v['learned_seconds']/v['control_seconds'])<1e-12
    q=HERE.parent/'ML_model_adaptive_reduction/refined_time_policy/summary.json'
    if q.exists():assert json.loads(q.read_text())==refined_time
    hybrid_expert=json.loads((HERE/'hybrid_expert_data.json').read_text())
    assert hybrid_expert['complete'] and hybrid_expert['requested']==len(hybrid_expert['rows'])==34
    assert 'sec:hybrid-experts' in labels and 'app:hybrid-experts' in labels
    for group in hybrid_expert['comparisons'].values():
        for v in group.values():
            if v['cases']:assert abs(v['ratio']-v['learned_seconds']/v['control_seconds'])<1e-12
    p=HERE.parent/'ML_model_adaptive_reduction/hybrid_experts/summary.json'
    if p.exists():assert json.loads(p.read_text())==hybrid_expert
    analytic=json.loads((HERE/'analytic_decomposition_data.json').read_text())
    assert analytic['complete'] and analytic['requests']==len(analytic['rows'])==41
    assert 'sec:analytic-results' in labels and 'app:analytic-decomposition' in labels
    for group in analytic['comparisons'].values():
        for value in group.values():
            if value['cases']:assert abs(value['ratio']-value['learned_seconds']/value['control_seconds'])<1e-12
    p=HERE.parent/'ML_model_adaptive_reduction/analytic_decomposition/summary.json'
    if p.exists():assert json.loads(p.read_text())==analytic
    guard=json.loads((HERE/'parser_guard_data.json').read_text())
    assert guard['complete'] and guard['requests']==len(guard['rows'])==9
    assert 'sec:parser-guard' in labels and 'app:parser-guard' in labels
    for group in guard['comparisons'].values():
        for value in group.values():
            assert abs(value['ratio']-value['learned_seconds']/value['control_seconds'])<1e-12
    p=HERE.parent/'ML_model_adaptive_reduction/analytic_decomposition/deployment/summary.json'
    if p.exists():assert json.loads(p.read_text())==guard
    fast=json.loads((HERE/'fast_decomposition_data.json').read_text())
    assert fast['complete'] and fast['requests']==len(fast['rows'])==65
    assert fast['coverage']['total']['requests']==len(fast['coverage']['rows'])==110
    assert set(fast['coverage']['by_loop'])==set(map(str,range(1,14)))
    assert 'sec:fast-results' in labels and 'app:fast-method' in labels
    for group in fast['comparisons'].values():
        for value in group.values():
            if value['cases']:assert abs(value['ratio']-value['learned_seconds']/value['control_seconds'])<1e-12
    p=HERE.parent/'ML_model_adaptive_reduction/fast_decomposition/summary.json'
    if p.exists():assert json.loads(p.read_text())==fast
    deployment=json.loads((HERE/'fast_deployment_data.json').read_text())
    assert deployment['complete'] and deployment['requests']==12
    assert 'sec:fast-deployment' in labels and 'app:fast-deployment' in labels
    for group in deployment['comparisons'].values():
        for value in group.values():
            if value['cases']:assert abs(value['ratio']-value['final_seconds']/value['control_seconds'])<1e-12
    p=HERE.parent/'ML_model_adaptive_reduction/fast_decomposition/deployment/summary.json'
    if p.exists():assert json.loads(p.read_text())==deployment
    result=dict(general_model_test_complete=True,general_requests=general['requested'],general_checked_cases=general['overall']['cases'],external_citation_keys=len(cites),internal_references=len(refs),figures=len(figs),
        preparation_requests=preparation['requests'],preparation_exact_checks=preparation['coefficient_checks'],
        recovery_requests=recovery['requests'],recovery_exact_checks=recovery['coefficient_checks'],
        self_repository_citations=0,original_notes_reconstructable=True,terminology_updated_as_requested=True,
        original_supporting_files_preserved=len(archive['supporting_files']),
        complete_cost_workflows=workflow['workflows'],joint_request_workflows=batching['workflows'],
        applications_without_reference_answers=applications,
        specialist_workflows=specialist['workflows'],specialist_applications=43,specialist_candidates=70,
        basis_completion_workflows=completion['workflows'],basis_completion_applications=43,
        ordering_workflows=ordering['workflows'],ordering_applications=43,
        thread_workflows=thread['workflows'],thread_applications=50,
        pdf_sha256={n:hashlib.sha256((HERE/(n+'.pdf')).read_bytes()).hexdigest() for n in ['report','notes']})
    (HERE/'paper_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':main()
