"""Check gzip/XZ readers and new record links without model updates."""
import gzip,importlib.util,json,lzma,os,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"ML_model_seed_selection"))
from s01_data import rows as seed_rows
sys.path.insert(0,str(ROOT/"ML_model_reduction"))
from s00_common import rows as reduction_rows,record_path,sha
spec=importlib.util.spec_from_file_location("integral_reader",ROOT/"integrals/s01_read_data.py")
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
assert os.environ.get("JOB_ID"),"Use compute allocation"
checked=[]
for profile in (350,351,352):
 fid="vacuum_L12_profile%03d"%profile
 targets=list(reader.records(fid,"inputs"));references=list(reader.records(fid,"references"))
 assert len(targets)==len(references)==128
 for a,b in zip(targets,references):assert a["id"]==b["id"]
 base=ROOT/"integrals/target_integrals/families"/fid
 path=record_path(base/"inputs.jsonl.gz")
 assert targets==list(seed_rows(path))==list(reduction_rows(path))
 assert reader.linked_target(targets[0]["id"])["references"]==references[0]
 payload=b"".join((json.dumps(t)+"\n").encode() for t in targets)
 with tempfile.TemporaryDirectory(dir=str(HERE)) as tmp:
  gz=Path(tmp)/"copy.jsonl.gz";xz=Path(tmp)/"copy.jsonl.xz"
  with gzip.open(gz,"wb") as f:f.write(payload)
  with lzma.open(xz,"wb",preset=3) as f:f.write(payload)
  assert list(seed_rows(gz))==list(seed_rows(xz))==targets
  assert list(reduction_rows(gz))==list(reduction_rows(xz))==targets
  gz.unlink();assert record_path(gz)==xz and list(reduction_rows(gz))==targets
 checked.append(dict(family=fid,targets=len(targets),compression=path.suffix))
result=dict(status="passed",checks=checked,optimizer_updates=0,predictions_made=0,
 source_hashes={p:sha(ROOT/p) for p in ["integrals/s01_read_data.py","ML_model_seed_selection/s01_data.py","ML_model_reduction/s00_common.py","ML_model_reduction/s02_prepare_data.py","ML_model_reduction/model_test/s02_evaluate.py"]})
(HERE/"reader_validation.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result),flush=True)
