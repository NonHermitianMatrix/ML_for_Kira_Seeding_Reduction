"""Patch source selection inside native Kira and reuse the responsive shutdown."""
import os,difflib,hashlib,json,pathlib,shlex,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OUT=ROOT/os.getenv("KIRA_COST_BUILD_DIR",".tools/kira-cost-training");BUILD=ROOT/".tools/kira-build"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 header=HERE/os.getenv("KIRA_COST_HEADER","s00_cost_policy.h")
 source=ROOT/".tools/kira-source/src/kira/reduction.cpp";original=source.read_text();t=original
 t=t.replace('using namespace std;','#include "'+str(header)+'"\nusing namespace std;',1)
 start=t.index("int Kira::insert_equation(");end=t.index("\nvoid Kira::sort_equation",start)
 part=t[start:end].replace("  unsigned srange = EqPtr[0].length;","  kira_cost::before(EqPtr,insertEqPtr);\n  unsigned srange = EqPtr[0].length;",1)
 old="  if (srange != 0)\n    return 1;\n  else\n    return 0;"
 assert old in part
 part=part.replace(old,"  kira_cost::after(EqPtr,srange);\n  if(srange) return 1;\n  if(!collectTerms.empty()) delete[] EqPtr;\n  EqPtr=nullptr; return 0;")
 t=t[:start]+part+t[end:]
 anchor="  for (uint32_t jtt = 1; jtt < lengthEQ; jtt++) {\n    insert_equation(fwEQ[0][jtt], fwEQ[0][0]);"
 assert t.count(anchor)==1
 t=t.replace(anchor,"  kira_cost::choose(fwEQ[0],lengthEQ,[this](BaseIntegral*& d,BaseIntegral*& s){return insert_equation(d,s);});\n"+anchor)
 # Zero rows have no destination bucket. This also makes counterfactual clones
 # safe when an exact cancellation occurs.
 anchor="  for (uint32_t jtt = 1; jtt < lengthEQ; jtt++) {\n    pyred::Weight ID = fwEQ[0][jtt][0].id;"
 assert t.count(anchor)==1
 t=t.replace(anchor,anchor.replace("    pyred::Weight","    if(!fwEQ[0][jtt]) continue;\n    pyred::Weight"))
 start=t.index("void Kira::run_reduction(");point=t.index("  do {",start)
 t=t[:point]+"  kira_cost::start();\n  const double cost_begin=kira_cost::now();\n"+t[point:]
 point=t.index("  } while (red_1);",start)+len("  } while (red_1);")
 t=t[:point]+"\n  kira_cost::finish(kira_cost::now()-cost_begin);\n"+t[point:]
 OUT.mkdir(exist_ok=True);modified=OUT/"reduction_cost.cpp";modified.write_text(t)
 (HERE/os.getenv("KIRA_COST_PATCH","reduction_cost.patch")).write_text("".join(difflib.unified_diff(original.splitlines(True),t.replace(str(header),header.name).splitlines(True),fromfile="a/src/kira/reduction.cpp",tofile="b/src/kira/reduction.cpp")))
 commands=json.loads((BUILD/"compile_commands.json").read_text())
 command=next(shlex.split(c["command"]) for c in commands if c["file"].endswith("/reduction.cpp"))
 for flag,name in [("-o","reduction_cost.o"),("-MF","reduction_cost.d"),("-MQ","reduction_cost.o")]:command[command.index(flag)+1]=str(OUT/name)
 command[-1]=str(modified)
 link=json.loads((ROOT/"Kira_comparison/fast_expression/build.json").read_text())["link_command"]
 link=list(link);link[link.index("-o")+1]=str(OUT/"kira")
 assert link.count("src/kira/kira.p/reduction.cpp.o")==1
 link=[str(OUT/"reduction_cost.o") if x=="src/kira/kira.p/reduction.cpp.o" else x for x in link]
 # Reuse the already verified individual-seed gate; disabled by default.
 seed=json.loads((ROOT/"Kira_comparison/acceleration/build.json").read_text())
 archive=[x for x in seed["link"] if x.endswith(".a") and "kira-acceleration" in x]
 assert len(archive)==1
 link=[archive[0] if x=="src/pyred/libpyred.a" else x for x in link]
 subprocess.run(command,cwd=BUILD,check=True);subprocess.run(link,cwd=BUILD,check=True)
 record=dict(original_source_sha256=sha(source),source_sha256=sha(modified),header_sha256=sha(header),
  binary_sha256=sha(OUT/"kira"),compile_command=command,link_command=link,
  original_binary_sha256=sha(ROOT/".tools/kira/bin/kira"),responsive_binary_sha256=sha(ROOT/".tools/kira-fast-expression/kira"))
 (HERE/os.getenv("KIRA_COST_BUILD_RECORD","build.json")).write_text(json.dumps(record,indent=2)+"\n")
 print("Native source-row cost hook compiled",flush=True)
if __name__=="__main__":main()
