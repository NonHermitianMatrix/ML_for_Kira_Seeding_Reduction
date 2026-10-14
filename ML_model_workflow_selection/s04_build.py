"""Combine existing early equation filtering and guarded temporary databases."""
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'.tools/kira-workflow';out.mkdir(exist_ok=True)
 source=ROOT/'ML_model_equation_selection/early_generation/integration/build.json'
 cmd=json.loads(source.read_text())['link_command']
 old='src/kira/kira.p/dataBase.cpp.o';assert cmd.count(old)==1
 database=ROOT/'.tools/kira-runtime-db/dataBase.o'
 cmd=[str(database) if x==old else x for x in cmd]
 dest=out/'kira';cmd[cmd.index('-o')+1]=str(dest)
 subprocess.run(cmd,cwd=ROOT/'.tools/kira-build',check=True)
 (HERE/'build.json').write_text(json.dumps(dict(link_command=cmd,parent_build_sha256=sha(source),database_source_sha256=sha(ROOT/'.tools/kira-runtime-db/dataBase.cpp'),binary_sha256=sha(dest),change='Link the existing guarded temporary database implementation with early equation filtering.'),indent=2)+'\n')
 print('Combined integration built',flush=True)
if __name__=='__main__':main()
