#!/usr/bin/env python3
"""Identify symbolic master bases with Kira; no training targets are constructed."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
PROJECT_LIMIT = 8_000_000_000  # Reserve room below the user's 10 GB total ceiling.
RUN_LIMIT = 256_000_000
RSS_LIMIT_KIB = 1_500_000
STAGES = ('discovery', 'expanded', 'independent_point')
POINTS = (
    dict(d=37, s=-13, t=-19, s1=-11, s2=-17, s3=-29, s4=-43, m2=7, m12=7, m22=23),
    dict(d=41, s=-31, t=-47, s1=-23, s2=-37, s3=-53, s4=-71, m2=11, m12=11, m22=29),
)
PRIMES = (2147483647, 1000000007)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.part')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    temporary.replace(path)


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def disk_bytes(path):
    # Kira renames and removes temporary files while it runs. Count the files
    # present during this sample; permission and other I/O errors still fail.
    def fail(error):
        if not isinstance(error, FileNotFoundError):
            raise error
    total = path.stat().st_size
    for directory, directories, files in os.walk(str(path), onerror=fail):
        for name in directories + files:
            try:
                total += (Path(directory) / name).lstat().st_size
            except FileNotFoundError:
                continue
    return total


def sector(indices):
    return sum(1 << i for i, a in enumerate(indices) if a > 0)


def validate_family(family):
    if not re.fullmatch(r'[a-z][a-z0-9_]*', family['id']):
        raise ValueError('Invalid family name')
    loops, external = len(family['loop_momenta']), len(family['external_momenta'])
    n = len(family['propagators'])
    if n != loops * (loops + 1) // 2 + loops * external:
        raise ValueError('The propagators must form a complete scalar-product basis')
    if len(family['scalarproduct_rules']) != external * (external + 1) // 2:
        raise ValueError('Missing external scalar-product rules')
    if len(set(family['invariants'])) != len(family['invariants']):
        raise ValueError('Repeated invariant')
    for value in family['top_level_sectors']:
        if value < 1 or value >= 1 << n:
            raise ValueError('Invalid top-level sector')
    for point in POINTS:
        if not set(family['invariants']).issubset(point):
            raise ValueError('Missing finite-field sample value')


def config_documents(family):
    integral = {'integralfamilies': [dict(
        name=family['id'], loop_momenta=family['loop_momenta'],
        top_level_sectors=family['top_level_sectors'],
        propagators=[[p['momentum'], p['mass_squared']] for p in family['propagators']]) ]}
    kinematics = {'kinematics': dict(
        incoming_momenta=family['external_momenta'], outgoing_momenta=[],
        momentum_conservation=[],
        kinematic_invariants=[[v, 2] for v in family['invariants']],
        scalarproduct_rules=family['scalarproduct_rules'])}
    return integral, kinematics


def profiles(family):
    # Probe all subsectors, with a buffer between probe and equation-generation bounds.
    t = max(bin(s).count('1') for s in family['top_level_sectors'])
    result = []
    for index, name in enumerate(STAGES):
        padding = 2 if index == 0 else 3
        point_index = 1 if index == 2 else 0
        result.append(dict(name=name,
            seed_bounds=dict(sectors=family['top_level_sectors'], r=t+padding, s=padding, d=padding),
            probe_bounds=dict(sectors=family['top_level_sectors'], r=t+padding-1, s=padding-1, d=padding-1),
            sample={v: POINTS[point_index][v] for v in ['d']+family['invariants']},
            prime=PRIMES[point_index]))
    return result


def parse_masters(text, family):
    pattern = re.compile(r'(?m)^\s*' + re.escape(family['id']) + r'\[([^\]]+)\]')
    found = []
    for match in pattern.finditer(text):
        indices = tuple(int(s.strip()) for s in match.group(1).split(','))
        if len(indices) != len(family['propagators']):
            raise ValueError('Wrong number of master indices')
        if not any((sector(indices) | top) == top for top in family['top_level_sectors']):
            raise ValueError('Master outside configured physical sectors')
        found.append(indices)
    if not found:
        raise ValueError('No masters found in a nonzero benchmark family')
    if len(found) != len(set(found)):
        raise ValueError('Duplicate master entries')
    return sorted(found, key=lambda a: (sector(a), sum(abs(v) for v in a), a))


def canonical_lines(family, masters):
    return ''.join('{}[{}]\n'.format(family['id'], ','.join(map(str, a))) for a in masters)


def limits():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_AS, (1792 * 1024**2, 1792 * 1024**2))
    resource.setrlimit(resource.RLIMIT_FSIZE, (128 * 1024**2, 128 * 1024**2))


def session_rss(pid):
    command = subprocess.run(['ps', '-s', str(pid), '-o', 'rss='],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return sum(int(x) for x in command.stdout.split())


def execute(command, work, logfile, seconds):
    start = time.monotonic()
    peak = 0
    with logfile.open('wb') as output:
        process = subprocess.Popen(command, cwd=str(work), stdout=output, stderr=subprocess.STDOUT,
                                   start_new_session=True, preexec_fn=limits)
        try:
            while process.poll() is None:
                peak = max(peak, session_rss(process.pid))
                if peak > RSS_LIMIT_KIB:
                    raise RuntimeError('Stopped before reaching the allocated memory limit')
                if time.monotonic() - start > seconds:
                    raise RuntimeError('Kira stage exceeded its time limit')
                if disk_bytes(work) > RUN_LIMIT or disk_bytes(PROJECT) > PROJECT_LIMIT:
                    raise RuntimeError('Stopped at the project or stage storage limit')
                time.sleep(1)
            if process.returncode:
                raise RuntimeError('Kira exited with code {}; see {}'.format(process.returncode, logfile))
        except BaseException:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            raise
    return dict(elapsed_seconds=round(time.monotonic()-start, 3),
                sampled_peak_session_rss_kib=peak, returncode=process.returncode)


def prepare(family):
    validate_family(family)
    directory = ROOT / 'families' / family['id']
    write_json(directory / 'definition.json', family)
    integral, kinematics = config_documents(family)
    # JSON is accepted by YAML-cpp and avoids a separate Python YAML dependency.
    write_json(directory / 'config' / 'integralfamilies.yaml', integral)
    write_json(directory / 'config' / 'kinematics.yaml', kinematics)
    return directory


def identify(family, args, executable_hash, version):
    directory = prepare(family)
    signature = hashlib.sha256(json.dumps(dict(
        family=family, profiles=profiles(family), generator=sha256(Path(__file__)),
        executable=executable_hash), sort_keys=True).encode()).hexdigest()
    final = directory / 'masters.json'
    if final.exists() and not args.rerun:
        previous = json.loads(final.read_text(encoding='utf-8'))
        if previous.get('input_signature') == signature and previous.get('status') == 'validated':
            print('Reuse {}: {} masters'.format(family['id'], len(previous['masters'])), flush=True)
            return previous
    write_json(directory / 'status.json', dict(status='running', input_signature=signature))
    reference = None
    checks = []
    try:
        for profile in profiles(family):
            work = ROOT / '.work' / family['id'] / profile['name']
            if work.exists():
                # This is only disposable engine state inside this generator's .work directory.
                shutil.rmtree(work)
            (work / 'config').mkdir(parents=True)
            for path in (directory / 'config').iterdir():
                shutil.copy2(str(path), str(work / 'config' / path.name))
            reduction = dict(reduce=[profile['seed_bounds']],
                select_integrals={'select_mandatory_recursively': [profile['probe_bounds']]},
                run_initiate='masters', run_triangular=False, run_back_substitution=False)
            if reference is not None:
                (work / 'preferred_masters').write_text(canonical_lines(family, reference), encoding='utf-8')
                reduction.update(preferred_masters='preferred_masters', check_masters=True)
            job = {'jobs': [{'reduce_sectors': reduction}]}
            write_json(work / 'jobs.yaml', job)
            destination = directory / 'validation' / profile['name']
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(work / 'jobs.yaml'), str(destination / 'jobs.yaml'))
            if reference is not None:
                shutil.copy2(str(work / 'preferred_masters'), str(destination / 'preferred_masters'))
            command = [str(args.kira), '--parallel=1', '--integral_ordering=1',
                       '--prime=' + str(profile['prime'])]
            command += ['--set_value={}={}'.format(k, v) for k, v in sorted(profile['sample'].items())]
            command.append('jobs.yaml')
            print('{}: {}'.format(family['id'], profile['name']), flush=True)
            run = dict(profile, command=command, hostname=socket.gethostname(),
                       scheduler_job_id=os.environ.get('JOB_ID'), input_signature=signature)
            write_json(destination / 'run.json', dict(run, status='running'))
            run.update(execute(command, work, destination / 'kira.log', args.timeout))
            raw = work / 'results' / family['id'] / 'masters'
            if not raw.is_file():
                raise RuntimeError('Kira did not produce its master list')
            masters = parse_masters(raw.read_text(encoding='utf-8'), family)
            shutil.copy2(str(raw), str(destination / 'masters.raw'))
            (destination / 'masters.txt').write_text(canonical_lines(family, masters), encoding='utf-8')
            if reference is None:
                reference = masters
            elif masters != reference:
                raise RuntimeError('Master basis changed during validation')
            run.update(status='passed', master_count=len(masters), master_indices=masters)
            write_json(destination / 'run.json', run)
            checks.append(run)
        records = []
        for index, powers in enumerate(reference, 1):
            records.append(dict(id='{}:M{:03d}'.format(family['id'], index),
                family=family['id'], indices=powers, sector=sector(powers),
                expression='{}[{}]'.format(family['id'], ','.join(map(str, powers))),
                mass_dimension='{}*d - ({})'.format(len(family['loop_momenta']), 2*sum(powers))))
        result = dict(schema_version=1, status='validated', family=family['id'],
            input_signature=signature, masters=records, kira_version=version,
            executable_sha256=executable_hash,
            validation='Same basis with expanded seeds and probes, then a second point and prime; Kira check_masters passed.',
            scope='Symbolic basis at generic kinematics. Finite-field and finite-domain checks are not an all-index proof.',
            stages=[c['name'] for c in checks])
        write_json(final, result)
        (directory / 'masters.txt').write_text(canonical_lines(family, reference), encoding='utf-8')
        write_json(directory / 'status.json', dict(status='validated', input_signature=signature))
        lines=['# '+family['title'], '',
               'These are symbolic master-integral definitions for the specified family. Numerical values and epsilon expansions are not calculated.', '',
               'The denominators use $D_i=q_i^2-m_i^2+i0$, with the momenta and squared masses listed below. The dimension is $d=4-2\\epsilon$.', '']
        for i, p in enumerate(family['propagators'], 1):
            lines.append('- D{}: momentum `{}`, mass squared `{}`.'.format(i,p['momentum'],p['mass_squared']))
        lines += ['', 'The scalar-product rules and assumptions are in [definition.json](definition.json). The listed top-level sectors include their subsectors.', '',
                  'Kira found {} master integrals:'.format(len(reference)), '', '```text',canonical_lines(family, reference).rstrip(), '```', '',
                  'All three validation runs returned this basis. Their exact inputs, sample points, primes and raw Kira output are in `validation/`.', '',
                  'The checks establish stability in the recorded domains. They do not prove completeness for every possible integer index or exceptional kinematic limit.', '']
        (directory / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
        return result
    except BaseException as error:
        if 'run' in locals() and 'destination' in locals():
            write_json(destination / 'run.json', dict(run, status='failed', error=str(error)))
        write_json(directory / 'status.json', dict(status='failed', input_signature=signature, error=str(error)))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', action='append', help='Family id; repeat to select several. Default: all.')
    parser.add_argument('--prepare', action='store_true', help='Write definitions/configuration only.')
    parser.add_argument('--rerun', action='store_true')
    parser.add_argument('--kira', type=Path, default=PROJECT/'.tools/kira/bin/kira')
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error('--timeout must be positive')
    catalog = json.loads((ROOT/'families.json').read_text(encoding='utf-8'))['families']
    names = [f['id'] for f in catalog]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate family identifiers')
    if args.family and set(args.family) - set(names):
        parser.error('Unknown family: '+', '.join(sorted(set(args.family)-set(names))))
    selected = [f for f in catalog if not args.family or f['id'] in args.family]
    if args.prepare:
        for family in selected:
            prepare(family)
        print('Prepared {} family definitions; no Kira jobs run.'.format(len(selected)))
        return
    if not os.environ.get('JOB_ID') and (socket.gethostname().startswith('login') or 'hoffman' in socket.getfqdn()):
        raise RuntimeError('Submit Master_Integrals/s04_run_masters.sh through qsub')
    args.kira = args.kira.resolve()
    if not args.kira.is_file():
        raise RuntimeError('Build Kira before generating masters')
    if disk_bytes(PROJECT) >= PROJECT_LIMIT or shutil.disk_usage(PROJECT).free < 1024**3:
        raise RuntimeError('Insufficient project storage headroom')
    (ROOT/'logs').mkdir(exist_ok=True)
    version = subprocess.check_output([str(args.kira),'--version'], cwd=str(ROOT/'logs'), stderr=subprocess.STDOUT).decode('utf-8',errors='replace').strip()
    digest = sha256(args.kira)
    for family in selected:
        identify(family,args,digest,version)
    entries=[]
    for family in catalog:
        directory=ROOT/'families'/family['id']
        if (directory/'masters.json').exists() and (directory/'status.json').exists():
            status=json.loads((directory/'status.json').read_text(encoding='utf-8'))
            result=json.loads((directory/'masters.json').read_text(encoding='utf-8'))
            if status['status']=='validated' and status['input_signature']==result['input_signature']:
                entries.append(dict(family=family['id'], loops=len(family['loop_momenta']),
                    master_count=len(result['masters']),path='families/'+family['id']+'/masters.json'))
    write_json(ROOT/'catalog.json',dict(schema_version=1,families=entries,
        validated_family_count=len(entries),master_records=sum(e['master_count'] for e in entries),
        counting_note='Counts are per family; masters in different families can represent related or identical integrals.'))
    print('Validated {} families with {} master records.'.format(len(entries),sum(e['master_count'] for e in entries)),flush=True)


if __name__=='__main__':
    main()
