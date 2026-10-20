"""Build a separate FireFly-enabled copy of the published exact Kira sources."""
from s00_reconstruction_common import *
import shlex,shutil,signal
from concurrent.futures import ThreadPoolExecutor

def command(cmd,cwd,name,seconds=1200):
 log=STAGE/(name+'.log');start=time.monotonic()
 with log.open('wb') as out:
  p=subprocess.Popen(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
  try:
   while p.poll() is None:
    check_storage()
    if time.monotonic()-start>seconds:raise TimeoutError(name)
    time.sleep(1)
   if p.returncode:
    raise RuntimeError(name+': '+log.read_text(errors='replace')[-5000:])
  finally:
   if p.poll() is None:
    os.killpg(p.pid,signal.SIGKILL);p.wait()
 print(name,'completed',round(time.monotonic()-start,2),flush=True)

def main():
 assert os.environ.get('JOB_ID');check_storage()
 dependency=read(HERE/'dependency.json');source=STAGE/'firefly';ffbuild=STAGE/'firefly-build'
 ffbuild.mkdir(exist_ok=True);TOOLS.mkdir(exist_ok=True)
 temporary=STAGE/'compiler-temp';temporary.mkdir(exist_ok=True);os.environ['TMPDIR']=str(temporary)
 gmp=Path(os.environ['GMP_DIR']);flint=Path(os.environ['FLINT_DIR'])
 assert (gmp/'lib/libgmp.so').exists() and (flint/'lib/libflint.so').exists()
 assert (TOOLS/'include/gmpxx.h').exists() and Path('/usr/lib64/libgmpxx.so').exists()
 command(['cmake','-S',str(source),'-B',str(ffbuild),'-UGMPXX_H_INCLUDE_DIRS','-DWITH_FLINT=true','-DWITH_MPI=false','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG -g0 -D_GLIBCXX_USE_CXX11_ABI=0','-DDISABLE_INSTALL=true','-DGMP_INCLUDE_DIRS='+str(TOOLS/'include')+';'+str(gmp/'include'),'-DGMP_LIBRARIES='+str(gmp/'lib/libgmp.so'),'-DFLINT_INCLUDE_DIR='+str(flint/'include'),'-DFLINT_LIBRARY='+str(flint/'lib/libflint.so')],ROOT,'configure-firefly',120)
 command(['cmake','--build',str(ffbuild),'--target','FireFly_static','--parallel','2'],ROOT,'build-firefly',1800)
 inc=TOOLS/'include';(inc/'firefly').mkdir(parents=True,exist_ok=True);(inc/'pyred').mkdir(exist_ok=True)
 for f in (source/'source/include/firefly').iterdir():
  if f.suffix in ['.hpp','.h']:shutil.copyfile(f,inc/'firefly'/f.name)
 for name in ['config.hpp','version.hpp']:shutil.copyfile(ffbuild/'include/firefly'/name,inc/'firefly'/name)
 lib=TOOLS/'lib';lib.mkdir(exist_ok=True);shutil.copyfile(ffbuild/'libfirefly.a',lib/'libfirefly.a')
 config=(ROOT/'.tools/kira-sector-wide/include/config.h').read_text();assert '#undef KIRAFIREFLY' in config
 config=config.replace('#undef KIRAFIREFLY','#define KIRAFIREFLY 1')
 for f in [inc/'config.h',inc/'pyred/config.h']:f.write_text(config)
 record=read(ROOT/'ML_model_adaptive_reduction/portfolio_policy/wide_integration/build.json')
 objects=STAGE/'objects';objects.mkdir(exist_ok=True);commands=[];mapping={};source_checks={}
 extra=['-I'+str(inc),'-I'+str(flint/'include'),'-I'+str(gmp/'include')]
 for original in record['compile']:
  cmd=list(original);old=cmd[cmd.index('-o')+1];obj=objects/Path(old).name
  for flag,value in [('-o',obj),('-MF',obj.with_suffix('.d')),('-MQ',obj)]:
   cmd[cmd.index(flag)+1]=str(value)
  cmd[1:1]=extra;mapping[old]=str(obj);commands.append(cmd);source_checks[cmd[-1]]=sha(cmd[-1])
 base=next(cmd for cmd in commands if Path(cmd[-1]).name=='kira.cpp')
 for name in ['reductionFF.cpp','mpi_work.cpp']:
  cmd=list(base);obj=objects/(name+'.o')
  for flag,value in [('-o',obj),('-MF',obj.with_suffix('.d')),('-MQ',obj)]:
   cmd[cmd.index(flag)+1]=str(value)
  cmd[-1]=str(ROOT/'.tools/kira-source/src/kira'/name);commands.append(cmd);source_checks[cmd[-1]]=sha(cmd[-1])
 build=ROOT/'.tools/kira-build'
 with ThreadPoolExecutor(max_workers=2) as pool:
  jobs=[pool.submit(command,cmd,build,'compile-'+Path(cmd[-1]).name,1200) for cmd in commands]
  for job in jobs:job.result()
 link=[mapping.get(x,x) for x in record['link']];link[link.index('-o')+1]=str(TOOLS/'kira')
 link.extend([str(objects/'reductionFF.cpp.o'),str(objects/'mpi_work.cpp.o'),str(lib/'libfirefly.a'),'-L'+str(flint/'lib'),'-L'+str(gmp/'lib'),'-Wl,-rpath,'+str(flint/'lib'),'-Wl,-rpath,'+str(gmp/'lib'),'-lflint','-lgmpxx','-lgmp','-lmpfr','-lz','-lpthread'])
 command(link,build,'link-kira',180)
 version=subprocess.check_output([str(TOOLS/'kira'),'--version'],text=True,timeout=10)
 assert 'without FireFly' not in version and 'FireFly' in version,version
 write(HERE/'build.json',dict(complete=True,dependency=dependency,binary_sha256=sha(TOOLS/'kira'),preceding_binary_sha256=sha(ROOT/'.tools/kira-sector-wide/kira'),source_sha256=source_checks,compile=commands,link=link,configuration=config,version=version,gmp_cpp_header_sha256=sha(TOOLS/'include/gmpxx.h'),gmp_cpp_library='/usr/lib64/libgmpxx.so',modules=['gcc/9.5.0','python/3.9.6','gmp/6.2.1','flint/2.8.0','cmake/3.30.0'],build_allocated_bytes=check_storage()))
 for f in source.glob('*COPY*'):shutil.copyfile(f,TOOLS/f.name)
 (TOOLS/'README.md').write_text('# Reconstruction backend\n\nThis separate Kira 3.1 executable retains the published exact source changes and adds FireFly 2.0.3.\nRead ML_model_adaptive_reduction/reconstruction_policy/build.json for sources and build commands.\nThe current published solver remains in .tools/kira-sector-wide.\n')
 assert allocated(TOOLS)<RETAINED_TOOLS_LIMIT,allocated(TOOLS)
 # These are new temporary compilation objects. Preserve their commands and source checks above.
 shutil.rmtree(objects);shutil.rmtree(ffbuild)
 print('BUILD COMPLETE',version.strip(),'retained_tools_bytes',allocated(TOOLS),flush=True)
if __name__=='__main__':main()
