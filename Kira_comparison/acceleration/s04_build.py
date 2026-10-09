"""Compile the seed gate separately and link unchanged Kira objects."""
import hashlib,json,pathlib,shlex,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BUILD=ROOT/".tools/kira-build";OUT=ROOT/".tools/kira-acceleration";OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=ROOT/".tools/kira-source/src/pyred/relations.cpp";t=source.read_text()
 t=t.replace('#include "relations.h"','#include "relations.h"\n#include "'+str(HERE/"s03_seed_filter.h")+'"',1)
 needle='    const std::vector<pow_type>& seed) const {\n  std::vector<eqdata> numibps;'
 assert needle in t
 t=t.replace(needle,'    const std::vector<pow_type>& seed) const {\n  if (!kira_accel::seed_allowed(m_topoid, seed)) return {};\n  std::vector<eqdata> numibps;',1)
 dest=OUT/"relations_accel.cpp";dest.write_text(t)
 compile=shlex.split(next(c["command"] for c in json.loads((BUILD/"compile_commands.json").read_text()) if c["file"].endswith("/relations.cpp")))
 obj=OUT/"relations_accel.o"
 for flag,value in [("-o",obj),("-MF",OUT/"relations_accel.d"),("-MQ",obj)]:compile[compile.index(flag)+1]=str(value)
 compile[-1]=str(dest)
 subprocess.run(compile,cwd=BUILD,check=True)
 archive=BUILD/"src/pyred/libpyred.a"
 members=subprocess.check_output(["ar","t",str(archive)],cwd=ROOT,text=True).splitlines()
 objects=[str(obj) if name.endswith("/relations.cpp.o") else str((ROOT/name).resolve()) for name in members]
 new=OUT/"libpyred_accel.a"
 if new.exists():new.unlink()
 subprocess.run(["ar","crsT",str(new)]+objects,check=True)
 ninja=ROOT/".tools/build-python/bin/ninja"
 link=shlex.split(subprocess.check_output([str(ninja),"-C",str(BUILD),"-t","commands","src/kira/kira"],text=True).splitlines()[-1])
 link[link.index("-o")+1]=str(OUT/"kira")
 link=[str(new) if x=="src/pyred/libpyred.a" else x for x in link]
 subprocess.run(link,cwd=BUILD,check=True)
 (HERE/"build.json").write_text(json.dumps(dict(original_sha256=sha(source),modified_sha256=sha(dest),header_sha256=sha(HERE/"s03_seed_filter.h"),binary_sha256=sha(OUT/"kira"),compile=compile,link=link),indent=2)+"\n")
 print("Individual-seed gate compiled",flush=True)
if __name__=="__main__":main()
