"""Bounded compressed exact evidence."""
import gzip,json,pathlib,subprocess,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/"Kira_comparison/integrated_runtime"))
from s105_parallel_records import read_record as legacy_read
def read(path):
 path=pathlib.Path(path).resolve()
 if HERE not in path.parents:return legacy_read(path)
 with gzip.open(path,"rt") as f:return json.load(f)
def packed(path,record):
 path=pathlib.Path(path).resolve();assert HERE in path.parents and not path.exists()
 data=gzip.compress(json.dumps(record,separators=(",",":"),sort_keys=True).encode(),compresslevel=6,mtime=0)
 cap=json.loads((HERE/"resource_plan.json").read_text())["additional_data_cap_bytes"]
 used=int(subprocess.check_output(["du","-s","-B1",str(HERE)],text=True).split()[0])
 if used+len(data)+8192>cap:raise RuntimeError("Equation experiment storage bound")
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
