"""Evaluate the frozen trained model on every held-out target and save reproducible predictions."""
import collections,datetime,gzip,hashlib,json,os,pathlib,resource,subprocess,sys,time
import numpy as np
import torch
HERE=pathlib.Path(__file__).resolve().parent
MODEL=HERE.parent
sys.path.insert(0,str(MODEL))
from s01_data import DATA,encode,encode_shared,family_records,read,storage_guard,verify_sources
from s04_predict import load_model
from s02_model import reference_loss
from s00_metrics import Aggregate,Curves,micro_metrics,self_check,target_metrics
def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):h.update(block)
    return h.hexdigest()
def write_json(path,data):
    temp=path.with_name(path.name+".part")
    temp.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    os.replace(str(temp),str(path))
def main():
    started=time.monotonic()
    HERE.mkdir(exist_ok=True);(HERE/"predictions").mkdir(exist_ok=True)
    check=self_check();write_json(HERE/"metric_checks.json",check)
    checkpoint=MODEL/"trained_model.pt";model_hash=sha(checkpoint)
    trained=read(MODEL/"trained_model.json")
    assert model_hash==trained["model_sha256"]
    model,cfg,saved=load_model(checkpoint)
    assert saved["epoch"]==10 and saved["test_targets_processed"]==0
    state_before={k:v.detach().clone() for k,v in model.state_dict().items()}
    split_hash=verify_sources(split="test")
    manifest=read(MODEL/"split_manifest.json")
    test=[m for m in manifest["families"] if m["split"]=="test"]
    train=[m for m in manifest["families"] if m["split"]=="train"]
    assert not {m["family"] for m in test}&{m["family"] for m in train}
    assert not {m["group"] for m in test}&{m["group"] for m in train}
    assert len(test)==307 and sum(m["counts"]["targets"] for m in test)==72142
    initial_bytes=storage_guard()
    overall=Aggregate();groups=collections.defaultdict(Aggregate);families={};curves=Curves()
    inference_time=0.;encoding_time=0.;outputs=[]
    per_target_temp=HERE/"per_target_metrics.jsonl.gz.part"
    def status(done_families,finished=False):
        data=dict(status="completed" if finished else "testing",targets_processed=overall.targets,
                  targets_total=72142,families_processed=done_families,families_total=307,
                  elapsed_seconds=time.monotonic()-started,optimizer_updates=0,
                  threshold=0.5,model_sha256=model_hash,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        write_json(HERE/"test_status.json",data);print(json.dumps(data),flush=True)
    status(0)
    with gzip.open(str(per_target_temp),"wt",encoding="utf-8",compresslevel=6) as records,torch.inference_mode():
        for number,meta in enumerate(test,1):
            fid=meta["family"];archive=HERE/"predictions"/(fid+".npz")
            family_aggregate=Aggregate();family_started=time.monotonic()
            if archive.exists():
                with np.load(str(archive),allow_pickle=False) as data:
                    assert str(data["model_sha256"])==model_hash and str(data["split_sha256"])==split_hash
                    probabilities=data["probabilities"];labels=data["labels"];seeds=data["seeds"]
                    ids=data["target_ids"];kinds=data["target_kinds"];losses=data["binary_cross_entropy"]
                    encoding_seconds=data["encoding_seconds"];inference_seconds=data["inference_seconds"]
                assert len(ids)==meta["counts"]["targets"]
            else:
                n=meta["counts"]["targets"]
                nc=len(read(DATA/meta["seeds"])["indices"])
                assert n*nc*5<128*1024**2
                probabilities=np.empty((n,nc),np.float32);labels=np.empty((n,nc),np.uint8)
                losses=np.empty(n,np.float64);encoding_seconds=np.empty(n);inference_seconds=np.empty(n)
                ids=[];kinds=[];shared=None
                for index,(target,family,candidates,y) in enumerate(family_records(meta,cfg)):
                    assert index<n and target["family"]==fid
                    t=time.perf_counter()
                    if shared is None:shared=encode_shared(family,candidates,cfg)
                    x=encode(target,family,candidates,cfg,shared=shared)
                    encoding_seconds[index]=time.perf_counter()-t
                    t=time.perf_counter();logits=model(x);p=logits.sigmoid()
                    inference_seconds[index]=time.perf_counter()-t
                    assert torch.isfinite(logits).all()
                    losses[index]=float(reference_loss(logits,y))
                    probabilities[index]=p.numpy();labels[index]=y.numpy().astype(np.uint8)
                    ids.append(target["id"]);kinds.append(target["kind"])
                assert len(ids)==n and len(set(ids))==n
                seeds=np.asarray(candidates,np.int64);ids=np.asarray(ids);kinds=np.asarray(kinds)
                temp=archive.with_name(archive.name+".part")
                with temp.open("wb") as f:
                    np.savez_compressed(f,probabilities=probabilities,labels=labels,seeds=seeds,
                        target_ids=ids,target_kinds=kinds,binary_cross_entropy=losses,
                        encoding_seconds=encoding_seconds,inference_seconds=inference_seconds,
                        model_sha256=np.asarray(model_hash),split_sha256=np.asarray(split_hash))
                assert temp.stat().st_size<64*1024**2
                os.replace(str(temp),str(archive))
            assert probabilities.shape==labels.shape and len(ids)==len(probabilities)
            assert int(labels.sum())==meta["counts"]["positive_seed_labels"]
            assert labels.size==meta["counts"]["candidate_seed_labels"]
            for i,identifier in enumerate(ids):
                p=probabilities[i];y=labels[i]
                values=target_metrics(p,y,seeds)
                values["binary_cross_entropy"]=float(losses[i])
                values["encoding_seconds"]=float(encoding_seconds[i])
                values["inference_seconds"]=float(inference_seconds[i])
                for aggregate in (overall,family_aggregate,groups["kind:"+str(kinds[i])],groups["loops:"+str(meta["loops"])]):
                    aggregate.add(values)
                curves.add(p,y)
                records.write(json.dumps(dict(target=str(identifier),family=fid,kind=str(kinds[i]),loops=meta["loops"],**values),allow_nan=False)+"\n")
            inference_time+=float(inference_seconds.sum());encoding_time+=float(encoding_seconds.sum())
            families[fid]=dict(loops=meta["loops"],group=meta["group"],**family_aggregate.result())
            outputs.append(dict(family=fid,path=str(archive.relative_to(HERE)),bytes=archive.stat().st_size,
                                sha256=sha(archive),targets=len(ids),candidates=probabilities.shape[1]))
            if number%10==0 or number==len(test):
                status(number)
                if sum(p["bytes"] for p in outputs)>700000000:raise RuntimeError("Prediction archive size exceeded 700 MB budget")
    os.replace(str(per_target_temp),str(HERE/"per_target_metrics.jsonl.gz"))
    result=overall.result()
    assert result["targets"]==72142 and result["candidate_labels"]==33828275 and result["positive_labels"]==201885
    assert result["empty_reference_targets"]==2
    assert sha(checkpoint)==model_hash
    assert all(torch.equal(state_before[k],v) for k,v in model.state_dict().items())
    family_keys=sorted({k for f in families.values() for k in f["target_macro"]})
    family_macro={k:float(np.mean([f["target_macro"][k] for f in families.values() if k in f["target_macro"]])) for k in family_keys}
    family_denominators={k:sum(k in f["target_macro"] for f in families.values()) for k in family_keys}
    total=result["candidate_labels"];positive=result["positive_labels"]
    summary=dict(status="completed",threshold=0.5,checkpoint_sha256=model_hash,split_sha256=split_hash,
                 overall=result,groups={k:v.result() for k,v in groups.items()},family_macro=family_macro,
                 family_macro_denominators=family_denominators,
                 baseline_all_zero=dict(micro=micro_metrics(total-positive,0,positive,0),
                    exact_reference_set_fraction=2/72142,positive_prevalence=positive/total),
                 elapsed_seconds=time.monotonic()-started,encoding_seconds=encoding_time,
                 model_inference_seconds=inference_time,optimizer_updates=0,
                 model_unchanged=True,initial_project_bytes=initial_bytes,final_project_bytes=storage_guard(),
                 max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 git_commit=subprocess.check_output(["git","rev-parse","HEAD"],universal_newlines=True).strip(),
                 testing_code_sha256={p.name:sha(p) for p in (HERE/"s00_metrics.py",pathlib.Path(__file__))},
                 finished_at_utc=datetime.datetime.utcnow().isoformat()+"Z",
                 software=dict(python=sys.version.split()[0],torch=torch.__version__,numpy=np.__version__),
                 interpretation="Agreement with recorded sufficient seed sets. This evaluation does not run Kira or establish minimal seed sets, reduction success or solver speedup.")
    write_json(HERE/"test_results.json",summary);write_json(HERE/"family_metrics.json",families)
    write_json(HERE/"curves.json",curves.result());write_json(HERE/"prediction_manifest.json",dict(model_sha256=model_hash,split_sha256=split_hash,families=outputs))
    status(len(test),True)
    print(json.dumps(dict(micro=result["micro"],target_macro=result["target_macro"])),flush=True)
if __name__=="__main__":
    try:main()
    except BaseException as error:
        write_json(HERE/"interruption.json",dict(type=type(error).__name__,message=str(error)))
        raise
