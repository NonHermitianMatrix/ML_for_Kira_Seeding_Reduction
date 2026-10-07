"""Check the publication size estimate against bounded temporary Git objects."""
import hashlib,json,subprocess,tempfile,zlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 checks=[]
 with tempfile.TemporaryDirectory(prefix="publication-size-check-",dir=str(ROOT/".tools")) as name:
  work=Path(name)
  subprocess.run(["git","init","-q"],cwd=name,check=True)
  for data in [b'{"family":"bounded_example","indices":[1,2,3,4]}\n'*30000,bytes(range(256))*8192]:
   assert len(data)<4*1024**2
   compressor=zlib.compressobj(6)
   count=len(compressor.compress(("blob %d\0"%len(data)).encode()))
   for start in range(0,len(data),1048576):count+=len(compressor.compress(data[start:start+1048576]))
   count+=len(compressor.flush())
   oid=subprocess.check_output(["git","-c","core.looseCompression=6","hash-object","-w","--stdin"],input=data,cwd=name).decode().strip()
   actual=(work/".git/objects"/oid[:2]/oid[2:]).stat().st_size
   assert actual==count,(actual,count)
   checks.append(dict(source_bytes=len(data),estimated_compressed_bytes=count,actual_git_bytes=actual))
 result=dict(status="passed",checks=checks,temporary_objects_removed=True,publication_source_sha256=hashlib.sha256((HERE/"s20_publish_release.py").read_bytes()).hexdigest())
 (HERE/"git_blob_estimate_validation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result),flush=True)
if __name__=="__main__":main()
