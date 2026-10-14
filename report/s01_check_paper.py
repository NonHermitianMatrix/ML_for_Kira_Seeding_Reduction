"""Bounded checks of the paper and preserved notes, with no research reruns."""
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

HERE=Path(__file__).resolve().parent
def main():
    names=['report.tex','paper_appendices.tex','scattering_results.tex','workflow_results.tex','workflow_appendix.tex']
    source='\n'.join((HERE/n).read_text() for n in names)
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
    for label in ['app:families','app:basis','app:optimal','app:models','app:vacuum','app:workflow']:
        assert label in labels,label
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
    result=dict(external_citation_keys=len(cites),internal_references=len(refs),figures=len(figs),
        self_repository_citations=0,original_notes_reconstructable=True,terminology_updated_as_requested=True,
        original_supporting_files_preserved=len(archive['supporting_files']),
        complete_cost_workflows=workflow['workflows'],joint_request_workflows=batching['workflows'],
        applications_without_reference_answers=applications,
        pdf_sha256={n:hashlib.sha256((HERE/(n+'.pdf')).read_bytes()).hexdigest() for n in ['report','notes']})
    (HERE/'paper_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':main()
