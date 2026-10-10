"""Store repeated exact outputs once, verifying lossless record recovery."""
import gzip,hashlib,json,pathlib
from s04_workflows import HERE,read,save,canonical,guard
def main():
 record=[];before=sum(p.stat().st_blocks*512 for p in HERE.rglob("*") if p.is_file())
 paths=sorted(list((HERE/"validation").rglob("*.json.gz"))+list((HERE/"development_overlap/validation").rglob("*.json.gz")))
 for p in paths:
  r=read(p)
  if "attempts" not in r:continue
  digest=hashlib.sha256(canonical(r)).hexdigest();old=hashlib.sha256(p.read_bytes()).hexdigest()
  save(p,r);assert hashlib.sha256(canonical(read(p))).hexdigest()==digest
  record.append(dict(file=str(p.relative_to(HERE)),decoded_sha256=digest,old_storage_sha256=old,new_storage_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 after=sum(p.stat().st_blocks*512 for p in HERE.rglob("*") if p.is_file())
 audit=dict(lossless=True,records=len(record),allocated_before=before,allocated_after=after,record_digests=record)
 (HERE/"validation/storage_integrity.json").write_text(json.dumps(audit,indent=2)+"\n")
 guard();print(json.dumps({k:v for k,v in audit.items() if k!="record_digests"}),flush=True)
if __name__=="__main__":main()
