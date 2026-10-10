"""Compile equation filtering and collection without changing prior binaries."""
import os,re,difflib,hashlib,json,pathlib,shlex,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent
BUILD=ROOT/".tools/kira-build";OUT=ROOT/".tools/kira-equation-selection"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(exist_ok=True)
 header=HERE/"integration"/os.getenv("KIRA_EQ_HEADER","s00_equation_policy.h")
 binary=OUT/os.getenv("KIRA_EQ_BINARY_NAME","kira")
 sources={}
 p=ROOT/".tools/kira-acceleration/relations_accel.cpp";t=p.read_text()
 t=t.replace('#include "relations.h"','#include "relations.h"\n#include "'+str(header)+'"',1)
 anchor='    numibps.push_back(std::move(crop));'
 assert t.count(anchor)==1
 t=t.replace(anchor,'    if(!kira_eq::allow(seed,numibps.size(),crop))crop.clear();\n'+anchor)
 if "inline int precheck(" in header.read_text():
  anchor='  for (const auto& ibp_tmpl : m_ibps) {'
  assert t.count(anchor)==1
  t=t.replace(anchor,anchor+'\n    const int eq_cached=kira_eq::precheck(seed,numibps.size());\n    if(eq_cached==0){numibps.emplace_back();continue;}')
  t=t.replace('if(!kira_eq::allow(seed,numibps.size(),crop))','if(eq_cached<0 && !kira_eq::allow(seed,numibps.size(),crop))')
 sources["relations.cpp"]=(p,t)
 p=ROOT/".tools/kira-source/src/pyred/interface.cpp";t=p.read_text()
 t=t.replace('#include "pyred/parser.h"','#include "pyred/parser.h"\n#include "'+str(header)+'"',1)
 for marker in ["#define PYRED_PP_CCS_SYSTEMGENERATERETRIEVE1","#define PYRED_PP_CCS_SYSTEMGENERATERETRIEVE2"]:
  idx=t.index(marker);t=t[:idx]+'''  kira_eq::retrieve_begin();
  auto eq_callback=[&](eqdata&& eq){kira_eq::selected(eq);treateq(std::move(eq));};
'''+t[idx:]
 # Only replace callback in the two macro argument lists.
 t=t.replace('std::move(eqnums), treatcoeff, treateq, Config::parallel());','std::move(eqnums), treatcoeff, eq_callback, Config::parallel());')
 t=t.replace('Config::auto_symseed(), std::move(eqnums), treatcoeff, treateq,','Config::auto_symseed(), std::move(eqnums), treatcoeff, eq_callback,')
 for method,stage in [("generate_solve","generation_modular"),("select","equation_selection"),("select_coeff","equation_selection_coeff"),("solve","modular_solve"),("generate_retrieve","equation_regeneration")]:
  search=0
  while True:
   match=re.search(r'(?m)^[^"\n]*\bSystem::'+method+r'\(',t[search:])
   if not match:break
   idx=search+match.start()
   pos=t.index("{",idx)+1
   insert='\n  kira_eq::StageTimer equation_stage_timer("'+stage+'");'
   t=t[:pos]+insert+t[pos:];search=pos+len(insert)
 sources["interface.cpp"]=(p,t)
 commands=json.loads((BUILD/"compile_commands.json").read_text());objects={};records={}
 for name,(p,t) in sources.items():
  dest=OUT/name;dest.write_text(t)
  (HERE/"integration"/(name+".patch")).write_text("".join(difflib.unified_diff(p.read_text().splitlines(True),t.replace(str(header),header.name).splitlines(True),fromfile=str(p.relative_to(ROOT)),tofile=name)))
  cmd=shlex.split(next(c["command"] for c in commands if c["file"].endswith("/"+name)))
  obj=OUT/(name+".o")
  for flag,value in [("-o",obj),("-MF",OUT/(name+".d")),("-MQ",obj)]:cmd[cmd.index(flag)+1]=str(value)
  cmd[-1]=str(dest);subprocess.run(cmd,cwd=BUILD,check=True)
  objects[name]=str(obj);records[name]=dict(source=sha(p),patched=sha(dest),command=cmd)
 old=ROOT/".tools/kira-acceleration/libpyred_accel.a"
 members=subprocess.check_output(["ar","t",str(old)],text=True).splitlines()
 objs=[objects["relations.cpp"] if "relations_accel.o" in m else objects["interface.cpp"] if m.endswith("/interface.cpp.o") else str((ROOT/m).resolve()) for m in members]
 archive=OUT/"libpyred_eq.a"
 if archive.exists():archive.unlink()
 subprocess.run(["ar","crsT",str(archive)]+objs,check=True)
 link=json.loads((ROOT/"Kira_comparison/parallel_inference/build.json").read_text())["link_command"]
 link=[str(archive) if x.endswith("/libpyred_accel.a") else x for x in link]
 link[link.index("-o")+1]=str(binary.with_suffix(".tmp"));subprocess.run(link,cwd=BUILD,check=True);binary.with_suffix(".tmp").replace(binary)
 (HERE/"integration"/os.getenv("KIRA_EQ_BUILD_RECORD","build.json")).write_text(json.dumps(dict(sources=records,header_sha256=sha(header),binary_sha256=sha(binary),link_command=link),indent=2)+"\n")
 print("Equation integration compiled",flush=True)
if __name__=="__main__":main()
