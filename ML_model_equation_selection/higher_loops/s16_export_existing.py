"""Prepare scalar-component requests from the existing coupled vacuum dataset."""
import argparse,gzip,hashlib,lzma,re
from s00_math import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument("family");ap.add_argument("--output",type=Path,required=True)
 ap.add_argument("--target-records",type=int,default=8);ap.add_argument("--loops",type=int,nargs="+")
 a=ap.parse_args();assert re.fullmatch(r"vacuum_L\d+_profile\d+",a.family) and 1<=a.target_records<=32
 base=ROOT/"integrals";p=base/"master_integrals/families"/a.family/"definition.json";d=json.loads(p.read_text())
 L=len(d["loop_momenta"]);rho=d["mass_ratios"];r=len(rho);root=base/"target_integrals/families"/a.family
 candidates=[p for p in [root/"inputs.jsonl.gz",root/"inputs.jsonl.xz"] if p.exists()];assert len(candidates)==1
 source=candidates[0];opener=lzma.open if source.suffix==".xz" else gzip.open
 rows=[];targets=[]
 with opener(source,"rt") as f:
  for line in f:
   t=json.loads(line);rows.append(t["id"])
   for term in t["terms"]:
    indices=term["indices"];assert len(indices)==L+r and indices[:L]==[1]*L
    b=indices[L:]
    if b not in targets:targets.append(b)
   if len(rows)>=a.target_records:break
 request=dict(id="existing_"+a.family,family="coupled_vacuum_unit_massless",mass_ratios=rho,targets=targets,loops=a.loops or [L],mass_scale_squared=1,source_family=a.family,source_target_records=rows,source_file=str(source.relative_to(ROOT)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),scope="Scalar components of the selected public target expressions; combine returned coefficients with their original target weights and restore the common mass scale.")
 validate(request);write(a.output,request);print(json.dumps(dict(request=str(a.output),scalar_components=len(targets),loops=request["loops"])))
if __name__=="__main__":main()
