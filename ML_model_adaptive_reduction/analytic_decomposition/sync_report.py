"""Copy only published report files and guides; verify each Git blob locally."""
import argparse,hashlib,json,os,re,shlex,subprocess,tarfile
from pathlib import Path
ROOT=Path('/home/physics/projects/ML_for_Kira_SeedReduction')
REMOTE='/u/home/r/rushil/ML_for_Kira_Seeding_Reduction'
SSH=['ssh','-i','/home/physics/.ssh/hoffman2_key','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','ConnectTimeout=20','-o','ServerAliveInterval=30','-o','ServerAliveCountMax=2','rushil@hoffman2.idre.ucla.edu']
def command(code):
 return 'export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1; source /u/local/Modules/default/init/modules.sh; module load gcc/9.5.0 git/2.40.0 python/3.9.6; cd '+shlex.quote(REMOTE)+"; python - <<'PY'\n"+code+'\nPY'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('commit');a=ap.parse_args();assert re.fullmatch('[a-f0-9]{40}',a.commit)
 code=f'''import hashlib,json,pathlib,subprocess
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()=={a.commit!r}
entries=subprocess.check_output(['git','ls-tree','-r','-z','HEAD','--','report','rules.md','README.md','.gitignore'])
blobs={{}}
for entry in entries.split(b'\\0'):
 if not entry:continue
 meta,name=entry.split(b'\\t',1);mode,kind,oid=meta.decode().split();name=name.decode()
 assert kind=='blob' and mode in ['100644','100755']
 data=pathlib.Path(name).read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\\0'+data).hexdigest();assert actual==oid,name
 blobs[name]=dict(mode=mode,oid=oid)
print(json.dumps(dict(commit={a.commit!r},blobs=blobs)))'''
 # Preserve local report edits that differ from the last synchronized publication.
 baseline=ROOT/'.tools/report-sync/higher_scattering_report_manifest.json'
 if not baseline.exists():baseline=ROOT/'.tools/report-sync/editorial_report_manifest.json'
 conflicts=[];preserved_bytes=0
 ignore=ROOT/'.gitignore'
 if ignore.is_file():
  backup=ROOT/'.tools/report-sync/higher_scattering_preserved_edits/.gitignore';backup.parent.mkdir(parents=True,exist_ok=True)
  if not backup.exists():backup.write_bytes(ignore.read_bytes())
 if baseline.exists():
  prior=json.loads(baseline.read_text())['blobs']
  for name,entry in prior.items():
   q=ROOT/name
   if not q.is_file():continue
   data=q.read_bytes();oid=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
   if oid!=entry['oid']:
    dest=ROOT/'.tools/report-sync/higher_scattering_preserved_edits'/name
    preserved_bytes+=len(data);assert len(data)<28*1024**2 and preserved_bytes<64*1024**2
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and dest.read_bytes()!=data:dest=dest.with_name(dest.name+'.'+hashlib.sha256(data).hexdigest()[:12])
    if not dest.exists():dest.write_bytes(data)
    conflicts.append(name)
  print(json.dumps(dict(preserved_local_edits=conflicts)),flush=True)
 manifest=json.loads(subprocess.check_output(SSH+[command(code)],timeout=180));allowed=manifest['blobs']
 assert all(n.startswith('report/') or n in ['rules.md','README.md','.gitignore'] for n in allowed)
 sync=ROOT/'.tools/report-sync';(sync/'higher_scattering_report_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 code=f'''import subprocess,tarfile,sys
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()=={a.commit!r}
names={sorted(allowed)!r}
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz') as archive:
 for name in names:archive.add(name,arcname=name,recursive=False)
'''
 proc=subprocess.Popen(SSH+[command(code)],stdout=subprocess.PIPE);seen=set();total=0
 try:
  with tarfile.open(fileobj=proc.stdout,mode='r|gz') as archive:
   for member in archive:
    name=member.name;assert member.isfile() and name in allowed and name not in seen and '..' not in Path(name).parts
    total+=member.size;assert member.size<28*1024**2 and total<64*1024**2
    data=archive.extractfile(member).read();digest=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert digest==allowed[name]['oid'],name
    dest=ROOT/name;dest.parent.mkdir(parents=True,exist_ok=True);tmp=dest.with_name(dest.name+'.report-sync-tmp');tmp.write_bytes(data);tmp.chmod(0o755 if allowed[name]['mode']=='100755' else 0o644);tmp.replace(dest);seen.add(name)
  assert proc.wait(timeout=180)==0
 finally:
  proc.stdout.close()
  if proc.poll() is None:proc.kill();proc.wait()
 assert seen==set(allowed)
 for name,entry in allowed.items():
  data=(ROOT/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==entry['oid']
 size=int(subprocess.check_output(['du','-sk',str(ROOT)]).split()[0])*1024
 result=dict(complete=True,commit=a.commit,verified_files=len(seen),local_report_files_match_published_blobs=True,
  pdf_sha256={n:hashlib.sha256((ROOT/'report'/f'{n}.pdf').read_bytes()).hexdigest() for n in ['report','notes']},local_project_bytes=size,scientific_data_downloaded=False)
 (sync/'higher_scattering_sync_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
