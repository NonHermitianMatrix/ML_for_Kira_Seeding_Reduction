"""Restore shared structured results and verify their unchanged logical content."""
import gzip,hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
def canonical(value):return json.dumps(value,separators=(",",":"),allow_nan=False).encode()
def restore(value):
 if not isinstance(value,dict) or "$json" not in value:return value
 assert set(value)=={"$json","bytes"}
 digest=value["$json"];assert len(digest)==64 and all(c in "0123456789abcdef" for c in digest)
 with gzip.open(HERE/"structured_evidence"/(digest+".json.gz"),"rb") as stream:raw=stream.read()
 assert len(raw)==value["bytes"] and hashlib.sha256(raw).hexdigest()==digest
 return json.loads(raw)
def read_record(path):
 with gzip.open(path,"rt") as stream:r=json.load(stream)
 metadata=r.pop("_storage",None)
 if metadata:
  assert metadata["format"]=="shared-json-v1"
  if "checks" in r:r["checks"]=restore(r["checks"])
  if "probabilities" in r.get("model",{}):r["model"]["probabilities"]=restore(r["model"]["probabilities"])
  assert hashlib.sha256(canonical(r)).hexdigest()==metadata["logical_sha256"]
 return r
