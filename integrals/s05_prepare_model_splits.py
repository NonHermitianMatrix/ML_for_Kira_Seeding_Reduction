#!/usr/bin/env python3
"""Create non-overlapping train/test directory views without copying integral data."""
import collections,hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MODEL=ROOT.parent/"ML_model_seed_selection"
KINDS=("master_integrals","target_integrals","master_to_target")
NAMES={"train":"training","test":"testing"}
PATH_KEYS=("definition","masters","inputs","references","seeds")

def read(path): return json.loads(path.read_text(encoding="utf-8"))
def write(path,obj): path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def original(path):
    parts=Path(path).parts
    if parts[0] in NAMES.values(): parts=parts[1:]
    return str(Path(*parts))

def main():
    manifest=read(MODEL/"split_manifest.json")
    hashes=read(MODEL/"source_hashes.json")
    canonical_hashes={original(k):v for k,v in hashes.items()}
    seen,groups=set(),{}
    totals={s:collections.Counter() for s in NAMES}
    split_rows={s:[] for s in NAMES}
    views=0
    for row in manifest["families"]:
        family,split=row["family"],row["split"]
        assert family not in seen
        seen.add(family)
        assert groups.setdefault(row["group"],split)==split
        base=ROOT/NAMES[split]
        for kind in KINDS:
            target=ROOT/kind/"families"/family
            assert target.is_dir()
            link=base/kind/"families"/family
            link.parent.mkdir(parents=True,exist_ok=True)
            relative=os.path.relpath(str(target),str(link.parent))
            if link.is_symlink():
                assert os.readlink(str(link))==relative
            else:
                assert not link.exists()
                link.symlink_to(relative,target_is_directory=True)
            assert link.resolve()==target.resolve()
            views+=1
        for key in PATH_KEYS:
            old=original(row[key])
            assert Path(old).parts[2]==family
            row[key]=NAMES[split]+"/"+old
            h=hashlib.sha256()
            with (ROOT/row[key]).open("rb") as stream:
                for b in iter(lambda:stream.read(1048576),b""):h.update(b)
            assert h.hexdigest()==canonical_hashes[old],row[key]
        totals[split].update(row["counts"]);totals[split]["families"]+=1
        split_rows[split].append(row)
    assert sum(v["targets"] for v in totals.values())==sum(m["counts"]["targets"] for m in manifest["families"])
    for split,name in NAMES.items():
        for kind in KINDS:
            got={p.name for p in (ROOT/name/kind/"families").iterdir()}
            expected={r["family"] for r in split_rows[split]}
            assert got==expected
        write(ROOT/name/"manifest.json",dict(split=split,path_base="integrals/",
              counts=dict(totals[split]),families=split_rows[split]))
        text=("# "+name.capitalize()+" integrals\n\n"+
              "This folder contains "+str(totals[split]["targets"])+" targets from "+
              str(totals[split]["families"])+" complete families in the seed model's "+split+" split.\n\n"+
              "The master_integrals/, target_integrals/ and master_to_target/ folders contain relative directory links to the existing family files. These links form a separate, non-overlapping view; each integral file remains stored once. Each family belongs to exactly one model split. Full box kinematic profiles remain together across mass assignments. Added vacuum mass profiles stay together across loop orders.\n\n"+
              "manifest.json lists the family records and paths, relative to integrals/. Stored records retain their original canonical file links and historical split labels. This manifest and the model's split_manifest.json define the current 70:30 model division.\n\n"+
              ("The training program reads only this split. The frozen expanded-data models will be evaluated on the separate testing split.\n" if split=="train" else
               "These targets are reserved for frozen-model testing. Training does not read these examples or update parameters from them.\n"))
        (ROOT/name/"README.md").write_text(text,encoding="utf-8")
        for kind in KINDS:
            (ROOT/name/kind/"README.md").write_text(
                "# "+kind.replace("_"," ").capitalize()+" for "+name+"\n\n"+
                "families/ contains links for the "+str(totals[split]["families"])+" families in this split. "+
                "See [the split README](../README.md) and [the canonical data README](../../"+kind+"/README.md).\n",
                encoding="utf-8")
    manifest["directory_views"]={s:NAMES[s]+"/" for s in NAMES}
    write(MODEL/"split_manifest.json",manifest)
    updated={row[key]:canonical_hashes[original(row[key])] for row in manifest["families"] for key in PATH_KEYS}
    write(MODEL/"source_hashes.json",updated)
    summary=dict(status="separated_and_hash_verified",family_overlap=0,kinematic_group_overlap=0,
                 links=views,copied_integral_files=0,counts={k:dict(v) for k,v in totals.items()},
                 model_testing_performed=False)
    write(ROOT/"model_split_summary.json",summary)
    print(json.dumps(summary),flush=True)
if __name__=="__main__":main()
