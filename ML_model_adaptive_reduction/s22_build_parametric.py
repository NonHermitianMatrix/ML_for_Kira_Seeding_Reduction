"""Project unused parameters before constructing the sector polynomials."""
import difflib, hashlib, json, shlex, subprocess, shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
OUT=HERE/'parametric_preparation'; BUILD=ROOT/'.tools/kira-build'
BIN=ROOT/'.tools/kira-parametric'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    BIN.mkdir(exist_ok=True);(OUT/'integration').mkdir(parents=True,exist_ok=True)
    original=ROOT/'.tools/kira-adaptive/trivial_sym.cpp';source=original.read_text()
    before='''  ex schwinger;
  for (uint32_t i = 0; i < integralfamily.jule; i++) {
    schwinger += -feynman[i] * integralfamily.props[i].expand();
  }'''
    after='''  // All later polynomial uses restrict to a declared sector. Polynomial
  // substitution commutes with determinants, adjugates and coefficient sums.
  // Keep the full propagator list for IBP and numerator transformations.
  const bool early_projection = std::getenv("KIRA_PROJECT_PARAMETRIC")
      && std::getenv("KIRA_RESTRICT_SECTOR_INIT")
      && !integralfamily.topLevelSectors.empty()
      && integralfamily.cutProps.empty() && integralfamily.symbolicIBP.empty();
  uint32_t parametric_domain = (1u << integralfamily.jule)-1;
  if (early_projection) {
    parametric_domain=0;
    for (uint32_t top: integralfamily.topLevelSectors) parametric_domain |= top;
  }
  ex schwinger;
  for (uint32_t i = 0; i < integralfamily.jule; i++) {
    if (parametric_domain & (1u<<i))
      schwinger += -feynman[i] * integralfamily.props[i].expand();
  }
  logger << "Parametric domain: " << parametric_domain
         << "; early projection: " << early_projection << "\\n";'''
    assert source.count(before)==1;source=source.replace(before,after)
    anchor='  integralfamily.G = expand(integralfamily.Gsym.subs(invariants4symRev));'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+'''
  if (const char* metric_path=std::getenv("KIRA_STAGE_METRICS")) {
    std::ofstream metric(metric_path,std::ios::app);
    metric << "{\\"stage\\":\\"parametric_construction\\",\\"seconds\\":"
           << clock.eval_time() << ",\\"early_projection\\":"
           << (early_projection ? "true" : "false") << "}\\n";
  }
''')
    src=BIN/'trivial_sym.cpp';src.write_text(source)
    (OUT/'integration/early_projection.patch').write_text(''.join(difflib.unified_diff(original.read_text().splitlines(True),source.splitlines(True),fromfile='adaptive/trivial_sym.cpp',tofile='parametric/trivial_sym.cpp')))
    commands=json.loads((BUILD/'compile_commands.json').read_text())
    cmd=shlex.split(next(c['command'] for c in commands if c['file'].endswith('/trivial_sym.cpp')))
    obj=BIN/'trivial_sym.o'
    for flag,value in [('-o',obj),('-MF',BIN/'trivial_sym.d'),('-MQ',obj)]:cmd[cmd.index(flag)+1]=str(value)
    cmd[-1]=str(src);subprocess.run(cmd,cwd=BUILD,check=True)
    # The first retrieval checks whether extra masters remain. If the selected
    # source list stays identical, the final pass can consume the same exact rows.
    original_kira=ROOT/'.tools/kira-adaptive/kira.cpp';kira=original_kira.read_text()
    before='''  sys.generate_retrieve(std::move(selection.first), treateq2, treatcoeff);
  treateq2.finalize();'''
    after='''  bool replay_ready = std::getenv("KIRA_REUSE_SELECTED_EQUATIONS") != nullptr
      && selection.first.size()<=4096;
  const std::vector<std::size_t> replay_ids = replay_ready ? selection.first : std::vector<std::size_t>();
  std::size_t replay_limit=4*1024*1024;
  if (const char* limit=std::getenv("KIRA_SELECTED_CACHE_BYTES"))
    replay_limit=std::min<std::size_t>(replay_limit,std::strtoull(limit,nullptr,10));
  std::vector<eqdata> replay_rows;
  if (replay_ready) replay_rows.reserve(4096);
  std::size_t replay_bytes=0;
  std::mutex replay_mutex;
  const std::function<void(eqdata&&)> collect_selected = [&](eqdata&& row) {
    std::lock_guard<std::mutex> lock(replay_mutex);
    if (replay_ready) {
      std::size_t bytes=sizeof(eqdata)+row.size()*sizeof(eqdata::value_type);
      for (const auto& term: row) bytes += term.second.size()+1;
      if (replay_rows.size()>=4096 || bytes>replay_limit-replay_bytes) {
        replay_ready=false;
        std::vector<eqdata>().swap(replay_rows);
      } else {
        replay_rows.push_back(row);
        replay_bytes += bytes;
      }
    }
    treateq2(std::move(row));
  };
  sys.generate_retrieve(std::move(selection.first), collect_selected, treatcoeff);
  treateq2.finalize();'''
    assert kira.count(before)==1;kira=kira.replace(before,after)
    before='''    sys.generate_retrieve(std::move(selection.first), treateq, treatcoeff);
    treateq.finalize();'''
    after='''    if (replay_ready && selection.first==replay_ids) {
      Clock replay_clock;
      for (const auto& saved: replay_rows) {
        eqdata row(saved);
        treateq(std::move(row));
      }
      if (const char* path=std::getenv("KIRA_STAGE_METRICS")) {
        std::ofstream metric(path,std::ios::app);
        metric << "{\\"stage\\":\\"selected_equation_replay\\",\\"seconds\\":"
               << replay_clock.eval_time() << ",\\"rows\\":" << replay_rows.size()
               << ",\\"accounted_bytes\\":" << replay_bytes << "}\\n";
      }
    } else {
      sys.generate_retrieve(std::move(selection.first), treateq, treatcoeff);
    }
    treateq.finalize();'''
    assert kira.count(before)==1;kira=kira.replace(before,after)
    src_kira=BIN/'kira.cpp';src_kira.write_text(kira)
    (OUT/'integration/selected_equations.patch').write_text(''.join(difflib.unified_diff(original_kira.read_text().splitlines(True),kira.splitlines(True),fromfile='adaptive/kira.cpp',tofile='parametric/kira.cpp')))
    cmd_kira=shlex.split(next(c['command'] for c in commands if c['file'].endswith('/kira.cpp')))
    obj_kira=BIN/'kira.o'
    for flag,value in [('-o',obj_kira),('-MF',BIN/'kira.d'),('-MQ',obj_kira)]:cmd_kira[cmd_kira.index(flag)+1]=str(value)
    cmd_kira[-1]=str(src_kira);subprocess.run(cmd_kira,cwd=BUILD,check=True)
    link=json.loads((HERE/'integration/build.json').read_text())['link']
    link=[str(obj) if a.endswith('/trivial_sym.o') else a for a in link]
    link=[str(obj_kira) if a.endswith('/kira.o') else a for a in link]
    if (BIN/'kira').exists() and not (BIN/'kira.early').exists():
        shutil.copyfile(BIN/'kira',BIN/'kira.early')
        shutil.copyfile(OUT/'integration/build.json',OUT/'integration/early_build.json')
    link[link.index('-o')+1]=str(BIN/'kira');subprocess.run(link,cwd=BUILD,check=True)
    runner=(HERE/'s01_native_runner.py').read_text()
    runner=runner.replace('[".tools/kira-adaptive/kira",','[".tools/kira-parametric/kira",".tools/kira-adaptive/kira",')
    (HERE/'s23_parametric_runner.py').write_text(runner)
    result=dict(binary_sha256=sha(BIN/'kira'),source_sha256=sha(original),compile=cmd,kira_compile=cmd_kira,link=link,
        scope='Project sector polynomials; reuse exact selected equations only within one system when its ordered selection is unchanged. No cross-request coefficient cache.')
    (OUT/'integration/build.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PARAMETRIC_BUILD_COMPLETE',flush=True)
if __name__=='__main__':main()
