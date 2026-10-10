"""Patch source selection inside native Kira and reuse the responsive shutdown."""
import os,difflib,hashlib,json,pathlib,shlex,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OUT=ROOT/os.getenv("KIRA_RUNTIME_BUILD_DIR",".tools/kira-integrated-runtime");BUILD=ROOT/".tools/kira-build"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 header=ROOT/"ML_model_reduction/runtime_training"/os.getenv("KIRA_RUNTIME_HEADER","s00_runtime_policy.h")
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
 # A single Fermat worker can process sector ranges sequentially.
 # The original code starts two helper threads per sector even at parallel=1.
 # Compact mode merges the ranges and commits their results together.
 old='  biggestSize = reduct2StartHere.size();'
 assert t.count(old)==1
 new='  const bool compact_bs=std::getenv("KIRA_BOUNDED_BACKSUB") &&\n      std::string(std::getenv("KIRA_BOUNDED_BACKSUB"))=="1" &&\n      coreNumber==1 && !reduct2StartHere.empty();\n  biggestSize = compact_bs ? 1 : reduct2StartHere.size();\n  const double bs_begin=kira_cost::now();\n  std::vector<unsigned> compact_order;\n  if(compact_bs){\n    std::vector<unsigned> indegree(reihen,0);\n    std::vector<std::vector<unsigned>> dependents(reihen);\n    for(unsigned row=0;row<reihen;++row){\n      if(!(rdy2P[row]&1))continue;\n      for(unsigned k=1;k<allEq[row][0][0].length;++k){\n        auto found=reverseLastReduce.find(allEq[row][0][k].id);\n        if(found==reverseLastReduce.end())continue;\n        unsigned dep=found->second;\n        if(dep>=reihen)throw ExceptionInternal("Back-substitution dependency outside loaded system");\n        if(rdy2P[dep]&1){++indegree[row];dependents[dep].push_back(row);}\n      }\n    }\n    std::priority_queue<unsigned,std::vector<unsigned>,std::greater<unsigned>> ready;\n    for(unsigned row=0;row<reihen;++row)if(!indegree[row])ready.push(row);\n    while(!ready.empty()){\n      const unsigned row=ready.top();ready.pop();compact_order.push_back(row);\n      for(unsigned next:dependents[row])if(--indegree[next]==0)ready.push(next);\n    }\n    if(compact_order.size()!=reihen)throw ExceptionInternal("Cyclic unresolved back-substitution dependencies");\n  }\n'
 t=t.replace(old,new)
 old='    if (itReduct < reduct2StartHere.size() - 1)'
 assert t.count(old)==1
 t=t.replace(old,'    if (!compact_bs && itReduct < reduct2StartHere.size() - 1)')
 t=t.replace('#include "'+str(header)+'"','#include <queue>\n#include "'+str(header)+'"',1)
 old='    unsigned itStart = /*itReduct*/ reduct2StartHere[itReduct];'
 assert t.count(old)==1
 t=t.replace(old,'    unsigned itStart = compact_bs ? 0 : reduct2StartHere[itReduct];')
 old='                     &clock, &database]() {'
 assert t.count(old)==1
 t=t.replace(old,'                     &clock, &database, compact_bs, &compact_order]() {')
 old='''      for (unsigned it = itStart; it < /*reihen*/ itEnd;
           it++ /*=biggestSize*/) {'''
 assert t.count(old)==1
 t=t.replace(old,'''      for (unsigned schedule_pos = itStart; schedule_pos < itEnd; ++schedule_pos) {
        const unsigned it = compact_bs ? compact_order[schedule_pos] : schedule_pos;''')

 anchor='  delete poolBS;\n  delete[] pool4;'
 assert t.count(anchor)==1
 t=t.replace(anchor,anchor+r'''
  if(const char* metrics=std::getenv("KIRA_STAGE_METRICS")){
    std::ofstream out(metrics,std::ios::app);
    out<<std::setprecision(17)<<R"json({"stage":"back_substitution","seconds":)json"
       <<kira_cost::now()-bs_begin<<R"json(,"sector_ranges":)json"<<reduct2StartHere.size()
       <<R"json(,"worker_ranges":)json"<<biggestSize<<R"json(,"equations":)json"<<reihen
       <<'}'<<std::endl;
  }
''')
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
