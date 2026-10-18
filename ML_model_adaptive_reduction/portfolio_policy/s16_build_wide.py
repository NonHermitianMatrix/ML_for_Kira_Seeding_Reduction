"""Build the same exact sector implementation with Kira's 128-bit weights."""
from s00_common import *
def main():
 assert os.environ.get('JOB_ID')
 folder=ROOT/'.tools/kira-sector-wide';inc=folder/'include';(inc/'pyred').mkdir(parents=True,exist_ok=True)
 native=ROOT/'.tools/kira-build/src/pyred/config.h';s=native.read_text();assert '#undef WEIGHT128' in s;s=s.replace('#undef WEIGHT128','#define WEIGHT128 1')
 for q in [inc/'config.h',inc/'pyred/config.h']:q.write_text(s)
 code=(HERE/'s06_build_sector_storage.py').read_text().replace("BIN=ROOT/'.tools/kira-sector-storage'","BIN=ROOT/'.tools/kira-sector-wide'").replace("'integration/","'wide_integration/")
 code=code.replace("cmd=shlex.split(record['command'])", "cmd=shlex.split(record['command']);cmd[1:1]=['-I'+str(BIN/'include')]")
 g=dict(__name__='wide_builder',__file__=str(HERE/'s06_build_sector_storage.py'));exec(compile(code,str(HERE/'s06_build_sector_storage.py'),'exec'),g);g['main']()
 p=HERE/'wide_integration/build.json';v=read(p);v.update(weight_width=128,configuration=s,base_configuration_sha256=inputs.sha(native));write(p,v)
 (folder/'README.md').write_text('# Wider integral weights\n\nThis executable uses 128-bit Kira integral weights and the bounded sector implementation. Read portfolio_policy/wide_integration for its build records and exact checks. The 64-bit executable remains separate.\n')
if __name__=='__main__':main()
