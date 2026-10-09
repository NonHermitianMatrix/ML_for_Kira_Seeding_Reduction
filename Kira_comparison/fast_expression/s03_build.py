"""Build an isolated stock Kira with responsive, bounded Fermat shutdown."""
import difflib,hashlib,json,pathlib,shlex,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/".tools/kira-fast-expression";out.mkdir(exist_ok=True)
 build=ROOT/".tools/kira-build";source=ROOT/".tools/kira-source/src/kira/connect2kira.cpp"
 original=source.read_text();begin=original.index("  // give Fermat some time to properly close itself")
 end=original.index("\n  if (mustCleanup)",begin)
 text=original[:begin]+"  // Reap promptly, retaining the original one-second grace and kill fallback.\n  kira_responsive::reap(g_childpid, status);\n"+original[end:]
 text=text.replace('#include "kira/connect2kira.h"','#include "'+str(HERE/"s01_reap_child.h")+'"\n#include "kira/connect2kira.h"')
 modified=out/"connect2kira_fast.cpp";modified.write_text(text)
 (HERE/"connect2kira.patch").write_text("".join(difflib.unified_diff(original.splitlines(True),text.replace(str(HERE/"s01_reap_child.h"),"s01_reap_child.h").splitlines(True),fromfile="a/src/kira/connect2kira.cpp",tofile="b/src/kira/connect2kira.cpp")))
 commands=json.loads((build/"compile_commands.json").read_text())
 compile=next(shlex.split(c["command"]) for c in commands if c["file"].endswith("/connect2kira.cpp"))
 for flag,name in [("-o","connect2kira_fast.o"),("-MF","connect2kira_fast.d"),("-MQ","connect2kira_fast.o")]:
  compile[compile.index(flag)+1]=str(out/name)
 compile[-1]=str(modified)
 link=shlex.split(subprocess.check_output([str(ROOT/".tools/build-python/bin/ninja"),"-C",str(build),"-t","commands","src/kira/kira"],text=True).splitlines()[-1])
 link[link.index("-o")+1]=str(out/"kira")
 assert link.count("src/kira/kira.p/connect2kira.cpp.o")==1
 link=[str(out/"connect2kira_fast.o") if x=="src/kira/kira.p/connect2kira.cpp.o" else x for x in link]
 subprocess.run(["g++","-std=c++17","-O2","-pthread",str(HERE/"s02_reap_test.cpp"),"-o",str(out/"reap_test")],check=True)
 checks=json.loads(subprocess.check_output([str(out/"reap_test")],text=True))
 (HERE/"reap_validation.json").write_text(json.dumps(checks,indent=2)+"\n")
 subprocess.run(compile,cwd=build,check=True);subprocess.run(link,cwd=build,check=True)
 commit=subprocess.check_output(["git","-C",str(ROOT/".tools/kira-source"),"rev-parse","HEAD"],text=True).strip()
 record=dict(original_source_sha256=sha(source),modified_source_sha256=sha(modified),header_sha256=sha(HERE/"s01_reap_child.h"),
  original_binary_sha256=sha(ROOT/".tools/kira/bin/kira"),modified_binary_sha256=sha(out/"kira"),
  upstream_commit=commit,upstream="https://gitlab.com/kira-pyred/kira",compile_command=compile,link_command=link,
  changed_object="connect2kira.cpp only; stock symbolic elimination and all model weights preserved",checks=checks)
 (HERE/"build.json").write_text(json.dumps(record,indent=2)+"\n")
 print(json.dumps(record),flush=True)
if __name__=="__main__":main()
