"""Verify disposable-directory guards against actual compiled database helper."""
import hashlib,json,pathlib,shutil,subprocess,tempfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 out=ROOT/".tools/kira-runtime-db"
 source=(out/"dataBase.cpp").read_text()
 begin=source.index("static void configure_ephemeral_database(")
 end=source.index("\nusing namespace std;",begin)
 helper=source[begin:end]
 harness=r'''
#include <sqlite3.h>
#include <cstdlib>
#include <climits>
#include <fstream>
#include <cstring>
#include <string>
#include <stdexcept>
#include <iostream>
#include <sys/stat.h>
#include <unistd.h>
'''
 harness+=helper+r'''
int scalar(sqlite3* db,const char* sql){
 sqlite3_stmt* s=nullptr;
 if(sqlite3_prepare_v2(db,sql,-1,&s,nullptr)!=SQLITE_OK)throw std::runtime_error("query");
 if(sqlite3_step(s)!=SQLITE_ROW)throw std::runtime_error("row");
 int v=sqlite3_column_int(s,0);sqlite3_finalize(s);return v;
}
void test(const std::string& path,bool reject,bool enabled){
 sqlite3* db=nullptr;if(sqlite3_open(path.c_str(),&db))throw std::runtime_error("open");
 bool failed=false;try{configure_ephemeral_database(db);}catch(const std::runtime_error&){failed=true;}
 if(failed!=reject)throw std::runtime_error("wrong rejection");
 if(!reject && enabled){
  if(scalar(db,"PRAGMA synchronous")!=0 || scalar(db,"PRAGMA cache_size")!=-8192)
   throw std::runtime_error("settings not applied");
 }else if(scalar(db,"PRAGMA synchronous")!=2)throw std::runtime_error("changed unrelated database");
 sqlite3_close(db);
}
int main(int argc,char** argv){
 if(argc!=2)return 2;
 const std::string base=argv[1],inside=base+"/inside",empty=base+"/empty";
 mkdir(inside.c_str(),0700);mkdir(empty.c_str(),0700);
 std::ofstream(inside+"/.kira_ephemeral_trial")<<"disposable";
 setenv("KIRA_EPHEMERAL_DB","1",1);setenv("KIRA_EPHEMERAL_ROOT",inside.c_str(),1);
 test(inside+"/accepted.db",false,true);
 test(base+"/outside.db",true,false);
 symlink((base+"/outside.db").c_str(),(inside+"/escape.db").c_str());
 test(inside+"/escape.db",true,false);
 setenv("KIRA_EPHEMERAL_ROOT",empty.c_str(),1);test(empty+"/unmarked.db",true,false);
 unsetenv("KIRA_EPHEMERAL_ROOT");test(base+"/missing_root.db",true,false);
 setenv("KIRA_EPHEMERAL_DB","0",1);test(base+"/disabled.db",false,false);
 std::cout<<"6 directory and settings checks passed\\n";
}
'''
 scratch=pathlib.Path(tempfile.mkdtemp(prefix="guard_",dir=out))
 try:
  cpp=scratch/"guard.cpp";cpp.write_text(harness)
  subprocess.run(["g++","-std=c++17","-O1",str(cpp),"-lsqlite3","-o",str(scratch/"guard")],check=True,timeout=60)
  result=subprocess.check_output([str(scratch/"guard"),str(scratch)],text=True,timeout=20)
  record=dict(all_passed=True,checks=6,helper_sha256=hashlib.sha256(helper.encode()).hexdigest(),source_sha256=hashlib.sha256(source.encode()).hexdigest(),result=result)
  (HERE/"database_guard_tests.json").write_text(json.dumps(record,indent=2)+"\n")
  print(json.dumps(record),flush=True)
 finally:shutil.rmtree(scratch)
if __name__=="__main__":main()
