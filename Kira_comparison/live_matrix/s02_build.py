"""Build one changed translation unit; reuse the unchanged installed Kira objects."""
import hashlib,json,pathlib,shlex,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
build=ROOT/".tools/kira-build";out=ROOT/".tools/kira-live-build";out.mkdir(exist_ok=True)
original=ROOT/".tools/kira-source/src/kira/reduction.cpp"
text=original.read_text()
text=text.replace('using namespace std;', '#include "'+str(HERE/"s01_live_policy.h")+'"\n\nusing namespace std;',1)
start=text.index("int Kira::insert_equation(");end=text.index("\nvoid Kira::sort_equation",start)
part=text[start:end]
part=part.replace("  unsigned srange = EqPtr[0].length;","  kira_live::before(EqPtr, insertEqPtr);\n  unsigned srange = EqPtr[0].length;",1)
old="  if (srange != 0)\n    return 1;\n  else\n    return 0;"
assert old in part
part=part.replace(old,'''  kira_live::after(EqPtr, srange);
  if (srange != 0) return 1;
  if (!collectTerms.empty()) delete[] EqPtr;
  EqPtr = nullptr;
  return 0;''')
text=text[:start]+part+text[end:]
start=text.index("void Kira::run_reduction(")
point=text.index("  do {",start)
text=text[:point]+'''  kira_live::start();
  const double live_start=kira_live::now();
  const char* live_policy=std::getenv("KIRA_LIVE_POLICY");
  if(live_policy && std::string(live_policy)!="native") {
    const bool learned=std::string(live_policy)=="learned";
    if(!learned && std::string(live_policy)!="deterministic")
      throw std::runtime_error("Invalid live Kira policy");
    kira_live::forward(forwardRed,reduce_please,
      [this](BaseIntegral*& d,BaseIntegral*& q){return insert_equation(d,q);},learned);
    information=kira_live::steps;
  } else {
'''+text[point:]
point=text.index("  } while (red_1);",start)+len("  } while (red_1);")
text=text[:point]+'''\n  }
  kira_live::finish(kira_live::now()-live_start);
'''+text[point:]
modified=out/"reduction_live.cpp";modified.write_text(text)
commands=json.load(open(build/"compile_commands.json"))
compile=next(shlex.split(c["command"]) for c in commands if c["file"].endswith("/reduction.cpp"))
compile[compile.index("-o")+1]=str(out/"reduction_live.o")
compile[compile.index("-MF")+1]=str(out/"reduction_live.d")
compile[compile.index("-MQ")+1]=str(out/"reduction_live.o")
compile[-1]=str(modified)
ninja=ROOT/".tools/build-python/bin/ninja"
if not ninja.exists():ninja="ninja"
link=shlex.split(subprocess.check_output([str(ninja),"-C",str(build),"-t","commands","src/kira/kira"],text=True).splitlines()[-1])
link[link.index("-o")+1]=str(out/"kira")
link=[str(out/"reduction_live.o") if x=="src/kira/kira.p/reduction.cpp.o" else x for x in link]
subprocess.run(compile,cwd=build,check=True)
subprocess.run(link,cwd=build,check=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
record=dict(original_source_sha256=sha(original),modified_source_sha256=sha(modified),
            binary_sha256=sha(out/"kira"),header_sha256=sha(HERE/"s01_live_policy.h"),
            original_binary_sha256=sha(ROOT/".tools/kira/bin/kira"),
            compile_command=compile,link_command=link)
(HERE/"build.json").write_text(json.dumps(record,indent=2)+"\n")
print(json.dumps(record),flush=True)

