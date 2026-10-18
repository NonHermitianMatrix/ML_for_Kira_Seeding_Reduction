"""Bound symmetry arrays by the existing declared-sector domain."""
from s00_common import *
import difflib,shlex,subprocess
from concurrent.futures import ThreadPoolExecutor
BUILD=ROOT/'.tools/kira-build';BIN=ROOT/'.tools/kira-sector-storage'
HELPER='''
// The restricted initializer only creates relations in declared subsectors.
// Every such sector is at most the largest declared sector. Keep the native
// allocation unless the same restriction is explicitly active.
static std::size_t project_sector_capacity(const Integral_F& f) {
  if (std::getenv("KIRA_BOUNDED_SECTOR_ARRAYS") &&
      std::getenv("KIRA_RESTRICT_SECTOR_INIT") &&
      !f.topLevelSectors.empty() && f.cutProps.empty() && f.symbolicIBP.empty()) {
    return static_cast<std::size_t>(*std::max_element(
        f.topLevelSectors.begin(), f.topLevelSectors.end())) + 1;
  }
  return (std::size_t(1) << f.jule) + 1;
}
'''
def update_source(p,s):
 if not p.exists() or p.read_text()!=s:p.write_text(s)
def main():
 assert os.environ.get('JOB_ID')
 BIN.mkdir(exist_ok=True);commands=json.loads((BUILD/'compile_commands.json').read_text())
 pool=ThreadPoolExecutor(max_workers=min(2,int(os.environ.get('NSLOTS','1'))));pending=[]
 original=ROOT/'.tools/kira-source/src/kira/ReadYamlFiles.cpp';s=original.read_text();anchor='void Kira::read_config()';pos=s.index(anchor)
 # Insert the helper before all method definitions, after includes and namespaces.
 pos=s.index('Kira::');pos=s.rfind('\n',0,pos)+1;s=s[:pos]+HELPER+s[pos:]
 for name in ['symVecReverse','symVec','relVec']:
  old='(*iT).second.'+name+' = new SYM[(1 << (*iT).second.jule) + 1];'
  assert s.count(old)==1;s=s.replace(old,'(*iT).second.'+name+' = new SYM[project_sector_capacity((*iT).second)];')
 old='sec < (1u << integralfamily.jule)';assert old in s;s=s.replace(old,'sec < project_sector_capacity(integralfamily)')
 update_source(BIN/'ReadYamlFiles.cpp',s)
 write(HERE/'integration/ReadYamlFiles_source.json',dict(original_sha256=inputs.sha(original),patched_sha256=inputs.sha(BIN/'ReadYamlFiles.cpp')))
 (HERE/'integration/sector_storage.patch').write_text(''.join(difflib.unified_diff(original.read_text().splitlines(True),s.splitlines(True),fromfile='native/ReadYamlFiles.cpp',tofile='bounded/ReadYamlFiles.cpp')))
 original=ROOT/'.tools/kira-parametric/trivial_sym.cpp';s=original.read_text();pos=s.index('Kira::');pos=s.rfind('\n',0,pos)+1;s=s[:pos]+HELPER+s[pos:]
 old='(1u << integralfamily.jule) + 1';assert s.count(old)==3;s=s.replace(old,'project_sector_capacity(integralfamily)')
 old='      symVec[sector].push_back(halloB);';assert s.count(old)==1
 s=s.replace(old,'      if (sector < 0 || static_cast<std::size_t>(sector) >= project_sector_capacity(integralfamily)) throw ExceptionInternal("Sector exceeds allocated symmetry domain");\n'+old)
 update_source(BIN/'trivial_sym.cpp',s)
 with (HERE/'integration/sector_storage.patch').open('a') as out:out.write(''.join(difflib.unified_diff(original.read_text().splitlines(True),s.splitlines(True),fromfile='parametric/trivial_sym.cpp',tofile='bounded/trivial_sym.cpp')))
 original=ROOT/'.tools/kira-source/src/pyred/integrals.cpp';weights=original.read_text()
 old='  for (uint32_t s = 0; s != (1u << np); ++s) {'
 assert weights.count(old)==1
 new="""  const bool bounded_sectors = std::getenv("KIRA_BOUNDED_SECTOR_ARRAYS")
      && std::getenv("KIRA_RESTRICT_SECTOR_INIT") && np<=31 && topsectors.size()==1
      && (topsectors[0] & (topsectors[0]+1))==0;
  const uint32_t sector_limit = bounded_sectors ? topsectors[0]+1 : (1u<<np);
  for (uint32_t original_sector = 0; original_sector != sector_limit; ++original_sector) {
    const uint32_t s = bounded_sectors ? permutation.permute_sector(original_sector) : original_sector;"""
 weights=weights.replace(old,new)
 old="""  for (uint32_t s = 0; s != (1u << m_np); ++s) {
    // m_minlines: minimal number of lines in any non-trivial sector.
    auto lines = count_set_bits(s);
    if (lines < m_minlines &&
        m_trivialsectors.find(s) == m_trivialsectors.end()) {
      m_minlines = lines;
    }
  }"""
 assert weights.count(old)==1
 new="""  if (m_np<=31 && std::getenv("KIRA_BOUNDED_SECTOR_ARRAYS")) {
    // There are binomial(np,k) sectors with k lines. A nontrivial one
    // exists exactly when fewer than this many are in the trivial set.
    std::array<uint64_t,33> trivial_by_lines{};
    for (const auto s: m_trivialsectors) {
      if (uint64_t(s) < (uint64_t(1)<<m_np)) ++trivial_by_lines[count_set_bits(s)];
    }
    uint64_t combinations=1;
    for (uint32_t k=0;k<=m_np;++k) {
      if (trivial_by_lines[k]<combinations) { m_minlines=k; break; }
      if (k<m_np) combinations=combinations*(m_np-k)/(k+1);
    }
  } else {
"""+old+"""
  }"""
 weights=weights.replace(old,new);update_source(BIN/'integrals.cpp',weights)
 (HERE/'integration/sector_weights.patch').write_text(''.join(difflib.unified_diff(original.read_text().splitlines(True),weights.splitlines(True),fromfile='native/integrals.cpp',tofile='bounded/integrals.cpp')))
 # Raw IBP templates contain zero-coefficient terms outside the seeded sector.
 # Prove that these terms vanish before requesting an omitted sector weight.
 original=ROOT/'.tools/kira-early-generation/relations.cpp';relations=original.read_text()
 relations=relations.replace('#include <algorithm>', '#include <algorithm>\n#include <ginac/ginac.h>')
 old="""      auto weight = ic.first.zip(seed).to_weight();
      auto coeff = sow_coeff(ic.second, s_seed);"""
 new="""      const auto integral = ic.first.zip(seed);
      auto coeff = sow_coeff(ic.second, s_seed);
      if (std::getenv("KIRA_BOUNDED_SECTOR_ARRAYS")) {
        uint32_t sector=0;
        for (std::size_t k=0;k<integral.m_powers.size();++k)
          if (integral.m_powers[k]>0) sector |= uint32_t(1)<<k;
        if (sector >= Integral::s_sector_weight.at(integral.m_topoid).size()) {
          static thread_local std::unordered_set<std::string> proven_zero;
          if (proven_zero.find(coeff)!=proven_zero.end()) continue;
          GiNaC::parser exact_parser;
          if (exact_parser(coeff).normal().is_zero()) {
            if (proven_zero.size()<4096 && coeff.size()<=1024) proven_zero.insert(coeff);
            continue;
          }
          throw input_error("Nonzero IBP term outside bounded sector domain: "+coeff);
        }
      }
      auto weight = integral.to_weight();"""
 assert relations.count(old)==1;relations=relations.replace(old,new);update_source(BIN/'relations.cpp',relations)
 (HERE/'integration/zero_terms.patch').write_text(''.join(difflib.unified_diff(original.read_text().splitlines(True),relations.splitlines(True),fromfile='early/relations.cpp',tofile='bounded/relations.cpp')))
 link=read(ROOT/'ML_model_adaptive_reduction/parametric_preparation/integration/build.json')['link'];objects=[];newlink=[];compile_records=[]
 replacements={'ReadYamlFiles.cpp':BIN/'ReadYamlFiles.cpp','trivial_sym.cpp':BIN/'trivial_sym.cpp','kira.cpp':ROOT/'.tools/kira-parametric/kira.cpp','connect2kira.cpp':ROOT/'.tools/kira-fast-expression/connect2kira_fast.cpp','dataBase.cpp':ROOT/'.tools/kira-runtime-db/dataBase.cpp','reduction.cpp':ROOT/'.tools/kira-parallel-inference/reduction_cost.cpp'}
 for a in link:
  if not a.endswith('.o'):newlink.append(a);continue
  name=Path(a).name
  if name.endswith('.cpp.o'):name=name[:-2]
  else:name=name[:-2]+'.cpp'
  original_name={'connect2kira_fast.cpp':'connect2kira.cpp','reduction_cost.cpp':'reduction.cpp'}.get(name,name)
  src=replacements.get(original_name,ROOT/'.tools/kira-source/src/kira'/original_name)
  assert src.exists(),str(src)
  record=next(c for c in commands if c['file'].endswith('/'+original_name))
  cmd=shlex.split(record['command']);obj=BIN/(name+'.o')
  for flag,value in [('-o',obj),('-MF',BIN/(name+'.d')),('-MQ',obj)]:cmd[cmd.index(flag)+1]=str(value)
  cmd[-1]=str(src)
  if not obj.exists() or obj.stat().st_mtime<src.stat().st_mtime:
   print('COMPILE',original_name,flush=True);pending.append(pool.submit(subprocess.run,cmd,cwd=BUILD,check=True))
  objects.append(obj);newlink.append(str(obj));compile_records.append(cmd)
  assert sum(p.stat().st_blocks*512 for folder in ['kira-sector-storage','kira-sector-wide'] for p in (ROOT/'.tools'/folder).glob('*') if p.is_file())<40*1024**2
 # Rebuild the original pyRed units and their bundled C/C++ dependencies. The old archive used thin members
 # that were removed during earlier temporary-build cleanup.
 pyobjects=[]
 for record in commands:
  if not record['output'].startswith('src/pyred/'):continue
  name=Path(record['file']).name
  src=BIN/'relations.cpp' if name=='relations.cpp' else (ROOT/'.tools/kira-early-generation'/name if name=='interface.cpp' else (BIN/'integrals.cpp' if name=='integrals.cpp' else (BUILD/record['file']).resolve()))
  obj=BIN/(name+'.o');cmd=shlex.split(record['command'])
  for flag,value in [('-o',obj),('-MF',BIN/(name+'.d')),('-MQ',obj)]:cmd[cmd.index(flag)+1]=str(value)
  cmd[-1]=str(src)
  if not obj.exists() or obj.stat().st_mtime<src.stat().st_mtime:
   print('COMPILE pyRed',name,flush=True);pending.append(pool.submit(subprocess.run,cmd,cwd=BUILD,check=True))
  objects.append(obj);pyobjects.append(str(obj));compile_records.append(cmd)
  assert sum(p.stat().st_blocks*512 for folder in ['kira-sector-storage','kira-sector-wide'] for p in (ROOT/'.tools'/folder).glob('*') if p.is_file())<40*1024**2
 for future in pending:future.result()
 pool.shutdown()
 assert sum(p.stat().st_blocks*512 for folder in ['kira-sector-storage','kira-sector-wide'] for p in (ROOT/'.tools'/folder).glob('*') if p.is_file())<40*1024**2
 j=newlink.index(str(ROOT/'.tools/kira-early-generation/libpyred_eq.a'));newlink[j:j+1]=pyobjects
 newlink[newlink.index('-o')+1]=str(BIN/'kira');subprocess.run(newlink,cwd=BUILD,check=True)
 write(HERE/'integration/build.json',dict(complete=True,binary_sha256=inputs.sha(BIN/'kira'),compile=compile_records,link=newlink,scope='Cold single-family reductions with declared sector initialization and no cuts or symbolic IBP. Native allocation remains available with the new flag absent.'))
 # Keep bounded objects until the complete test grid passes. The finish step removes them.
 write(HERE/'integration/build_objects.json',dict(objects=[str(p.relative_to(ROOT)) for p in objects]))
 print('BUILD_COMPLETE',flush=True)
if __name__=='__main__':main()
