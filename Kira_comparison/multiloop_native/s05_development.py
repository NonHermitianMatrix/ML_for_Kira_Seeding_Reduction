"""Collect cost labels only from the fixed training and validation cases."""
import argparse,json,pathlib
from s02_run import run
from s04_records import read_record
HERE=pathlib.Path(__file__).resolve().parent
def main():
 ap=argparse.ArgumentParser();ap.add_argument("case",type=int);a=ap.parse_args()
 for name in ["sunrise_stock","sunrise_collect","box_stock","vacuum_stock"]:
  r=read_record(HERE/"pilot_v3"/(name+".json.gz"));assert r["success"],name
 cases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["split"]!="reserved"]
 case=cases[a.case];size=min(32,len(case["targets"]))
 output=HERE/"references"/(case["id"]+f"_n{size}.json.gz")
 ref=read_record(output) if output.exists() else run(case,size,"stock",output,timeout=360)
 if not ref["success"]:
  print(json.dumps(dict(case=case["id"],stage="reference",status=ref["status"])),flush=True);return
 output=HERE/"training"/(case["id"]+f"_n{size}.json.gz")
 result=read_record(output) if output.exists() else run(case,size,"collect",output,timeout=600,reference=HERE/"references"/(case["id"]+f"_n{size}.json.gz"))
 print(json.dumps({k:result.get(k) for k in ["case","size","status","success","complete_seconds","metrics"]}),flush=True)
if __name__=="__main__":main()
