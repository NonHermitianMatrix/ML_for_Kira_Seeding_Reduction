"""Extend canonical catalogs and the existing grouped split after independent validation."""
import collections,gzip,lzma,hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;DATA=HERE.parent;ROOT=DATA.parent;MODEL=ROOT/"ML_model_seed_selection"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 with (lzma.open if p.suffix==".xz" else gzip.open)(p,"rt",encoding="utf-8") as f:
  for line in f:yield json.loads(line)
def main():
 validation=read(HERE/"validation.json");assert validation["status"]=="passed" and len(validation["families"])==12000
 added=read(HERE/"generation_summary.json")["families"];assert len(added)==12000
 split=read(MODEL/"split_manifest.json");existing={m["family"]:m for m in split["families"]}
 baseline=read(HERE/"previous_split_manifest.json")
 for m in baseline["families"]:assert existing[m["family"]]["split"]==m["split"]
 hashes=read(MODEL/"source_hashes.json")
 catalog=read(DATA/"catalog.json");entries={m["family"]:m for m in catalog["families"]}
 for x in added:
  fid=x["family"];m="master_integrals/families/"+fid;r="master_to_target/families/"+fid;t="target_integrals/families/"+fid
  item=dict(family=fid,loops=x["loops"],split=x["split"],group=x["group"],definition=m+"/definition.json",
    masters=m+"/masters.json",inputs=t+"/inputs.jsonl.xz",references=r+"/references.jsonl.xz",seeds=r+"/candidate_seeds.json",counts=x["counts"])
  if fid in existing:assert existing[fid]["split"]==item["split"]
  existing[fid]=item
  for k in ("definition","masters","inputs","references","seeds"):hashes[item[k]]=sha(DATA/item[k])
  entries[fid]=dict(family=fid,loops=x["loops"],definition=m+"/definition.json",master_basis=m+"/masters.json",
    master_count=x["master_count"],manifest=r+"/manifest.json",records=r,references=r+"/references.jsonl.xz",
    traces=r+"/elimination_traces.jsonl.xz",targets_file=t+"/inputs.jsonl.xz",targets=x["counts"]["targets"],
    single_integral=x["counts"]["single_integral"],integral_expression=x["counts"]["integral_expression"],
    origin="analytic_coupled_vacuum_reverse_construction",split=x["split"])
 assert len(existing)==len(entries)==17100
 split["families"]=[existing[k] for k in sorted(existing)]
 split["higher_loop_policy"]="Fixed 70:30 mass-profile assignment shared across loop orders one through twelve; previous assignments preserved."
 write(MODEL/"split_manifest.json",split);write(MODEL/"source_hashes.json",hashes)
 # s05 checks all source hashes and creates separate directory views without copying originals.
 subprocess.run(["python3",str(DATA/"s05_prepare_model_splits.py")],check=True)
 split=read(MODEL/"split_manifest.json");counts={s:collections.Counter() for s in ("train","test")};byloops={}
 for meta in split["families"]:
  counts[meta["split"]].update(meta["counts"]);counts[meta["split"]]["families"]+=1
  byloops.setdefault(str(meta["loops"]),{s:dict(families=0,targets=0) for s in ("train","test")})
  byloops[str(meta["loops"])][meta["split"]]["families"]+=1
  byloops[str(meta["loops"])][meta["split"]]["targets"]+=meta["counts"]["targets"]
  entries[meta["family"]]["split"]=meta["split"];entries[meta["family"]]["loops"]=meta["loops"]
 catalog.update(families=[entries[k] for k in sorted(entries)],family_count=len(entries),
   master_records=sum(m["master_count"] for m in entries.values()),targets=sum(m["targets"] for m in entries.values()),
   single_integrals=sum(m["single_integral"] for m in entries.values()),integral_expressions=sum(m["integral_expression"] for m in entries.values()),
   split_counts={s:dict(c) for s,c in counts.items()},loop_counts=byloops,status="expanded_collection_independently_verified",
   topology_coverage="997 original one-loop families and 3 original two-loop families; 100 previously added profiles at orders 2..12, 250 earlier profiles and 1,000 new profiles at each order 1..12 in the restricted coupled vacuum domain.",
   counting_note="Master entries are family-local records. Mass profiles are family instances, not distinct graph topologies.",
   higher_loop_validation="higher_loops/validation.json",expansion_validation="expansion_1000/validation.json")
 write(DATA/"catalog.json",catalog)
 for kind in ("master_integrals","target_integrals","master_to_target"):
  write(DATA/kind/"catalog.json",{k:catalog[k] for k in ("families","family_count","master_records","targets","status","loop_counts")}|dict(path_base="integrals/"))
 definitions=[read(DATA/m["definition"]) for m in catalog["families"]]
 write(DATA/"families.json",dict(family_count=len(definitions),families=definitions))
 ids={s:[] for s in ("train","test")}
 for meta in split["families"]:ids[meta["split"]].extend(t["id"] for t in rows(DATA/meta["inputs"]))
 write(DATA/"splits.json",dict(train=ids["train"],test=ids["test"],validation=[],
    policy="Grouped 70:30 model split. Existing kinematic groups retained; each added mass profile stays in one split across all loop orders.",
    model_manifest="../ML_model_seed_selection/split_manifest.json"))
 audit=read(MODEL/"data_audit.json");audit.update(status="expanded_data_prepared",counts={s:dict(c) for s,c in counts.items()},
    total_targets=catalog["targets"],train_fraction=counts["train"]["targets"]/catalog["targets"],loop_counts=byloops,
    grouping=split["higher_loop_policy"],groups=len({m["group"] for m in split["families"]}),
    limitations=["New higher-loop coverage is a restricted coupled vacuum family, varied through mass profiles.",
     "Both splits contain all loop orders; these tests measure held-out profile performance, not transfer to unseen loop orders.",
     "Reference seeds and paths are sufficient; no global minimality claim.","Candidate pools have explicit finite bounds.",
     "Previously inspected held-out families remain the existing benchmark; new profile assignments were fixed before training."])
 audit["maxima"]["indices"]=16
 audit.pop("two_loop_grouping",None);write(MODEL/"data_audit.json",audit)
 summary=dict(status="integrated",families=catalog["family_count"],master_entries=catalog["master_records"],targets=catalog["targets"],
    counts={s:dict(c) for s,c in counts.items()},loop_counts=byloops,added_families=12000,added_targets=1536000,
    existing_split_preserved=True,profile_overlap=0,previous_test_visibility="Existing held-out benchmark was evaluated in prior project stages.")
 write(HERE/"integration_summary.json",summary)
 text=("# Integral collection\n\nThe collection contains "+str(catalog["family_count"])+" family instances, "+str(catalog["master_records"])+" family-local master entries and "+str(catalog["targets"])+" targets. It includes 2,247 one-loop families, 1,353 two-loop families and 1,350 families at each loop order from three through twelve.\n\n"+
  "master_integrals/ stores definitions and bases; target_integrals/ stores input targets; master_to_target/ stores exact master coefficients, IBP seeds, source identities, reverse constructions, elimination traces and operation counts. IDs join all three folders. training/ and testing/ are disjoint linked views; canonical data is stored once.\n\n"+
  "The latest 12,000 added families vary 1,000 new positive mass profiles across twelve loop orders, following the earlier additions of 1,100 and 3,000 families. Each is a restricted coupled vacuum integral. Massless powers equal one, and two to four distinct massive denominators share the sum of the loop momenta. Partial fractions and Euler IBP give an exact basis and reference reductions. These mass profiles share topology and do not establish coverage of general high-loop scattering families. See higher_loops/README.md and expansion_1000/README.md for equations, generation and checks.\n\n"+
  "Training contains "+str(counts["train"]["targets"])+" targets from "+str(counts["train"]["families"])+" families; testing contains "+str(counts["test"]["targets"])+" targets from "+str(counts["test"]["families"])+" families. Related mass profiles stay in one split across loop orders. Existing assignments are preserved. Paths in model_split_summary.json and the split manifests define the current assignment. Reference seed sets and paths are sufficient; no optimality claim is made.\n")
 (DATA/"README.md").write_text(text,encoding="utf-8")
 for kind in ("master_integrals","target_integrals","master_to_target"):
  (DATA/kind/"README.md").write_text("# "+kind.replace("_"," ").capitalize()+"\n\n"+text.split("\n\n",1)[1]+
    "\nEach family subfolder keeps its own definitions or records. catalog.json lists paths and counts. Higher-loop families contain a README describing their restricted domain; historical initial and expanded collections retain their original detailed records.\n",encoding="utf-8")
 p=HERE/"README.md";s=p.read_text(encoding="utf-8").replace("Generation in progress:","Generated and independently validated:").replace("Generated; independent validation pending:","Generated and independently validated:")
 s+="\ns03_validate.py checks graph loop counts, source integrands, all reverse and forward records at three finite-field samples, and convergent radial master quadratures. s04_run_validation.sh runs those checks on a compute node. s05_integrate.py extends catalogs and the grouped split after validation; it preserves existing assignments. integration_summary.json records final counts. The new phase uses "+str(counts["train"]["targets"])+" training targets and "+str(counts["test"]["targets"])+" held-out targets.\n"
 p.write_text(s,encoding="utf-8");print(json.dumps(summary),flush=True)
if __name__=="__main__":main()
