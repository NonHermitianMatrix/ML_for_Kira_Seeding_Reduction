"""Build native inference while preserving stock and earlier experimental binaries."""
import hashlib,json,pathlib,shlex,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
build=ROOT/".tools/kira-build";out=ROOT/".tools/kira-cpp-row";out.mkdir(exist_ok=True)
header=(HERE.parent/"live_matrix/s01_live_policy.h").read_text()
header=header.replace("extern char **environ;",'#include "'+str(HERE/"s23_cpp_model.h")+'"\nextern char **environ;')
header=header.replace(' std::unique_ptr<Broker> broker;',' const bool compiled=std::getenv("KIRA_ROW_SCOPE") && std::string(std::getenv("KIRA_ROW_SCOPE"))=="compiled_source";\n std::unique_ptr<Broker> broker;')
header=header.replace('if(learned){broker.reset(', 'if(learned&&!compiled){broker.reset(')
header=header.replace('if(learned){auto action=broker->choose(group,weight);q=action.first;r=action.second;}',
 'if(learned){auto action=compiled?kira_cpp::choose(group,rows,weight):broker->choose(group,weight);q=action.first;r=action.second;}')
header=header.replace('if(learned)broker->row(', 'if(learned&&!compiled)broker->row(')
header=header.replace('if(learned)broker->finish();','if(learned&&!compiled)broker->finish();')
(HERE/"s25_cpp_live_policy.h").write_text(header)
original=ROOT/".tools/kira-live-build/reduction_live.cpp"
text=original.read_text().replace(str(HERE.parent/"live_matrix/s01_live_policy.h"),str(HERE/"s25_cpp_live_policy.h"))
assert str(HERE/"s25_cpp_live_policy.h") in text
modified=out/"reduction_cpp.cpp";modified.write_text(text)
commands=json.load(open(build/"compile_commands.json"))
compile=next(shlex.split(c["command"]) for c in commands if c["file"].endswith("/reduction.cpp"))
for flag,name in [("-o","reduction_cpp.o"),("-MF","reduction_cpp.d"),("-MQ","reduction_cpp.o")]:
 compile[compile.index(flag)+1]=str(out/name)
compile[-1]=str(modified)
ninja=ROOT/".tools/build-python/bin/ninja"
link=shlex.split(subprocess.check_output([str(ninja),"-C",str(build),"-t","commands","src/kira/kira"],text=True).splitlines()[-1])
link[link.index("-o")+1]=str(out/"kira")
link=[str(out/"reduction_cpp.o") if x=="src/kira/kira.p/reduction.cpp.o" else x for x in link]
seed_build=json.loads((HERE/"build.json").read_text())
archives=[x for x in seed_build["link"] if x.endswith(".a") and "kira-acceleration" in x]
assert len(archives)==1,archives
assert "src/pyred/libpyred.a" in link
link=[archives[0] if x=="src/pyred/libpyred.a" else x for x in link]
subprocess.run(compile,cwd=build,check=True);subprocess.run(link,cwd=build,check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record=dict(source_sha256=sha(modified),binary_sha256=sha(out/"kira"),header_sha256=sha(HERE/"s23_cpp_model.h"),
 weights_sha256=sha(HERE/"s24_row_weights.h"),compile_command=compile,link_command=link,
 original_solver_sha256=sha(ROOT/".tools/kira/bin/kira"))
(HERE/"cpp_build.json").write_text(json.dumps(record,indent=2)+"\n")
print("Native source-row policy compiled",flush=True)
