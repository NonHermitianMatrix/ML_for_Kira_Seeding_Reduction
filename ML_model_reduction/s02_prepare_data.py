"""Prepare only the existing training-family reduction states; replay every label."""
import argparse, collections, json, os, time, resource, concurrent.futures
import numpy as np
from s00_common import HERE,INTEGRALS,SPLIT,record_path,config,read,rows,sha,write_json,storage_guard,status
from s01_state import column,clean_row,eliminate,state_from_step,encode_state,feature_names

def prepare_family(meta,cfg,signature):
    family=meta["family"]
    base=INTEGRALS/"training/master_to_target/families"/family
    definition=INTEGRALS/meta["definition"];master_file=INTEGRALS/meta["masters"]
    sources=[definition,master_file,record_path(base/"identities.jsonl.gz"),record_path(base/"elimination_traces.jsonl.gz")]
    source_hashes={str(p.relative_to(INTEGRALS)):sha(p) for p in sources}
    output=HERE/"data/training"/(family+".npz");audit=output.with_suffix(".json")
    if output.exists() and audit.exists():
        saved=read(audit)
        if saved["preparation_signature"]==signature and saved["source_hashes"]==source_hashes and saved["sha256"]==sha(output):
            return saved
    f=read(definition);masters={column(x["indices"]) for x in read(master_file)["masters"]}
    traces=list(rows(base/"elimination_traces.jsonl.gz"))
    if len(traces)!=meta["counts"]["targets"]:raise ValueError("Trace/target count mismatch: "+family)
    ids=[t["id"] for t in traces]
    if len(ids)!=len(set(ids)) or any(not v.startswith(family+":") for v in ids):
        raise ValueError("Invalid target identifiers")
    required={eid for t in traces for step in t["steps"] for eid in step["allowed_pivot_equations"]}
    identities={}
    for row in rows(base/"identities.jsonl.gz"):
        if row["id"] in required:
            if row["id"] in identities:raise ValueError("Duplicate equation ID")
            identities[row["id"]]={"modular_terms":row["modular_terms"],"terms":row["terms"]}
    if set(identities)!=required:raise ValueError("Missing source identity")
    xs=[];offsets=[0];labels=[];target_number=[];step_number=[];action_ids=[]
    counts=collections.Counter();hist=collections.Counter()
    n=len(f["propagators"])
    for it,t in enumerate(traces):
        p=t["prime"];previous=None
        if t.get("sample")!=0:raise ValueError("Expected source identity sample 0")
        counts["targets"]+=1
        if not t["steps"]:counts["already_reduced_targets"]+=1
        ops=collections.Counter()
        for istep,step in enumerate(t["steps"]):
            state=state_from_step(step,identities,f,masters,p)
            x=encode_state(state,cfg)
            if previous is not None and clean_row(step["before"],p,n)!=previous:
                raise ValueError("Discontinuous trace: "+t["id"])
            choices=step["allowed_pivot_equations"]
            label=choices.index(step["pivot_equation"])
            src=clean_row(identities[step["pivot_equation"]]["modular_terms"],p,n)
            after,factor=eliminate(clean_row(step["before"],p,n),src,column(step["pivot_indices"]),p)
            if after!=clean_row(step["after"],p,n) or factor!=step["factor_mod_p"]:
                raise ValueError("Exact row replay failed: "+t["id"])
            # Stored support counts describe symbolic rows; specialization can remove terms.
            # Check the sampled rows exactly and retain/count the distinction without rewriting data.
            before=clean_row(step["before"],p,n)
            if len(after)>step["after_nonzeros"] or len(before)>step["before_nonzeros"]:
                raise ValueError("Sampled support exceeds the stored symbolic support")
            field_counts=(len(before),len(after),len(set(after)-set(before)),len(set(before)-set(after)))
            stored_counts=(step["before_nonzeros"],step["after_nonzeros"],step["fill_in"],step["cancelled_entries"])
            counts["symbolic_sample_support_count_differences"]+=int(field_counts!=stored_counts)
            # Recorded arithmetic counts use the original source term count.
            row_terms=len(identities[step["pivot_equation"]]["terms"])
            expected=dict(divisions=1,multiplications=row_terms,subtractions=row_terms)
            if expected!=step["operations"]:raise ValueError("Recorded operation count mismatch")
            counts["sampled_symbolic_support_differences"]+=int(row_terms!=len(src))
            ops.update(expected)
            previous=after
            xs.append(x);offsets.append(offsets[-1]+len(x));labels.append(label)
            target_number.append(it);step_number.append(istep);action_ids.extend(choices)
            counts["states"]+=1;counts["candidate_actions"]+=len(x)
            counts["choice_states" if len(x)>1 else "forced_states"]+=1;hist[len(x)]+=1
        final=clean_row(t["final_master_row"],p,n)
        if previous is not None and previous!=final:raise ValueError("Final row mismatch")
        if not set(final)<=masters:raise ValueError("Final row contains a nonmaster")
        if dict(ops)!=t["total_operations"] and any(ops[k]!=t["total_operations"].get(k,0) for k in ("divisions","multiplications","subtractions")):
            raise ValueError("Total operation count mismatch")
    dim=len(feature_names(cfg))
    features=np.concatenate(xs,axis=0) if xs else np.empty((0,dim),np.float32)
    if features.nbytes>268435456:raise RuntimeError("Family feature memory budget exceeded")
    output.parent.mkdir(parents=True,exist_ok=True)
    tmp=output.with_name(output.name+".part")
    with tmp.open("wb") as out:
        np.savez_compressed(out,features=features,offsets=np.asarray(offsets,np.int64),
                            labels=np.asarray(labels,np.int32),target_number=np.asarray(target_number,np.int32),
                            step_number=np.asarray(step_number,np.int32),target_ids=np.asarray(ids),
                            action_ids=np.asarray(action_ids))
    if tmp.stat().st_size>cfg["shard_limit_bytes"]:raise RuntimeError("Training shard exceeds size bound")
    os.replace(str(tmp),str(output))
    result=dict(family=family,loops=meta["loops"],group=meta["group"],counts=dict(counts),
                action_count_histogram=dict(sorted(hist.items())),max_actions=max(hist,default=0),
                feature_shape=list(features.shape),file=str(output.relative_to(HERE)),
                sha256=sha(output),bytes=output.stat().st_size,source_hashes=source_hashes,
                preparation_signature=signature)
    write_json(audit,result)
    return result

def worker_limit():
    soft,hard=resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS,(min(soft,768*1024**2) if soft>0 else 768*1024**2,hard))
def prepare_task(args):return prepare_family(*args)
def prepare_selected(selected,cfg,signature,workers):
    if workers==1:
        for meta in selected:yield prepare_family(meta,cfg,signature)
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers,initializer=worker_limit) as pool:
            yield from pool.map(prepare_task,((m,cfg,signature) for m in selected),chunksize=1)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--limit",type=int);args=ap.parse_args()
    evidence=read(HERE.parent/"integrals/expansion_1000/parallel_preparation_validation.json")
    if evidence["status"]!="passed" or not evidence["arrays_exactly_equal"]:raise RuntimeError("Parallel preparation check required")
    if evidence["preparer_sha256"]!=sha(HERE/"s02_prepare_data.py"):raise RuntimeError("Preparation source changed after check")
    cfg=config();storage=storage_guard(full=True);start=time.time()
    split=read(SPLIT);train=[m for m in split["families"] if m["split"]=="train"]
    test=[m for m in split["families"] if m["split"]=="test"]
    if {m["family"] for m in train}&{m["family"] for m in test}:raise ValueError("Family leakage")
    if {m["group"] for m in train}&{m["group"] for m in test}:raise ValueError("Group leakage")
    split_hash=sha(SPLIT)
    signature=dict(split_sha256=split_hash,config_sha256=sha(HERE/"config.json"),
                   encoder_sha256=sha(HERE/"s01_state.py"),preparer_sha256=sha(HERE/"s02_prepare_data.py"))
    selected=train[:args.limit] if args.limit else train
    completed=[];workers=min(cfg.get("training_cpu_threads",1),int(os.environ.get("NSLOTS","1")))
    for i,item in enumerate(prepare_selected(selected,cfg,signature,workers)):
        meta=selected[i];completed.append(item)
        if i%16==0 or i+1==len(selected):
            if i%64==0 or i+1==len(selected):storage_guard()
            status("preparing",families_completed=i+1,families_total=len(selected),elapsed_seconds=time.time()-start)
            print("prepared",i+1,len(selected),meta["family"],flush=True)
    counts=collections.Counter()
    for m in completed:counts.update(m["counts"])
    result=dict(schema_version=1,status="pilot" if args.limit else "complete",
                preparation_signature=signature,feature_names=feature_names(cfg),feature_dim=len(feature_names(cfg)),
                split_sha256=split_hash,train_families=len(train),held_out_families=len(test),
                held_out_targets=sum(m["counts"]["targets"] for m in test),
                held_out_family_ids=[m["family"] for m in test],held_out_data_read=False,
                counts=dict(counts),families=completed,source_project_bytes=storage,
                workers=workers,elapsed_seconds=time.time()-start,total_shard_bytes=sum(m["bytes"] for m in completed))
    if not args.limit and counts["targets"]!=sum(m["counts"]["targets"] for m in train):
        raise ValueError("Missing training targets")
    write_json(HERE/("data/pilot_manifest.json" if args.limit else "data/manifest.json"),result)
    print(json.dumps(dict(status=result["status"],counts=dict(counts),bytes=result["total_shard_bytes"])),flush=True)
if __name__=="__main__":main()
