"""Build an opt-in test of initialization restricted to the declared sectors."""
import difflib,hashlib,json,shlex,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OUT=ROOT/'.tools/kira-higher-scattering';BUILD=ROOT/'.tools/kira-build'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    OUT.mkdir(exist_ok=True)
    p=ROOT/'.tools/kira-source/src/kira/trivial_sym.cpp';original=p.read_text();s=original
    s='#include <cstdlib>\n'+s
    anchor='  uint32_t loopSIZE = (1 << integralfamily.jule);'
    assert s.count(anchor)==1
    s=s.replace(anchor,'''  uint32_t loopSIZE = (1u << integralfamily.jule);
  std::vector<uint32_t> admitted_sectors;
  const bool restrict_sector_init = std::getenv("KIRA_RESTRICT_SECTOR_INIT")
      && !integralfamily.topLevelSectors.empty()
      && integralfamily.cutProps.empty() && integralfamily.symbolicIBP.empty();
  if (restrict_sector_init) {
    uint32_t largest = 0;
    for (uint32_t top : integralfamily.topLevelSectors) largest = std::max(largest, top);
    for (uint32_t candidate = 0; candidate <= largest; ++candidate) {
      for (uint32_t top : integralfamily.topLevelSectors) {
        if ((candidate & top) == candidate) {
          admitted_sectors.push_back(candidate);
          break;
        }
      }
    }
    loopSIZE = admitted_sectors.size();
    logger << "Declared-sector initialization: " << loopSIZE << " sectors.\\n";
  }''')
    anchor='''    for (uint32_t sector_number = 0; sector_number < (1u << integralfamily.jule);
         sector_number++) {'''
    assert s.count(anchor)==1
    s=s.replace(anchor,'''    for (uint32_t sector_task = 0; sector_task < loopSIZE; ++sector_task) {
      const uint32_t sector_number = restrict_sector_init
          ? admitted_sectors[sector_task] : sector_task;''')
    anchor='load_bar(sector_number + 1, (1u << integralfamily.jule), 50, 100);'
    assert s.count(anchor)==1;s=s.replace(anchor,'load_bar(countLoop, loopSIZE, 50, 100);')
    src=OUT/'trivial_sym.cpp';src.write_text(s)
    (HERE/'sector_initialization.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='src/kira/trivial_sym.cpp',tofile='src/kira/trivial_sym.cpp')))
    commands=json.loads((BUILD/'compile_commands.json').read_text())
    cmd=shlex.split(next(c['command'] for c in commands if c['file'].endswith('/trivial_sym.cpp')))
    obj=OUT/'trivial_sym.o'
    for flag,value in [('-o',obj),('-MF',OUT/'trivial_sym.d'),('-MQ',obj)]:cmd[cmd.index(flag)+1]=str(value)
    cmd[-1]=str(src)
    subprocess.run(cmd,cwd=BUILD,check=True)
    link=json.loads((ROOT/'ML_model_workflow_selection/build.json').read_text())['link_command']
    link=[str(obj) if a.endswith('/trivial_sym.cpp.o') else a for a in link]
    binary=OUT/'kira';link[link.index('-o')+1]=str(binary)
    subprocess.run(link,cwd=BUILD,check=True)
    runner=(ROOT/'ML_model_workflow_selection/thread_policy/s02_native_runner.py').read_text()
    anchor='[".tools/kira-workflow/kira",'
    assert runner.count(anchor)==1
    runner=runner.replace(anchor,'[".tools/kira-higher-scattering/kira",".tools/kira-workflow/kira",')
    (HERE/'s05_native_runner.py').write_text(runner)
    (HERE/'build.json').write_text(json.dumps(dict(source_sha256=sha(p),patched_sha256=sha(src),binary_sha256=sha(binary),
        parent_binary_sha256=sha(ROOT/'.tools/kira-workflow/kira'),compile=cmd,link=link,
        opt_in='KIRA_RESTRICT_SECTOR_INIT',scope='Declared top sectors and all their subsectors. No cuts or symbolic-index identities.'),indent=2)+'\n')
    print('SECTOR_TEST_BUILD_COMPLETE',flush=True)
if __name__=='__main__':main()
