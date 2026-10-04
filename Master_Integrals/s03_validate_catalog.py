#!/usr/bin/env python3
"""Check catalog consistency, Kira evidence, domain expansion and simple known cases."""
import argparse
import importlib.util
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('master_generator', ROOT/'s02_generate_masters.py')
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def check_family(family):
    directory=ROOT/'families'/family['id']
    result=read(directory/'masters.json')
    status=read(directory/'status.json')
    assert status['status']==result['status']=='validated'
    assert status['input_signature']==result['input_signature']
    g.validate_family(family)
    assert read(directory/'definition.json')==family
    expected_config=g.config_documents(family)
    for file,expected in zip(['integralfamilies.yaml','kinematics.yaml'],expected_config):
        assert read(directory/'config'/file)==expected
    indices=[tuple(m['indices']) for m in result['masters']]
    assert len(indices)==len(set(indices)) and indices
    for m in result['masters']:
        assert m['family']==family['id']
        assert m['sector']==g.sector(m['indices'])
    assert g.parse_masters((directory/'masters.txt').read_text(encoding='utf-8'),family)==indices
    runs=[]
    for stage in g.STAGES:
        directory_stage=directory/'validation'/stage
        run=read(directory_stage/'run.json')
        assert run['status']=='passed' and run['returncode']==0
        assert run['input_signature']==result['input_signature']
        assert [tuple(v) for v in run['master_indices']]==indices
        assert g.parse_masters((directory_stage/'masters.raw').read_text(encoding='utf-8'),family)==indices
        job=read(directory_stage/'jobs.yaml')['jobs'][0]['reduce_sectors']
        assert job['run_initiate']=='masters'
        assert job['run_triangular'] is False and job['run_back_substitution'] is False
        assert job['reduce']==[run['seed_bounds']]
        assert job['select_integrals']['select_mandatory_recursively']==[run['probe_bounds']]
        if stage!='discovery':
            assert job['check_masters'] is True
            assert g.parse_masters((directory_stage/'preferred_masters').read_text(encoding='utf-8'),family)==indices
        log=(directory_stage/'kira.log').read_text(encoding='utf-8')
        counts=[int(x) for x in re.findall(r'Number of master integrals:\s*(\d+)',log)]
        assert counts and counts[-1]==len(indices)
        runs.append(run)
    for key in ['r','s','d']:
        assert runs[1]['seed_bounds'][key]>runs[0]['seed_bounds'][key]
        assert runs[1]['probe_bounds'][key]>runs[0]['probe_bounds'][key]
    assert runs[1]['sample']!=runs[2]['sample']
    assert runs[1]['prime']!=runs[2]['prime']
    # Independent simple-family regression checks; representatives can change under symmetry.
    expected_counts={'tadpole_massive':1,'bubble_massless':1,'bubble_one_mass':2,
                     'bubble_equal_mass':2,'bubble_two_mass':3,'box_massless_onshell':3}
    if family['id'] in expected_counts:
        assert len(indices)==expected_counts[family['id']], 'Known simple-family count differs'
    if family['id']=='tadpole_massive':
        assert indices==[(1,)]
    if family['id']=='bubble_massless':
        assert indices==[(1,1)]
    return dict(family=family['id'],master_count=len(indices),checks_passed=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-all',action='store_true')
    args=parser.parse_args()
    families=read(ROOT/'families.json')['families']
    checked=[]
    missing=[]
    for family in families:
        if not (ROOT/'families'/family['id']/'masters.json').exists():
            missing.append(family['id'])
            continue
        checked.append(check_family(family))
    assert checked, 'No generated master bases to check'
    if args.require_all:
        assert not missing, 'Missing families: '+', '.join(missing)
    catalog=read(ROOT/'catalog.json')
    assert catalog['validated_family_count']==len(checked)
    assert catalog['master_records']==sum(c['master_count'] for c in checked)
    g.write_json(ROOT/'validation_summary.json',dict(status='passed',families=checked,
        missing_families=missing,complete_requested_catalog=not missing,
        scope='Checks consistency and finite-domain evidence; does not prove an all-index theorem.'))
    print('Passed checks for {} families and {} master records.'.format(len(checked),catalog['master_records']))


if __name__=='__main__':
    main()
