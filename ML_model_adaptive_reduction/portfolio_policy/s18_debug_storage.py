from s00_common import *
gen=module('debug_cases',ROOT/'Kira_comparison/coverage_study/s00_cases.py')
c=gen.case('vacuum_one_mass',3,False,1132)
original=rt.native.subprocess.Popen
def patched(args,*a,**kw):
 if isinstance(args,list) and str(args[0]).endswith('/kira-sector-storage/kira'):
  args=['gdb','-batch','-ex','run','-ex','bt','--args']+args
 return original(args,*a,**kw)
rt.native.subprocess.Popen=patched
with rt.environment():
 os.environ.update(KIRA_RUNTIME_BINARY=str(ROOT/'.tools/kira-sector-storage/kira'),KIRA_BOUNDED_SECTOR_ARRAYS='1')
 r=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=60,margin=0,archive=False,records=False,scratch_cap=32*1024**2,bounds=inputs.bounds(c,'expanded'),threads=1)
print(r.get('log','')[-14000:],flush=True)
