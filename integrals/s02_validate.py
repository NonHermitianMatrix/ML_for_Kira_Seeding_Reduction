#!/usr/bin/env python3
"""Verify the unified layout, all links and unchanged scientific records."""
import argparse,copy,gzip,hashlib,json,os,subprocess,tarfile
from pathlib import Path,PurePosixPath
from functools import lru_cache
from s00_reorganize import old_family,source_catalog,file_sha,read,write,sha
from s01_read_data import records,linked_target
ROOT=Path(__file__).resolve().parent
def lines(path):
    op=gzip.open if path.suffix=='.gz' else open
    with op(str(path),'rt',encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]
def content(path):
    if path.suffix=='.gz':
        with gzip.open(str(path),'rb') as f:return f.read()
    return path.read_bytes()
@lru_cache(maxsize=None)
def link(value):
    assert not PurePosixPath(value).is_absolute() and '..' not in PurePosixPath(value).parts
    p=ROOT/value
    assert p.is_file(),value
def unchanged_fields(before,after,changed,added=()):
    assert set(after)-set(before)<=set(added),(set(after)-set(before),set(added))
    assert set(before)-set(after)<=set(changed)
    for k,v in before.items():
        if k not in changed:assert after[k]==v,k
def compare_original(entry,raw,supp,inputs,refs,traces):
    name=entry['family'];mp='Master_Integrals/families/'+name+'/'
    tp='master_to_target/families/'+name+'/'
    for filename in ['masters.json','masters.txt','definition.json']:
        assert (ROOT/'master_integrals/families'/name/filename).read_bytes()==raw[mp+filename]
    with tarfile.open(str(ROOT/'master_integrals/families'/name/'basis_checks.tar.gz')) as tf:
        expected={k[len(mp):]:v for k,v in raw.items() if k.startswith(mp) and k[len(mp):] not in ['masters.json','masters.txt','definition.json']}
        assert set(tf.getnames())==set(expected)
        for k,v in expected.items():assert tf.extractfile(k).read()==v
    for filename in ['identities.jsonl','construction_proofs.jsonl','candidate_seeds.json','symmetries.json']:
        suffix='.gz' if filename.endswith('.jsonl') else ''
        assert content(ROOT/'master_to_target/families'/name/(filename+suffix))==raw[tp+filename]
    with tarfile.open(str(ROOT/'master_to_target/families'/name/'generation_records.tar.gz')) as tf:
        for filename in ['definition.json','summary.json','validation.json']:
            assert tf.extractfile(filename).read()==raw[tp+filename]
    old_inputs=[json.loads(l) for l in raw[tp+'inputs.jsonl'].splitlines() if l.strip()]
    old_refs=[json.loads(l) for l in raw[tp+'references.jsonl'].splitlines() if l.strip()]
    old_traces=[json.loads(l) for l in raw[tp+'elimination_traces.jsonl'].splitlines() if l.strip()]
    if supp:
        old_inputs+=supp['inputs'];old_refs+=supp['references'];old_traces+=supp['elimination_traces']
    assert len(old_inputs)==len(inputs)==len(refs)==len(traces)
    for before,after in zip(old_inputs,inputs):
        unchanged_fields(before,after,{'master_basis','candidate_seeds','equation_pool','source_archive','split'},
            {'stored_split','family_definition','reference_records','elimination_records'})
        assert after['split']==entry['split']
        if before['split']!=after['split']:assert after['stored_split']==before['split']
    for before,after in zip(old_refs,refs):
        unchanged_fields(before,after,{'split','construction'},
            {'stored_split','master_ids','master_basis','target_records','elimination_records'})
        c=copy.deepcopy(after['construction'])
        if 'proof_library' in before['construction']:
            c['proof_library']=before['construction']['proof_library']
        assert c==before['construction']
        assert after['split']==entry['split']
        if before['split']!=after['split']:assert after['stored_split']==before['split']
    assert traces==old_traces
def verify_family(entry,source=None,original=None):
    name=entry['family'];manifest=read(ROOT/entry['manifest'])
    for path,expected in manifest['files'].items():
        link(path);p=ROOT/path
        assert p.stat().st_size==expected['bytes'] and file_sha(p)==expected['sha256'],path
    basis=next(records(name,'masters'));definition=next(records(name,'definition'))
    assert basis['family']==definition['id']==name and basis['status']=='validated'
    assert len(basis['masters'])==entry['master_count']
    indices={tuple(m['indices']):m['id'] for m in basis['masters']}
    assert len(indices)==len(basis['masters'])
    with tarfile.open(str(ROOT/'master_integrals/families'/name/'basis_checks.tar.gz')) as tf:
        for stage in ['discovery','expanded','independent_point']:
            run=json.load(tf.extractfile('validation/'+stage+'/run.json'))
            assert run['status']=='passed' and run['returncode']==0
            assert run['master_indices']==[m['indices'] for m in basis['masters']]
    with tarfile.open(str(ROOT/'master_to_target/families'/name/'generation_records.tar.gz')) as tf:
        assert json.load(tf.extractfile('definition.json'))==definition
    inputs=list(records(name,'inputs'));refs=list(records(name,'references'));traces=list(records(name,'traces'))
    assert len(inputs)==len(refs)==len(traces)==entry['targets']
    ids=[r['id'] for r in inputs]
    assert len(ids)==len(set(ids))
    assert ids==[r['id'] for r in refs]==[r['id'] for r in traces]
    identity={r['id']:r for r in records(name,'identities')}
    total_steps=0;operations=dict(divisions=0,multiplications=0,subtractions=0)
    for inp,ref,trace in zip(inputs,refs,traces):
        assert inp['family']==ref['family']==name
        assert inp['split']==ref['split']==entry['split']
        for key in ['master_basis','family_definition','candidate_seeds','equation_pool','reference_records','elimination_records']:link(inp[key])
        assert inp['master_basis']==entry['master_basis'] and inp['family_definition']==entry['definition']
        assert inp['candidate_seeds']==entry['records']+'/candidate_seeds.json'
        assert inp['equation_pool']==entry['records']+'/identities.jsonl.gz'
        assert inp['reference_records']==entry['references'] and inp['elimination_records']==entry['traces']
        assert ref['master_basis']==entry['master_basis'] and ref['target_records']==entry['targets_file']
        assert ref['elimination_records']==entry['traces']
        for key in ['master_basis','target_records','elimination_records']:link(ref[key])
        if 'proof_library' in ref['construction']:link(ref['construction']['proof_library'])
        assert ref['master_ids']==[indices[tuple(t['indices'])] for t in ref['master_coefficients']]
        assert ref['reduction_steps']==len(trace['steps'])
        assert trace['final_master_row']==ref['samples'][0]['master_coefficients']
        used=[];seeds=set();cost=dict(divisions=0,multiplications=0,subtractions=0)
        for step in trace['steps']:
            eq=identity[step['pivot_equation']]
            assert step['pivot_indices']==eq['leading_indices']
            assert step['pivot_equation'] in step['allowed_pivot_equations']
            assert all(p in identity for p in step['allowed_pivot_equations'])
            used.append(step['pivot_equation'])
            if eq['source']['kind']=='ibp':seeds.add(tuple(eq['source']['seed']))
            for k in cost:cost[k]+=step['operations'][k]
        assert list(dict.fromkeys(used))==ref['source_equations']
        assert sorted(seeds)==[tuple(s) for s in ref['sufficient_seeds']]
        assert cost==ref['arithmetic_operations']==trace['total_operations']
        for k in cost:operations[k]+=cost[k]
        total_steps+=len(trace['steps'])
    singles=sum(x['kind']=='single_integral' for x in inputs)
    assert singles==entry['single_integral'] and len(inputs)-singles==entry['integral_expression']
    metadata=next(records(name,'metadata'))
    assert metadata['elimination_steps']==total_steps and metadata['operation_counts']==operations
    if source:
        raw,meta,supp=old_family(source,original)
        assert metadata['original_source_hashes']=={k:dict(bytes=len(v),sha256=sha(v)) for k,v in raw.items()}
        compare_original(entry,raw,supp,inputs,refs,traces)
    return dict(family=name,split=entry['split'],masters=len(indices),targets=len(inputs),
        single_integrals=singles,integral_expressions=len(inputs)-singles,
        elimination_steps=total_steps,source_equations=len(identity),ids=ids,
        operation_counts=operations,files_checked=len(manifest['files']))
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--compare-source',type=Path)
    p.add_argument('--family',action='append')
    a=p.parse_args()
    if not os.environ.get('JOB_ID'):raise RuntimeError('Submit the collection audit through the scheduler.')
    catalog=read(ROOT/'catalog.json');entries=catalog['families']
    selected=[e for e in entries if not a.family or e['family'] in a.family]
    if a.family:assert len(selected)==len(set(a.family))
    source=a.compare_source.resolve() if a.compare_source else None
    original={e['family']:e for e in source_catalog(source)['families']} if source else {}
    definitions={d['id']:d for d in read(ROOT/'families.json')['families']}
    assert set(definitions)=={e['family'] for e in entries}
    checks=[];split_ids={'train':[],'validation':[],'test':[]}
    for i,e in enumerate(selected,1):
        assert next(records(e['family'],'definition'))==definitions[e['family']]
        result=verify_family(e,source,original.get(e['family']))
        split_ids[e['split']]+=result.pop('ids');checks.append(result)
        if i%25==0 or a.family:print('Checked',i,'/',len(selected),'families',flush=True)
    if a.family:
        print('Selected families passed all layout, linkage and source comparisons.',flush=True);return
    expected=read(ROOT/'splits.json')
    for split,ids in split_ids.items():
        assert len(ids)==len(set(ids)) and set(ids)==set(expected[split])
    assert not (set(split_ids['train'])&set(split_ids['validation']) or set(split_ids['train'])&set(split_ids['test']) or set(split_ids['validation'])&set(split_ids['test']))
    totals={k:sum(x[k] for x in checks) for k in ['masters','targets','single_integrals','integral_expressions','elimination_steps','source_equations','files_checked']}
    assert len(checks)==catalog['family_count']==1000
    assert totals['masters']==catalog['master_records']==9678
    assert totals['targets']==catalog['targets']==240472
    assert totals['single_integrals']==catalog['single_integrals']==55768
    assert totals['elimination_steps']==832924
    for split in split_ids:
        stats=catalog['split_counts'][split]
        for key in ['targets','single_integrals','integral_expressions']:
            assert sum(x[key] for x in checks if x['split']==split)==stats[key]
    source_manifest=read(ROOT/'master_to_target/generation_source_manifest.json')
    with tarfile.open(str(ROOT/'master_to_target/generation_source.tar.gz')) as tf:
        assert set(tf.getnames())==set(source_manifest['files'])
        for name,info in source_manifest['files'].items():
            data=tf.extractfile(name).read()
            assert len(data)==info['bytes'] and sha(data)==info['sha256']
    previous=read(ROOT/'validation_summary.json')
    proof=bool(source) or previous.get('migration_source_comparison')=='passed'
    assert proof,'A full comparison with the original data must precede publication.'
    write(ROOT/'validation_summary.json',dict(status='passed',family_count=1000,
        migration_source_comparison='passed',source_commit=catalog['source_commit'],
        source_mathematical_checks=previous['source_mathematical_checks'],
        layout_totals=totals,families=checks,
        statement='Master files, source equations, proofs, coefficients and elimination operations match the previously validated collection. Only storage paths, explicit master links and combined split labels changed.'))
    catalog['status']='validated';write(ROOT/'catalog.json',catalog)
    for category in ['master_integrals','target_integrals','master_to_target']:
        write(ROOT/category/'catalog.json',dict(status='validated',family_count=1000,
            master_records=9678,targets=240472,path_base='integrals/',
            families=[{k:v for k,v in e.items() if k not in ['origin']} for e in entries]))
    print(json.dumps(dict(status='passed',totals=totals),sort_keys=True),flush=True)
if __name__=='__main__':
    if read(ROOT/'catalog.json').get('higher_loop_validation'):
        import sys
        sys.path.insert(0,str(ROOT/'higher_loops'))
        from s10_validate_collection import main as expanded_main
        expanded_main()
    else:main()
