"""Build opt-in database settings restricted to disposable trial directories."""
import difflib,hashlib,json,pathlib,shlex,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OUT=ROOT/".tools/kira-runtime-db";BUILD=ROOT/".tools/kira-build"
def main():
 OUT.mkdir(exist_ok=True)
 source=ROOT/".tools/kira-source/src/kira/dataBase.cpp";original=source.read_text()
 helper=r'''
#include <cstdlib>
#include <climits>
#include <fstream>
#include <cstring>
static void configure_ephemeral_database(sqlite3* db) {
  const char* mode=std::getenv("KIRA_EPHEMERAL_DB");
  if(!mode || std::string(mode)!="1") return;
  const char* base=std::getenv("KIRA_EPHEMERAL_ROOT");
  const char* filename=sqlite3_db_filename(db,"main");
  char root[PATH_MAX],file[PATH_MAX];
  if(!base || !filename || !realpath(base,root) || !realpath(filename,file))
    throw std::runtime_error("Invalid ephemeral database path");
  const std::string prefix=std::string(root)+"/";
  if(std::string(file).compare(0,prefix.size(),prefix)!=0 ||
      !std::ifstream(prefix+".kira_ephemeral_trial"))
    throw std::runtime_error("Database outside disposable trial directory");
  char* error=nullptr;
  int rc=sqlite3_exec(db,
      "PRAGMA journal_mode=MEMORY; PRAGMA synchronous=OFF; "
      "PRAGMA temp_store=MEMORY; PRAGMA cache_size=-8192;",
      nullptr,nullptr,&error);
  if(rc!=SQLITE_OK){
    std::string message=error?error:"unknown SQLite error";
    sqlite3_free(error);throw std::runtime_error(message);
  }
}
'''
 s=original.replace('using namespace std;',helper+'\nusing namespace std;',1)
 anchor='  string equation("EQUATION");'
 assert s.count(anchor)==2
 s=s.replace(anchor,'  configure_ephemeral_database(db);\n'+anchor)
 target=OUT/"dataBase.cpp";target.write_text(s)
 (HERE/"ephemeral_database.patch").write_text("".join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile="a/src/kira/dataBase.cpp",tofile="b/src/kira/dataBase.cpp")))
 commands=json.loads((BUILD/"compile_commands.json").read_text())
 command=next(shlex.split(c["command"]) for c in commands if c["file"].endswith("/dataBase.cpp"))
 for flag,name in [("-o","dataBase.o"),("-MF","dataBase.d"),("-MQ","dataBase.o")]:command[command.index(flag)+1]=str(OUT/name)
 command[-1]=str(target)
 link=json.loads((HERE/"fast_rows_build.json").read_text())["link_command"]
 link[link.index("-o")+1]=str(OUT/"kira")
 assert link.count("src/kira/kira.p/dataBase.cpp.o")==1
 link=[str(OUT/"dataBase.o") if x=="src/kira/kira.p/dataBase.cpp.o" else x for x in link]
 subprocess.run(command,cwd=BUILD,check=True);subprocess.run(link,cwd=BUILD,check=True)
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 (HERE/"ephemeral_db_build.json").write_text(json.dumps(dict(source_sha256=sha(source),modified_sha256=sha(target),binary_sha256=sha(OUT/"kira"),compile_command=command,link_command=link,scope="Opt-in freshly generated, disposable per-trial databases only. No restart from these databases after interruption."),indent=2)+"\n")
 print("Ephemeral database build complete",flush=True)
if __name__=="__main__":main()
