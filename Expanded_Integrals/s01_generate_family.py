#!/usr/bin/env python3
"""Run Kira, reverse construction and exact validation for one expanded family."""
import argparse, gc, hashlib, importlib.util, json, os, resource, shutil, socket
import subprocess, sys, tarfile, time, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
sys.path.insert(0,str(PROJECT/'master_to_target'))
import s00_ibp as ibp
import s01_generate_targets as gen
import s02_validate_targets as val
spec=importlib.util.spec_from_file_location('basis_generator',PROJECT/'Master_Integrals/s02_generate_masters.py')
basis=importlib.util.module_from_spec(spec); spec.loader.exec_module(basis)
from s00_prepare_families import POINTS, PRIMES

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.part')
    tmp.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    tmp.replace(path)

_SIZE_CACHE={}
def disk_bytes(path):
    # NFS can report ENOENT or ESTALE while other tasks remove archived work.
    path=Path(path)
    cached=_SIZE_CACHE.get(str(path))
    if path==PROJECT and cached and time.monotonic()-cached[0]<15:
        return cached[1]
    def onerror(error):
        if getattr(error,'errno',None) not in (2,116): raise error
    total=0
    for directory,_,files in os.walk(str(path),onerror=onerror):
        for name in files:
            try: total+=(Path(directory)/name).stat().st_size
            except OSError as error: onerror(error)
    _SIZE_CACHE[str(path)]=(time.monotonic(),total)
    return total


def headroom():
    if disk_bytes(PROJECT)>6_000_000_000:
        raise RuntimeError('Project guard at 6 GB reserves space for Git and archives below 10 GB.')
    if shutil.disk_usage(PROJECT).free<2_000_000_000:
        raise RuntimeError('Less than 2 GB filesystem headroom.')

def archive(work,destination,name):
    paths=[]
    for folder in [work/'Master_Integrals/families'/name,work/'master_to_target/families'/name]:
        paths.extend(p for p in folder.rglob('*') if p.is_file())
    manifest={}
    for p in sorted(paths):
        relative=str(p.relative_to(work))
        manifest[relative]=dict(bytes=p.stat().st_size,sha256=gen.digest_file(p))
    write(work/'manifest.json',dict(family=name,files=manifest))
    paths.append(work/'manifest.json')
    temp=destination.with_suffix('.part')
    with tarfile.open(str(temp),'w:gz',compresslevel=6) as out:
        for p in sorted(paths):
            info=out.gettarinfo(str(p),arcname=str(p.relative_to(work)))
            info.uid=info.gid=0; info.uname=info.gname=''; info.mtime=0
            with p.open('rb') as stream: out.addfile(info,stream)
    if temp.stat().st_size>40_000_000:
        raise RuntimeError('Family archive exceeds 40 MB file guard.')
    temp.replace(destination)
    return manifest

def run(index,args):
    headroom()
    catalog=json.loads((ROOT/'families.json').read_text())
    definition=catalog['families'][index-1]
    name=definition['id']; split=definition['profile']['split']
    destination=ROOT/'families'/name
    destination.parent.mkdir(exist_ok=True)
    status_path=destination.with_suffix('.json')
    if status_path.exists() and not args.rerun:
        status=json.loads(status_path.read_text())
        if status.get('status')=='validated' and destination.with_suffix('.tar.gz').is_file():
            assert status['archive_sha256']==gen.digest_file(destination.with_suffix('.tar.gz'))
            print('Already validated '+name,flush=True); return
    work=ROOT/'.work'/name
    if work.exists(): shutil.rmtree(work)
    work.mkdir(parents=True)
    started=time.monotonic()
    write(status_path,dict(family=name,status='running',job_id=os.environ.get('JOB_ID'),hostname=socket.gethostname()))
    try:
        basis.ROOT=work/'Master_Integrals'; basis.PROJECT=PROJECT
        basis.POINTS=POINTS[:2]; basis.PRIMES=PRIMES[:2]
        basis.RUN_LIMIT=200_000_000
        basis.disk_bytes=disk_bytes
        kira=PROJECT/'.tools/kira/bin/kira'
        version=subprocess.check_output([str(kira),'--version'],cwd=str(work),stderr=subprocess.STDOUT).decode().strip()
        master=basis.identify(definition,argparse.Namespace(kira=kira,rerun=False,timeout=120),
                              basis.sha256(kira),version)
        targetroot=work/'master_to_target'; targetroot.mkdir(exist_ok=True)
        for f in ['s00_ibp.py','s01_generate_targets.py','s02_validate_targets.py']:
            shutil.copy2(PROJECT/'master_to_target'/f,targetroot/f)
        for module in [ibp,gen,val]:
            module.ROOT=targetroot; module.PROJECT=work; module.POINTS=POINTS; module.PRIMES=PRIMES
        gen.TEST={name} if split=='test' else set()
        gen.VALIDATION={name} if split=='validation' else set()
        gen.DATA_LIMIT=300_000_000
        opts=argparse.Namespace(chains=args.chains,depth=args.depth,max_individual=args.individual,seed=20261004)
        generation_mode="current_seed"
        try:
            if args.connected:
                raise RuntimeError(name+": no accepted targets")
            generated=gen.generate_family(definition,opts)
        except RuntimeError as error:
            if str(error)!=name+": no accepted targets":
                raise
            ibp.Family.text.cache_clear(); ibp.Family.evaluate.cache_clear()
            connected_path=ROOT/'s06_generate_connected_targets.py'
            spec2=importlib.util.spec_from_file_location('connected_generator',connected_path)
            connected=importlib.util.module_from_spec(spec2); spec2.loader.exec_module(connected)
            connected.ROOT=targetroot; connected.PROJECT=work
            connected.POINTS=POINTS; connected.PRIMES=PRIMES
            connected.TEST=gen.TEST; connected.VALIDATION=gen.VALIDATION
            connected.DATA_LIMIT=gen.DATA_LIMIT
            shutil.copy2(connected_path,targetroot/'s01_generate_targets.py')
            generated=connected.generate_family(definition,opts)
            generation_mode="any_identity_containing_current_term"
        gc.collect()
        summary,validation,ids=val.validate_family(targetroot/'families'/name)
        # Verify input features as well as mathematical replay.
        folder=targetroot/'families'/name
        for inp in val.lines(folder/'inputs.jsonl'):
            expected=[dict(indices=t['indices'],**ibp.complexity(t['indices'])) for t in inp['terms']]
            assert {tuple(x['indices']):x for x in inp['integral_features']}=={tuple(x['indices']):x for x in expected}
        headroom()
        compressed=destination.with_suffix('.tar.gz')
        manifest=archive(work,compressed,name)
        result=dict(family=name,status='validated',definition=definition,split=split,generation_mode=generation_mode,
          masters=master['masters'],master_count=len(master['masters']),
          target_summary=summary,validation=validation,target_ids=ids,
          archive=compressed.name,archive_sha256=gen.digest_file(compressed),
          archive_bytes=compressed.stat().st_size,uncompressed_data_bytes=sum(x['bytes'] for x in manifest.values()),
          elapsed_seconds=round(time.monotonic()-started,3),
          peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
          source_sha256={str(p.relative_to(PROJECT)):gen.digest_file(p) for p in [
             Path(__file__),ROOT/'s00_prepare_families.py',ROOT/'s06_generate_connected_targets.py',PROJECT/'Master_Integrals/s02_generate_masters.py',
             PROJECT/'master_to_target/s00_ibp.py',PROJECT/'master_to_target/s01_generate_targets.py',
             PROJECT/'master_to_target/s02_validate_targets.py']})
        write(status_path,result)
        shutil.rmtree(work)
        print(json.dumps({k:result[k] for k in ['family','status','master_count','archive_bytes','elapsed_seconds']},
                         sort_keys=True),flush=True)
    except BaseException as error:
        write(status_path,dict(family=name,status='failed',error=str(error),traceback=traceback.format_exc(),
                             elapsed_seconds=round(time.monotonic()-started,3)))
        raise

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--index',type=int,default=int(os.environ.get('SGE_TASK_ID','1')))
    parser.add_argument('--chains',type=int,default=48)
    parser.add_argument('--depth',type=int,default=4)
    parser.add_argument('--individual',type=int,default=96)
    parser.add_argument('--rerun',action='store_true')
    parser.add_argument('--connected',action='store_true')
    args=parser.parse_args()
    if not os.environ.get('JOB_ID'): raise RuntimeError('Run through the Hoffman scheduler.')
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    run(args.index,args)
if __name__=='__main__': main()
