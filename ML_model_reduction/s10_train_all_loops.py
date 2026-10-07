"""Warm-start the saved reduction model and optimizer for twenty expanded-data passes."""
import argparse, math, random, resource, time, os
import numpy as np
import torch
from torch.nn import functional as F
from s00_common import HERE,config,read,sha,write_json,atomic_torch,storage_guard,status,SPLIT
from s03_model import ReductionSelector

def batches(shards,indices,cfg):
    pending=[];maximum=0
    for fi,si in indices:
        z=shards[fi];n=int(z["offsets"][si+1]-z["offsets"][si])
        newmax=max(maximum,n)
        if pending and (len(pending)>=cfg["batch_states"] or newmax*(len(pending)+1)>cfg["max_padded_actions"]):
            yield collate(shards,pending,maximum)
            pending=[];maximum=0
        if n>cfg["max_padded_actions"]:raise ValueError("Action list exceeds batch budget")
        pending.append((fi,si));maximum=max(maximum,n)
    if pending:yield collate(shards,pending,maximum)

def collate(shards,items,maximum):
    dim=shards[items[0][0]]["features"].shape[1]
    x=np.zeros((len(items),maximum,dim),np.float32);mask=np.zeros((len(items),maximum),bool)
    y=np.empty(len(items),np.int64)
    for b,(fi,si) in enumerate(items):
        z=shards[fi];lo,hi=z["offsets"][si:si+2];n=hi-lo
        x[b,:n]=z["features"][lo:hi];mask[b,:n]=True;y[b]=z["labels"][si]
    return torch.from_numpy(x),torch.from_numpy(mask),torch.from_numpy(y)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--resume",action="store_true");args=ap.parse_args()
    cfg=config();training_threads=cfg.get("training_cpu_threads",cfg["cpu_threads"])
    if int(os.environ.get("NSLOTS","1"))<training_threads:raise RuntimeError("Insufficient allocated CPU slots")
    torch.set_num_threads(training_threads);torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True);torch.manual_seed(cfg["seed"])
    manifest=read(HERE/"data/manifest.json")
    if manifest["status"]!="complete":raise ValueError("Complete data preparation required")
    if manifest["split_sha256"]!=sha(SPLIT):raise ValueError("Split changed")
    if manifest["preparation_signature"]["config_sha256"]!=sha(HERE/"config.json"):raise ValueError("Configuration changed")
    if manifest["preparation_signature"]["encoder_sha256"]!=sha(HERE/"s01_state.py"):raise ValueError("Encoder changed")
    fingerprint=dict(manifest_sha256=sha(HERE/"data/manifest.json"),config_sha256=sha(HERE/"config.json"),
                     model_code_sha256=sha(HERE/"s03_model.py"),trainer_sha256=sha(HERE/"s10_train_all_loops.py"))
    model=ReductionSelector(manifest["feature_dim"],cfg)
    optimizer=torch.optim.AdamW(model.parameters(),lr=cfg["learning_rate"],weight_decay=cfg["weight_decay"])
    latest=HERE/"runs/all_loops_latest.pt";epoch=0;group_start=0;history=[];updates=0;elapsed_previous=0
    partial=dict(loss_sum=0.0,correct=0,states=0,batches=0)
    if args.resume and latest.exists():
        saved=torch.load(latest,map_location="cpu",weights_only=False)
        if saved["fingerprint"]!=fingerprint:raise ValueError("Checkpoint provenance mismatch")
        model.load_state_dict(saved["model"]);optimizer.load_state_dict(saved["optimizer"])
        epoch=saved["epoch"];group_start=saved["next_group"];history=saved["history"]
        partial=saved["partial"];updates=saved["updates"];elapsed_previous=saved["elapsed_seconds"]
        torch.set_rng_state(saved["torch_rng"])
    elif latest.exists():raise RuntimeError("Checkpoint exists; use --resume")
    warm=HERE/"runs/before_expansion_250/runs/all_loops_latest.pt"
    initial=torch.load(warm,map_location="cpu",weights_only=False)
    lineage=dict(checkpoint=str(warm.relative_to(HERE)),sha256=sha(warm),
                 previous_dataset_epochs=initial["epoch"],expanded_dataset_epochs=cfg["epochs"],
                 previous_optimizer_updates=initial["updates"],prior_lineage=initial.get("lineage",{}))
    if not latest.exists():
        model.load_state_dict(initial["model"]);optimizer.load_state_dict(initial["optimizer"])
    started=time.time()
    def elapsed():return elapsed_previous+time.time()-started
    def save(ep,group,acc):
        atomic_torch(latest,dict(schema_version=1,model=model.state_dict(),optimizer=optimizer.state_dict(),
          epoch=ep,next_group=group,history=history,partial=acc,updates=updates,
          elapsed_seconds=elapsed(),fingerprint=fingerprint,lineage=lineage,torch_rng=torch.get_rng_state()))
    storage_guard(full=True)
    for ep in range(epoch,cfg["epochs"]):
        order=list(range(len(manifest["families"])))
        random.Random(cfg["seed"]+ep).shuffle(order)
        groups=[order[i:i+cfg["families_per_group"]] for i in range(0,len(order),cfg["families_per_group"])]
        if ep!=epoch:group_start=0;partial=dict(loss_sum=0.0,correct=0,states=0,batches=0)
        for gi in range(group_start,len(groups)):
            shards=[]
            for idx in groups[gi]:
                item=manifest["families"][idx];path=HERE/item["file"]
                if sha(path)!=item["sha256"]:raise ValueError("Training shard changed")
                with np.load(path,allow_pickle=False) as z:
                    shards.append({k:z[k] for k in ("features","offsets","labels")})
            items=[(fi,si) for fi,z in enumerate(shards) for si in range(len(z["labels"]))
                   if z["offsets"][si+1]-z["offsets"][si]>1]
            random.Random(cfg["seed"]+ep*100003+gi).shuffle(items)
            model.train()
            for x,mask,y in batches(shards,items,cfg):
                optimizer.zero_grad(set_to_none=True)
                logits=model(x,mask);loss=F.cross_entropy(logits,y)
                if not torch.isfinite(loss):raise RuntimeError("Non-finite training loss")
                loss.backward()
                norm=torch.nn.utils.clip_grad_norm_(model.parameters(),cfg["max_grad_norm"],error_if_nonfinite=True)
                optimizer.step()
                b=len(y);partial["loss_sum"]+=loss.item()*b;partial["states"]+=b
                partial["correct"]+=int((logits.argmax(-1)==y).sum())
                partial["batches"]+=1;updates+=1
            del shards,items
            save(ep,gi+1,partial)
            status("training",epoch=ep+1,epochs=cfg["epochs"],groups_completed=gi+1,groups_total=len(groups),
                   choice_states_seen_this_epoch=partial["states"],updates=updates,elapsed_seconds=elapsed(),
                   mean_loss=partial["loss_sum"]/max(1,partial["states"]),
                   max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            if gi%64==0:storage_guard()
        if partial["states"]!=manifest["counts"]["choice_states"]:raise ValueError("Epoch coverage mismatch")
        metric=dict(epoch=ep+1,choice_states=partial["states"],mean_cross_entropy=partial["loss_sum"]/partial["states"],
                    reference_top1=partial["correct"]/partial["states"],updates=partial["batches"],
                    cumulative_seconds=elapsed())
        history.append(metric);write_json(HERE/"runs/all_loops_history.json",history);print(metric,flush=True)
        partial=dict(loss_sum=0.0,correct=0,states=0,batches=0);group_start=0
        save(ep+1,0,partial)
    model.eval()
    payload=dict(schema_version=1,model=model.state_dict(),config=cfg,feature_dim=manifest["feature_dim"],
                 feature_names=manifest["feature_names"],fingerprint=fingerprint,lineage=lineage,
                 confidence_meaning="uncalibrated probability of the recorded next choice among supplied actions")
    atomic_torch(HERE/"trained_model.pt",payload)
    result=dict(status="trained_testing_deferred",epochs_completed=cfg["epochs"],lineage=lineage,parameter_count=sum(p.numel() for p in model.parameters()),
                training_cpu_threads=training_threads,inference_cpu_threads=cfg["cpu_threads"],
                choice_state_presentations=sum(h["choice_states"] for h in history),optimizer_updates=updates,
                counts=manifest["counts"],train_families=manifest["train_families"],
                held_out_families=manifest["held_out_families"],held_out_targets=manifest["held_out_targets"],
                history=history,elapsed_seconds=elapsed(),max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                model_sha256=sha(HERE/"trained_model.pt"),model_bytes=(HERE/"trained_model.pt").stat().st_size,
                fingerprint=fingerprint,test_data_used=False,calibration_performed=False,optimality_established=False,
                full_kira_integration=False)
    write_json(HERE/"trained_model.json",result)
    status("complete",**{k:v for k,v in result.items() if k not in ("status","history","fingerprint")})
    print("Training complete",result["model_sha256"],flush=True)
if __name__=="__main__":main()
