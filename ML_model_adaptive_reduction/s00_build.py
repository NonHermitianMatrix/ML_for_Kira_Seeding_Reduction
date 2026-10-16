"""Build an exact file-index improvement without changing the original binary."""
import difflib, hashlib, json, shlex, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
OUT=ROOT/'.tools/kira-adaptive'; BUILD=ROOT/'.tools/kira-build'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    OUT.mkdir(exist_ok=True)
    original=ROOT/'.tools/kira-source/src/kira/kira.cpp'
    source=original.read_text()
    helper=r'''
#include <dirent.h>
#include <cstdlib>
// Enumerate sector files in the same increasing order as the original scan.
// An unavailable directory falls back to the original exhaustive loop.
static bool kira_existing_sectors(const std::string& directory,
    const std::string& topology, uint32_t limit, std::vector<uint32_t>& result,
    const std::string& type = "SYSTEM") {
  DIR* dir = opendir(directory.c_str());
  if (!dir) return false;
  const std::string prefix = type + "_" + topology + "_";
  const std::string prefix_x = type + "x_" + topology + "_";
  std::set<uint32_t> sectors;
  while (dirent* entry = readdir(dir)) {
    const std::string name(entry->d_name);
    const bool plain = type=="SYSTEM" && name.compare(0,prefix_x.size(),prefix_x)==0;
    const std::string& start = plain ? prefix_x : prefix;
    if (name.compare(0,start.size(),start)!=0) continue;
    const std::string tail = name.substr(start.size());
    size_t n=0;
    while (n<tail.size() && tail[n]>='0' && tail[n]<='9') ++n;
    if (!n || n>10 || (n>1 && tail[0]=='0')) continue;
    const std::string suffix=tail.substr(n);
    bool valid=plain ? suffix.empty() : suffix==".gz";
    if (!plain && suffix.size()>4 && suffix[0]=='_' &&
        suffix.substr(suffix.size()-3)==".gz") {
      valid=true;
      for (size_t j=1;j<suffix.size()-3;++j)
        if (suffix[j]<'0'||suffix[j]>'9') valid=false;
    }
    if (!valid) continue;
    unsigned long long sector=std::strtoull(tail.substr(0,n).c_str(),nullptr,10);
    if (sector<limit) sectors.insert(static_cast<uint32_t>(sector));
  }
  closedir(dir);
  result.assign(sectors.begin(),sectors.end());
  return true;
}
'''
    anchor='void Kira::complete_triangular(vector<pyred::Weight>& mandatory) {'
    assert source.count(anchor)==1
    source=source.replace(anchor,helper+'\n'+anchor)
    before='''    for (uint32_t sectorNumber = 0; sectorNumber < (1u << integralfamily.jule);
         sectorNumber++) {

      load_triangular(k, sectorNumber, forwardRed, reduce_please,
                      rdy2F);
    }'''
    after='''    std::vector<uint32_t> existing;
    const bool indexed = std::getenv("KIRA_INDEX_SECTOR_FILES") &&
        kira_existing_sectors(outputDir + "/tmp/" + integralfamily.name,
                              collectReductions[k], (1u << integralfamily.jule), existing);
    if (indexed) {
      for (uint32_t sectorNumber : existing)
        load_triangular(k, sectorNumber, forwardRed, reduce_please, rdy2F);
      logger << "Indexed triangular sectors: " << existing.size() << "\\n";
    } else {
      for (uint32_t sectorNumber=0; sectorNumber<(1u << integralfamily.jule); ++sectorNumber)
        load_triangular(k, sectorNumber, forwardRed, reduce_please, rdy2F);
    }'''
    assert source.count(before)==1;source=source.replace(before,after)
    # Both back-substitution passes read VER files in the same sector order.
    start=source.index('int Kira::load_back_substitution(')
    end=source.index('void ConvertResult::get_firefly_flag()',start)
    part=source[start:end]
    anchor='  if (sectorOrdering == 2) {'
    assert part.count(anchor)==1
    part=part.replace(anchor,'''  std::vector<std::vector<uint32_t> > existing(collectReductions.size());
  std::vector<bool> indexed(collectReductions.size(),false);
  for (size_t k=0;k<collectReductions.size();++k) {
    indexed[k]=std::getenv("KIRA_INDEX_SECTOR_FILES") &&
      kira_existing_sectors(outputDir + "/tmp/" + integralfamily.name,
                            collectReductions[k], (1u << integralfamily.jule), existing[k], "VER");
  }
  if (sectorOrdering == 2) {''')
    import re
    pattern=r'for \(size_t sectorNumber = 0;\s*sectorNumber < \(1u << integralfamily.jule\);\s*sectorNumber\+\+\) \{'
    part,count=re.subn(pattern,'''for (size_t sectorTask=0;
             sectorTask < (indexed[k] ? existing[k].size() : (1u << integralfamily.jule));
             ++sectorTask) {
          const uint32_t sectorNumber=indexed[k] ? existing[k][sectorTask] : sectorTask;''',part)
    assert count==4
    source=source[:start]+part+source[end:]
    src=OUT/'kira.cpp';src.write_text(source)
    (HERE/'integration').mkdir(exist_ok=True)
    (HERE/'integration/sector_files.patch').write_text(''.join(difflib.unified_diff(original.read_text().splitlines(True),source.splitlines(True),fromfile='src/kira/kira.cpp',tofile='src/kira/kira.cpp')))
    commands=json.loads((BUILD/'compile_commands.json').read_text())
    cmd=shlex.split(next(c['command'] for c in commands if c['file'].endswith('/kira.cpp')))
    obj=OUT/'kira.o'
    for flag,value in [('-o',obj),('-MF',OUT/'kira.d'),('-MQ',obj)]:cmd[cmd.index(flag)+1]=str(value)
    cmd[-1]=str(src);subprocess.run(cmd,cwd=BUILD,check=True)
    # Terms containing a parameter outside every declared sector never enter
    # the zero-sector tests. Project them out before building those tests.
    trivial_original=(ROOT/'.tools/kira-higher-scattering/trivial_sym.cpp').read_text()
    trivial=trivial_original
    begin=trivial.index('  /*initialize Lee\'s zero sector criterium*/')
    end=trivial.index('  vector<int> seedInit;',begin)
    part=trivial[begin:end]
    part=part.replace('integralfamily.U','criterionU').replace('integralfamily.F','criterionF').replace('integralfamily.G','criterionG')
    projection='''  ex criterionU=integralfamily.U, criterionF=integralfamily.F, criterionG=integralfamily.G;
  if (std::getenv("KIRA_PROJECT_ZERO_CRITERION") && std::getenv("KIRA_RESTRICT_SECTOR_INIT")
      && !integralfamily.topLevelSectors.empty() && integralfamily.cutProps.empty()
      && integralfamily.symbolicIBP.empty()) {
    uint32_t admitted_parameters=0;
    for (uint32_t top: integralfamily.topLevelSectors) admitted_parameters |= top;
    lst projection;
    for (uint32_t i=0;i<integralfamily.jule;++i)
      if (!(admitted_parameters & (1u<<i))) projection.append(feynman[i]==0);
    criterionU=criterionU.subs(projection);
    criterionF=criterionF.subs(projection);
    criterionG=criterionG.subs(projection);
    logger << "Projected zero-sector criterion onto declared parameters.\\n";
  }
'''
    trivial=trivial[:begin]+projection+part+trivial[end:]
    trivial_src=OUT/'trivial_sym.cpp';trivial_src.write_text(trivial)
    (HERE/'integration/zero_criterion.patch').write_text(''.join(difflib.unified_diff(trivial_original.splitlines(True),trivial.splitlines(True),fromfile='restricted/trivial_sym.cpp',tofile='projected/trivial_sym.cpp')))
    trivial_cmd=shlex.split(next(c['command'] for c in commands if c['file'].endswith('/trivial_sym.cpp')))
    trivial_obj=OUT/'trivial_sym.o'
    for flag,value in [('-o',trivial_obj),('-MF',OUT/'trivial_sym.d'),('-MQ',trivial_obj)]:trivial_cmd[trivial_cmd.index(flag)+1]=str(value)
    trivial_cmd[-1]=str(trivial_src);subprocess.run(trivial_cmd,cwd=BUILD,check=True)
    link=json.loads((ROOT/'Kira_comparison/higher_scattering/build.json').read_text())['link']
    link=[str(obj) if a.endswith('/kira.cpp.o') else a for a in link]
    link=[str(trivial_obj) if a.endswith('/trivial_sym.o') else a for a in link]
    binary=OUT/'kira';link[link.index('-o')+1]=str(OUT/'kira.new')
    subprocess.run(link,cwd=BUILD,check=True)
    (OUT/'kira.new').replace(binary)
    runner=(ROOT/'Kira_comparison/higher_scattering/s15_memory_runner.py').read_text()
    runner=runner.replace('parents[2]','parents[1]',1)
    runner=runner.replace('[".tools/kira-higher-scattering/kira",','[".tools/kira-adaptive/kira",".tools/kira-higher-scattering/kira",')
    (HERE/'s01_native_runner.py').write_text(runner)
    (HERE/'integration/build.json').write_text(json.dumps(dict(compile=cmd,trivial_compile=trivial_cmd,link=link,source_sha256=sha(original),binary_sha256=sha(binary),change='Index existing SYSTEM/SYSTEMx/VER files without changing their order. Project the zero-sector criterion onto the declared parameter domain; keep full U and F for other operations.'),indent=2)+'\n')
    print('ADAPTIVE_BUILD_COMPLETE',flush=True)
if __name__=='__main__':main()
