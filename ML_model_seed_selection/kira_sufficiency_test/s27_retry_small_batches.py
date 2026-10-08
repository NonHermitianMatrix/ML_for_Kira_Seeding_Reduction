"""Retry unresolved symbolic systems with independent, smaller target batches."""
import argparse,copy,shutil
import s06_evaluate as evaluation
from s06_evaluate import *
def small_batches(blocks):
 bid=0
 for block in blocks:
  for start in range(0,len(block["targets"]),16):
   chosen=block["targets"][start:start+16];ids={t["id"] for t in chosen}
   piece=dict(block,id=bid,targets=chosen,
    policies={k:[tid for tid in tids if tid in ids] for k,tids in block["policies"].items()})
   bid+=1
   yield [piece]
def main(fid):
 evaluation.batches=small_batches
 meta=next(m for m in read(MODEL/"split_manifest.json")["families"] if m["family"]==fid)
 assert meta["split"]=="test"
 entry=next(e for e in read(MODEL/"model_test/prediction_manifest.json")["families"] if e["family"]==fid)
 dest=HERE/"small_batch_pilot";dest.mkdir(exist_ok=True)
 scratch=Path(os.environ["KIRA_SCRATCH"])/fid;scratch.mkdir()
 result=evaluation.process(meta,entry,dest,scratch)
 result["batching_override"]=dict(script=Path(__file__).name,sha256=sha(Path(__file__)),targets_per_system=16)
 evaluation.save_gz(dest/(fid+".summary.json.gz"),result)
 assert result["counts"]["full"].get("sufficient",0)==result["targets"]
 write(dest/"validation.json",dict(passed=True,family=fid,targets=result["targets"],counts=result["counts"],
   batches=len(result["batches"]),seconds=result["seconds"],script_sha256=sha(Path(__file__))))
 print(json.dumps(read(dest/"validation.json")),flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--family",default="box_profile_0168");main(p.parse_args().family)
