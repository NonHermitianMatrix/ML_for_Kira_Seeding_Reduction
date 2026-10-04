#!/usr/bin/env python3
"""Reorganize the existing checked collection without generating new integrals."""
import argparse, copy, gzip, hashlib, io, json, os, shutil, subprocess, tarfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
CATEGORIES=('master_integrals','target_integrals','master_to_target')
ORIGINAL=('Master_Integrals','master_to_target','Expanded_Integrals')
def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def encoded(value): return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(data): return hashlib.sha256(data).hexdigest()
def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def put(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.part');tmp.write_bytes(data);tmp.replace(path)
def write(path,value):put(path,(json.dumps(value,indent=2,sort_keys=True)+'\n').encode())
def zipped(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.part')
    with tmp.open('wb') as raw:
        with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0,compresslevel=6) as f:f.write(data)
    tmp.replace(path)
def archive(path,files):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.part')
    with tmp.open('wb') as raw:
        with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0,compresslevel=6) as z:
            with tarfile.open(fileobj=z,mode='w') as tf:
                for name,data in sorted(files.items()):
                    info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;info.mtime=0
                    tf.addfile(info,io.BytesIO(data))
    tmp.replace(path)
def rows(data):return [json.loads(line) for line in data.splitlines() if line.strip()]
_LAST_GUARD=0
def guard():
    global _LAST_GUARD
    if time.monotonic()-_LAST_GUARD<30:return
    result=subprocess.run(['du','-sk',str(PROJECT)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    errors=result.stderr.decode()
    if result.returncode and not all('No such file' in line or 'Stale file handle' in line for line in errors.splitlines()):
        raise RuntimeError(errors)
    used=int(result.stdout.split()[0])*1024
    _LAST_GUARD=time.monotonic()
    if used>6_000_000_000 or shutil.disk_usage(PROJECT).free<2_000_000_000:
        raise RuntimeError('Storage guard reserves space below the 10 GB ceiling.')
def source_catalog(source):return read(source/'Expanded_Integrals/catalog.json')
def old_family(source,entry):
    name=entry['family'];raw={};metadata=None;supplement=None
    if entry['origin']=='expanded_collection':
        metadata=read(source/'Expanded_Integrals'/entry['metadata'])
        path=source/'Expanded_Integrals'/entry['archive']
        assert file_sha(path)==entry['archive_sha256']
        with tarfile.open(str(path),'r:gz') as tf:
            manifest=json.load(tf.extractfile('manifest.json'))
            for member,expected in manifest['files'].items():
                data=tf.extractfile(member).read()
                assert len(data)==expected['bytes'] and sha(data)==expected['sha256']
                raw[member]=data
    else:
        for folder in ['Master_Integrals','master_to_target']:
            base=source/folder/'families'/name
            for p in sorted(base.rglob('*')):
                if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.part'):
                    raw[str(p.relative_to(source))]=p.read_bytes()
    catalog=source_catalog(source)
    extra=catalog.get('individual_supplements',{}).get(name)
    if extra:
        path=source/'Expanded_Integrals'/extra['path']
        assert file_sha(path)==extra['sha256']
        with gzip.open(str(path),'rt',encoding='utf-8') as f:supplement=json.load(f)
    return raw,metadata,supplement
def locations(name):
    return {k:k+'/families/'+name for k in CATEGORIES}
def family_entry(old):
    p=locations(old['family'])
    out={k:old[k] for k in ['family','split','master_count','targets','single_integral','integral_expression','origin']}
    out.update(master_basis=p['master_integrals']+'/masters.json',
        definition=p['master_integrals']+'/definition.json',
        targets_file=p['target_integrals']+'/inputs.jsonl.gz',
        references=p['master_to_target']+'/references.jsonl.gz',
        traces=p['master_to_target']+'/elimination_traces.jsonl.gz',
        records=p['master_to_target'],manifest=p['master_to_target']+'/manifest.json')
    return out
def prepare(source):
    guard();old=source_catalog(source)
    assert old['status']=='validated' and old['family_count']==1000
    files={}
    for folder in ORIGINAL:
        for p in sorted((source/folder).iterdir()):
            if p.is_file():files[str(p.relative_to(source))]=p.read_bytes()
    archive(ROOT/'master_to_target/generation_source.tar.gz',files)
    write(ROOT/'master_to_target/generation_source_manifest.json',
        dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=str(source)).decode().strip(),
             description='Original source programs, documentation, catalogs and validation reports; historical paths.',
             files={k:dict(bytes=len(v),sha256=sha(v)) for k,v in files.items()}))
    catalog={k:v for k,v in old.items() if k not in ['families','individual_supplements','initial_split_overrides','split_overlap_witnesses']}
    catalog.update(schema_version=3,status='reorganizing',families=[family_entry(x) for x in old['families']],
                   path_base='integrals/',link_key='family and target id',
                   source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=str(source)).decode().strip(),
                   original_validation='master_to_target/generation_source.tar.gz::Expanded_Integrals/validation_summary.json')
    write(ROOT/'catalog.json',catalog)
    original=read(source/'Master_Integrals/families.json')['families']
    expanded=read(source/'Expanded_Integrals/families.json')['families']
    write(ROOT/'families.json',dict(family_count=1000,families=original+expanded))
    put(ROOT/'splits.json',(source/'Expanded_Integrals/splits.json').read_bytes())
    put(ROOT/'master_to_target/split_overlap_witnesses.json',(source/'Expanded_Integrals/split_overlap_witnesses.json').read_bytes())
    write(ROOT/'validation_summary.json',dict(status='pending',source_mathematical_checks=read(source/'Expanded_Integrals/validation_summary.json')['totals']))
    print('Prepared unified catalogs and preserved the original generation source.',flush=True)
def convert(source,old):
    name=old['family'];p=locations(name)
    raw,metadata,supp=old_family(source,old)
    mb='Master_Integrals/families/'+name+'/'
    tb='master_to_target/families/'+name+'/'
    basis=json.loads(raw[mb+'masters.json'])
    mid={tuple(m['indices']):m['id'] for m in basis['masters']}
    for filename in ['masters.json','masters.txt','definition.json']:
        put(ROOT/p['master_integrals']/filename,raw[mb+filename])
    checks={k[len(mb):]:v for k,v in raw.items() if k.startswith(mb) and k[len(mb):] not in ['masters.json','masters.txt','definition.json']}
    archive(ROOT/p['master_integrals']/'basis_checks.tar.gz',checks)
    inputs=rows(raw[tb+'inputs.jsonl']);refs=rows(raw[tb+'references.jsonl']);traces=rows(raw[tb+'elimination_traces.jsonl'])
    if supp:
        inputs+=supp['inputs'];refs+=supp['references'];traces+=supp['elimination_traces']
    assert len(inputs)==len(refs)==len(traces)==old['targets']
    assert sum(x['kind']=='single_integral' for x in inputs)==old['single_integral']
    for x in inputs:
        if x['split']!=old['split']:x['stored_split']=x['split'];x['split']=old['split']
        x['master_basis']=p['master_integrals']+'/masters.json'
        x['family_definition']=p['master_integrals']+'/definition.json'
        x['candidate_seeds']=p['master_to_target']+'/candidate_seeds.json'
        x['equation_pool']=p['master_to_target']+'/identities.jsonl.gz'
        x['reference_records']=p['master_to_target']+'/references.jsonl.gz'
        x['elimination_records']=p['master_to_target']+'/elimination_traces.jsonl.gz'
        x.pop('source_archive',None)
    for x in refs:
        if x['split']!=old['split']:x['stored_split']=x['split'];x['split']=old['split']
        if 'proof_library' in x['construction']:
            x['construction']['proof_library']=p['master_to_target']+'/construction_proofs.jsonl.gz'
        x['master_ids']=[mid[tuple(t['indices'])] for t in x['master_coefficients']]
        x['target_records']=p['target_integrals']+'/inputs.jsonl.gz'
        x['master_basis']=p['master_integrals']+'/masters.json'
        x['elimination_records']=p['master_to_target']+'/elimination_traces.jsonl.gz'
    zipped(ROOT/p['target_integrals']/'inputs.jsonl.gz',b''.join(encoded(x) for x in inputs))
    for filename,records in [('references.jsonl.gz',refs),('elimination_traces.jsonl.gz',traces)]:
        zipped(ROOT/p['master_to_target']/filename,b''.join(encoded(x) for x in records))
    for filename in ['identities.jsonl','construction_proofs.jsonl']:
        zipped(ROOT/p['master_to_target']/(filename+'.gz'),raw[tb+filename])
    for filename in ['candidate_seeds.json','symmetries.json']:
        put(ROOT/p['master_to_target']/filename,raw[tb+filename])
    generation={k[len(tb):]:v for k,v in raw.items() if k.startswith(tb) and k[len(tb):] in ['definition.json','summary.json','validation.json']}
    if metadata:generation['family_metadata.json']=encoded(metadata)
    if supp:generation['additional_targets_metadata.json']=encoded({k:v for k,v in supp.items() if k not in ['inputs','references','elimination_traces']})
    archive(ROOT/p['master_to_target']/'generation_records.tar.gz',generation)
    entry=family_entry(old)
    entry.update(status='validated',elimination_steps=sum(len(x['steps']) for x in traces),
        operation_counts={k:sum(x['arithmetic_operations'][k] for x in refs) for k in ['divisions','multiplications','subtractions']},
        source_equations=len(rows(raw[tb+'identities.jsonl'])),
        original_source_hashes={k:dict(bytes=len(v),sha256=sha(v)) for k,v in raw.items()})
    if supp:entry['additional_individual_targets']=len(supp['inputs'])
    write(ROOT/p['master_to_target']/'metadata.json',entry)
    actual={}
    for directory in p.values():
        for path in sorted((ROOT/directory).iterdir()):
            if path.is_file() and path.name!='manifest.json' and not path.name.endswith('.part'):
                actual[str(path.relative_to(ROOT))]=dict(bytes=path.stat().st_size,sha256=file_sha(path))
    write(ROOT/p['master_to_target']/'manifest.json',dict(family=name,files=actual))
    print(name,old['master_count'],len(inputs),'converted',flush=True)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=PROJECT)
    ap.add_argument('--prepare',action='store_true')
    ap.add_argument('--family',action='append')
    ap.add_argument('--batch-index',type=int,default=int(os.environ.get('SGE_TASK_ID','1')) if os.environ.get('SGE_TASK_ID','1').isdigit() else 1)
    ap.add_argument('--batch-size',type=int,default=50)
    args=ap.parse_args();source=args.source.resolve()
    if args.prepare:prepare(source);return
    if not os.environ.get('JOB_ID'):raise RuntimeError('Submit through the Hoffman scheduler.')
    guard()
    entries=source_catalog(source)['families']
    if args.family:
        selected=[x for x in entries if x['family'] in args.family]
        assert len(selected)==len(set(args.family))
    else:
        start=(args.batch_index-1)*args.batch_size
        selected=entries[start:start+args.batch_size]
    for i,entry in enumerate(selected):
        if i%10==0:guard()
        convert(source,entry)
if __name__=='__main__':main()
