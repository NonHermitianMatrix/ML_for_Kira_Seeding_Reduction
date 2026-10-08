"""Resume the same frozen test with smaller box-family execution batches."""
import argparse
import s06_evaluate as evaluation
from s06_evaluate import *
from s31_pack_small_batches import packed_batches
original_process=evaluation.process
original_batches=evaluation.batches
def process(meta,entry,dest,scratch):
 use_small=meta["family"].startswith("box_")
 evaluation.batches=packed_batches if use_small else original_batches
 result=original_process(meta,entry,dest,scratch)
 if use_small:
  result["batching_override"]=dict(script=Path(__file__).name,sha256=sha(Path(__file__)),
   splitter_script="s27_retry_small_batches.py",splitter_sha256=sha(HERE/"s27_retry_small_batches.py"),
   packing_script="s31_pack_small_batches.py",packing_sha256=sha(HERE/"s31_pack_small_batches.py"),
   targets_per_system=16,independent_systems_per_batch=4,source_equations_unchanged=True)
  evaluation.save_gz(dest/(meta["family"]+".summary.json.gz"),result)
 return result
def main(index):
 v=read(HERE/"small_batch_pilot/validation.json")
 assert v["passed"] and v["script_sha256"]==sha(HERE/"s27_retry_small_batches.py")
 check=read(HERE/"packing_validation.json")
 assert check["passed"] and check["packing_sha256"]==sha(HERE/"s31_pack_small_batches.py")
 config=read(HERE/"execution_overrides.json")
 assert config["script_sha256"]==sha(Path(__file__))
 assert config["splitter_sha256"]==sha(HERE/"s27_retry_small_batches.py")
 assert config["packing_sha256"]==sha(HERE/"s31_pack_small_batches.py")
 assert config["scientific_protocol_sha256"]==sha(HERE/"protocol.json")
 evaluation.process=process
 evaluation.worker(index)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--worker",type=int,required=True);main(p.parse_args().worker)
