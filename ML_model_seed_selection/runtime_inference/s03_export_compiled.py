"""Export unchanged float32 weights into a bounded portable runtime archive."""
import hashlib,json,pathlib,struct
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 source=ROOT/"Kira_comparison/acceleration";meta=json.loads((source/"seed_export.json").read_text());c=meta["config"]
 names=["family.0","master.0","seed.0","term.0","pair.0","score.0","score.2"];data=bytearray(b"MLSEED01")
 data+=struct.pack("<7I",*[c[k] for k in ["max_indices","hash_bins","hidden","pair_chunk","candidate_chunk","max_terms"]],len(names))
 with np.load(source/"seed_weights.npz",allow_pickle=False) as weights:
  for name in names:
   w=weights[name+".weight"].astype("<f4");b=weights[name+".bias"].astype("<f4");assert w.ndim==2 and b.shape==(w.shape[0],)
   data+=struct.pack("<I",len(name))+name.encode()+struct.pack("<2I",*w.shape)+w.tobytes()+b.tobytes()
 assert len(data)<1024**2
 (HERE/"compiled_weights.bin").write_bytes(data)
 record=dict(config=c,checkpoint_sha256=meta["checkpoint_sha256"],source_archive_sha256=hashlib.sha256((source/"seed_weights.npz").read_bytes()).hexdigest(),weights_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),float_format="little-endian IEEE754 float32; unchanged coefficients")
 (HERE/"compiled_export.json").write_text(json.dumps(record,indent=2)+"\n")
 print(json.dumps({k:v for k,v in record.items() if k!="config"}),flush=True)
if __name__=="__main__":main()
