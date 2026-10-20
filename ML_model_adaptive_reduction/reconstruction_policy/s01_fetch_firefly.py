"""Fetch the upstream compatible FireFly source with explicit storage bounds."""
from s00_reconstruction_common import *
import tarfile,urllib.request,shutil

def main():
 check_storage()
 STAGE.mkdir(parents=True,exist_ok=True);manifest=HERE/'dependency.json'
 pinned=read(manifest) if manifest.exists() else None
 if pinned and (STAGE/'firefly/README.md').exists():
  print(json.dumps(pinned),flush=True);return
 repo='https://gitlab.com/firefly-library/firefly.git'
 revision=pinned['revision'] if pinned else subprocess.check_output(['git','ls-remote',repo,'refs/heads/kira-2'],text=True,timeout=60).split()[0]
 assert len(revision)==40 and all(c in '0123456789abcdef' for c in revision)
 url=f'https://gitlab.com/firefly-library/firefly/-/archive/{revision}/firefly-{revision}.tar.gz'
 archive=STAGE/'source.tar.gz';total=0
 with urllib.request.urlopen(url,timeout=45) as source,archive.open('wb') as out:
  while True:
   chunk=source.read(1024**2)
   if not chunk:break
   total+=len(chunk);assert total<16*1024**2;out.write(chunk)
 digest=sha(archive)
 if pinned:assert digest==pinned['archive_sha256']
 dest=STAGE/'firefly';dest.mkdir(exist_ok=True)
 with tarfile.open(archive,'r:gz') as tf:
  members=tf.getmembers();assert sum(m.size for m in members)<40*1024**2
  for member in members:
   parts=Path(member.name).parts;assert len(parts)>=1 and '..' not in parts and not Path(member.name).is_absolute()
   if len(parts)==1:continue
   q=dest.joinpath(*parts[1:])
   if member.isdir():q.mkdir(parents=True,exist_ok=True)
   elif member.isfile():
    q.parent.mkdir(parents=True,exist_ok=True)
    with tf.extractfile(member) as src,q.open('wb') as out:shutil.copyfileobj(src,out)
   else:raise ValueError('Unexpected archive link or device: '+member.name)
 archive.unlink();r=dict(repository=repo,revision=revision,url=url,archive_sha256=digest,source_allocated_bytes=allocated(dest))
 write(manifest,r);check_storage();print(json.dumps(r),flush=True)
if __name__=='__main__':main()
