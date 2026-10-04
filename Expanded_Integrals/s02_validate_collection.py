#!/usr/bin/env python3
"""Audit every compressed family and build the combined 1,000-family catalog."""
import collections, hashlib, json, os, tarfile
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
from s00_prepare_families import canonical,valid_gram,definition as build_definition
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path,data): path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()
def archive_check(path,status):
    assert sha(path)==status['archive_sha256']
    with tarfile.open(str(path),'r:gz') as tf:
        members=tf.getmembers()
        names=[x.name for x in members]
        assert len(names)==len(set(names))
        for m in members:
            assert m.isfile() and not PurePosixPath(m.name).is_absolute() and '..' not in PurePosixPath(m.name).parts
        manifest=json.load(tf.extractfile('manifest.json'))
        assert manifest['family']==status['family']
        assert set(manifest['files'])==set(names)-{'manifest.json'}
        for name,expected in manifest['files'].items():
            member=tf.getmember(name)
            assert member.size==expected['bytes']
            digest=hashlib.sha256()
            with tf.extractfile(member) as stream:
                for chunk in iter(lambda:stream.read(1024*1024),b''): digest.update(chunk)
            assert digest.hexdigest()==expected['sha256'],name
        base='Master_Integrals/families/'+status['family']+'/'
        basis=json.load(tf.extractfile(base+'masters.json'))
        assert basis['status']=='validated' and basis['masters']==status['masters']
        for stage in ['discovery','expanded','independent_point']:
            run=json.load(tf.extractfile(base+'validation/'+stage+'/run.json'))
            assert run['status']=='passed' and run['returncode']==0
            assert run['master_indices']==[m['indices'] for m in basis['masters']]
        root='master_to_target/families/'+status['family']+'/'
        assert json.load(tf.extractfile(root+'summary.json'))==status['target_summary']
        assert json.load(tf.extractfile(root+'validation.json'))==status['validation']
        summary=status['target_summary']
        implementation=(ROOT/'s06_generate_connected_targets.py' if
           summary['generation'].get('reverse_candidates') else PROJECT/'master_to_target/s01_generate_targets.py')
        assert summary['source_sha256']['s01_generate_targets.py']==sha(implementation)
        assert summary['source_sha256']['s00_ibp.py']==sha(PROJECT/'master_to_target/s00_ibp.py')
        assert status['validation']['source_sha256']['s02_validate_targets.py']==sha(PROJECT/'master_to_target/s02_validate_targets.py')
        for filename,number in [('inputs.jsonl',status['target_summary']['targets']),
                                ('references.jsonl',status['target_summary']['targets']),
                                ('elimination_traces.jsonl',status['target_summary']['targets']),
                                ('identities.jsonl',status['target_summary']['equations'])]:
            with tf.extractfile(root+filename) as stream:
                assert sum(1 for line in stream if line.strip())==number
    return len(manifest['files'])

def main():
    expected=read(ROOT/'families.json')
    original=read(PROJECT/'master_to_target/catalog.json')
    oldbasis=read(PROJECT/'Master_Integrals/catalog.json')
    oldchecks=read(PROJECT/'master_to_target/validation_summary.json')
    assert original['status']=='validated' and original['family_count']==16
    assert oldchecks['status']=='passed' and oldchecks['complete_catalog']
    assert oldbasis['validated_family_count']==16
    splits=read(PROJECT/'master_to_target/splits.json')
    ids={key:list(splits[key]) for key in ['train','validation','test']}
    reassigned={'bubble_two_mass','triangle_massless_three_offshell'}
    moved=[identifier for identifier in ids['validation'] if identifier.split(':')[0] in reassigned]
    ids['validation']=[identifier for identifier in ids['validation'] if identifier not in set(moved)]
    ids['train'].extend(moved)
    rows=[];checks=[]; signatures=set(); group_split={}
    for old in original['families']:
        name=old['family']
        basis=read(PROJECT/'Master_Integrals/families'/name/'masters.json')
        assert basis['status']=='validated'
        entry=dict(old)
        if name in reassigned:
            entry['stored_split']=entry['split'];entry['split']='train'
        rows.append(dict(entry,master_count=len(basis['masters']),origin='initial_collection',
                  master_path='../Master_Integrals/families/'+name,
                  target_path='../master_to_target/families/'+name))
    for number,definition in enumerate(expected['families'],1):
        name=definition['id']; status=read(ROOT/'families'/(name+'.json'))
        assert status['status']=='validated',name
        assert status['definition']==definition
        profile=definition['profile']
        reconstructed=build_definition(number,(profile['mass_labels'],profile['distance_labels']))
        assert json.loads(json.dumps(reconstructed))==definition
        signature=canonical(profile['mass_labels'],profile['distance_labels'])
        assert signature not in signatures and valid_gram(signature[1])
        signatures.add(signature)
        assert tuple(map(tuple,signature))==(tuple(profile['mass_labels']),tuple(profile['distance_labels']))
        group=tuple(profile['kinematic_group'])
        assert group_split.setdefault(group,status['split'])==status['split']
        files=archive_check(ROOT/'families'/status['archive'],status)
        summary=status['target_summary'];validation=status['validation']
        assert summary['status']=='validated' and validation['status']=='passed'
        assert len(status['target_ids'])==summary['targets']
        ids[status['split']].extend(status['target_ids'])
        rows.append(dict(family=name,split=status['split'],master_count=status['master_count'],
              targets=summary['targets'],single_integral=summary['single_integral'],
              integral_expression=summary['integral_expression'],origin='expanded_collection',
              archive='families/'+status['archive'],metadata='families/'+name+'.json',
              archive_sha256=status['archive_sha256'],archive_bytes=status['archive_bytes'],
              independent_squared_scales=len(definition['invariants']),kinematic_group=list(group),
              generation_mode=status.get('generation_mode','current_seed')))
        checks.append(dict(family=name,archive_files_checked=files,**{k:v for k,v in validation.items() if k!='family'}))
        if number%50==0: print('Checked %d/%d expanded archives'%(number,len(expected['families'])),flush=True)
    assert len(rows)==1000
    for split,values in ids.items(): assert len(values)==len(set(values)),split
    assert not (set(ids['train'])&set(ids['validation']) or set(ids['train'])&set(ids['test']) or set(ids['validation'])&set(ids['test']))
    totals=dict(family_count=len(rows),master_records=sum(x['master_count'] for x in rows),
                targets=sum(x['targets'] for x in rows),
                single_integrals=sum(x['single_integral'] for x in rows),
                integral_expressions=sum(x['integral_expression'] for x in rows))
    split_counts={split:dict(families=sum(x['split']==split for x in rows),
                     targets=len(values),single_integrals=sum(x['single_integral'] for x in rows if x['split']==split),
                     integral_expressions=sum(x['integral_expression'] for x in rows if x['split']==split))
                  for split,values in ids.items()}
    allchecks=oldchecks['families']+checks
    countkeys=['symbolic_constructions_checked','symbolic_elimination_steps_checked','equation_rows_rederived',
               'source_ibp_rows_checked_by_independent_differentiation','closure_proofs_checked']
    validation_totals={key:sum(x[key] for x in allchecks) for key in countkeys}
    metadata=dict(status='validated',**totals,split_counts=split_counts,
        topology_coverage=dict(one_loop_families=997,two_loop_families=3,
           additional_profiles='984 inequivalent mass and squared-distance assignments for one-loop four-propagator integrals.'),
        counting_note='Masters counted within each family; shared lower-sector integrals can occur across families. Family count does not count distinct graph topologies.',
        split_policy=expected['split_policy']+' Initial validation bubble and triangle reassigned to training because they occur as lower sectors of expanded training families.',
        initial_split_overrides={name:'train' for name in sorted(reassigned)},
        split_overlap_witnesses=read(ROOT/'split_overlap_witnesses.json'),
        optimality='Recorded valid reductions; minimum seed and operation counts are not established.',
        limits='Bounded one-loop and two-loop constructions. Dataset size does not establish model accuracy or high-loop generalization.',
        families=rows)
    write(ROOT/'catalog.json',metadata)
    write(ROOT/'splits.json',dict(policy=metadata['split_policy'],initial_split_overrides=metadata['initial_split_overrides'],**ids))
    write(ROOT/'validation_summary.json',dict(status='passed',family_count=1000,archive_count=len(checks),
        canonical_profiles_checked=len(signatures),kinematic_groups=len(group_split),
        totals=validation_totals,expanded_families=checks,
        initial_validation_path='../master_to_target/validation_summary.json'))
    print(json.dumps(dict(totals=totals,split_counts=split_counts,validation=validation_totals),sort_keys=True),flush=True)
if __name__=='__main__': main()
