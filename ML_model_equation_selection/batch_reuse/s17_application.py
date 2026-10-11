"""Apply identical learned choices through a native inference library."""
import argparse,importlib.util,gzip
from s00_common import *
from s16_native import load_native,select_native
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
 ap.add_argument("--backend",choices=["native","python","control","deployed","previous"],default="deployed");ap.add_argument("--model",default="forest4.json");ap.add_argument("--separate",action="store_true");a=ap.parse_args()
 driver=module("current_driver","s02_reduce.py");pack=module("current_pack","s11_pack.py")
 start=time.perf_counter();source=json.loads(a.input.read_text());requests=source["requests"];policy=json.loads((HERE/"trained_model/deployment.json").read_text())
 if a.backend=="deployed":
  np=json.loads((HERE/"trained_model/native_deployment.json").read_text());a.backend=np["backend"];a.model=np["model"]
 mode=policy["control"] if a.backend=="control" else "model"
 if a.backend=="native":
  driver.load_model=load_native;driver.select=select_native;pack.load_model=load_native;pack.select=select_native;pack.driver.load_model=load_native;pack.driver.select=select_native
 assert ROOT in a.output.resolve().parents
 if a.separate or a.backend=="previous":
  parts=[driver.previous.apply(c,"extreme",shared=True) if a.backend=="previous" else driver.apply(c,mode,a.model) for c in requests]
  result=dict(backend=a.backend,mode=mode,success=all(x["success"] for x in parts),packed=False,fallbacks=sum(x["fallbacks"] for x in parts),complete_seconds=time.perf_counter()-start,equations=sum(x["attempts"][0]["equations"] if a.backend=="previous" else x["equations"] for x in parts),algebra=dict(seconds=sum((x["attempts"][0]["algebra"] if a.backend=="previous" else x["algebra"])["seconds"] for x in parts),peak_tree_rss_bytes=max((x["attempts"][0]["algebra"] if a.backend=="previous" else x["algebra"])["peak_tree_rss_bytes"] for x in parts),peak_scratch_bytes=max((x["attempts"][0]["algebra"] if a.backend=="previous" else x["algebra"])["peak_scratch_bytes"] for x in parts)),individual_records=[])
  for i,x in enumerate(parts):
   if a.backend=="previous":
    for attempt in x["attempts"]:
     payload={k:attempt.pop(k) for k in ["raw_export","source_choices"] if k in attempt}
     payload["log"]=attempt["algebra"].pop("log")
     data=json.dumps(payload,sort_keys=True,separators=(",",":")).encode();h=hashlib.sha256(data).hexdigest();obj=HERE/"objects"/(h+".json.gz")
     if not obj.exists():obj.write_bytes(gzip.compress(data,compresslevel=9,mtime=0))
     attempt["payload_sha256"]=h
   dest=a.output.with_name(a.output.stem+"_part"+str(i)+".json");driver.save(dest,x);result["individual_records"].append(str(dest.relative_to(HERE)))
  write(a.output,result)
 else:
  result=pack.apply(requests,mode,a.model);result.update(backend=a.backend,complete_seconds=time.perf_counter()-start);driver.save(a.output,result)
 print(json.dumps({k:result[k] for k in ["backend","success","complete_seconds","fallbacks"]}),flush=True)
if __name__=="__main__":main()
