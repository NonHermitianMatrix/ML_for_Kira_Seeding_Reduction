"""Fetch the C++ header matching the cluster's GMP 6.2.1 arithmetic library."""
from s00_reconstruction_common import *
import urllib.request,tarfile

def main():
 check_storage();TOOLS.mkdir(exist_ok=True);(TOOLS/'include').mkdir(exist_ok=True)
 archive=STAGE/'gmp-6.2.1.tar.xz'
 url='https://gmplib.org/download/gmp/gmp-6.2.1.tar.xz'
 with urllib.request.urlopen(url,timeout=60) as response,archive.open('wb') as out:
  n=0
  while True:
   block=response.read(65536)
   if not block:break
   n+=len(block);assert n<4*1024**2;out.write(block)
 with tarfile.open(archive,'r:xz') as tf:
  selected={}
  for name in ['gmpxx.h','COPYING','COPYING.LESSERv3']:
   member=tf.getmember('gmp-6.2.1/'+name)
   assert member.isfile() and member.size<512*1024
   raw=tf.extractfile(member).read();target=TOOLS/'include/gmpxx.h' if name=='gmpxx.h' else TOOLS/('GMP_'+name)
   target.write_bytes(raw);selected[name]=sha(target)
 write(HERE/'gmp_cpp_dependency.json',dict(url=url,archive_sha256=sha(archive),selected_files_sha256=selected,system_stream_library='/usr/lib64/libgmpxx.so',arithmetic_library='/u/local/apps/gmp/6.2.1/lib/libgmp.so'))
 archive.unlink();print('Matching GMP C++ header installed',flush=True)
if __name__=='__main__':main()
