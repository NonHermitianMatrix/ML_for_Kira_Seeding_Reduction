"""Continue the published reduction weights and optimizer for twenty epochs."""
import fcntl,pathlib,sys
WORK=pathlib.Path(__file__).resolve().parent
MODEL=WORK.parents[1]
sys.path.insert(0,str(MODEL))
import argparse, math, random, resource, time
import numpy as np
import torch
from torch.nn import functional as F
from s00_common import HERE,config,read,sha,write_json,atomic_torch,storage_guard,status,SPLIT
from s03_model import ReductionSelector

from s04_train import batches

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--resume",action="store_true");ap.add_argument("--epochs",type=int,default=30);args=ap.parse_args()
    lock=(WORK/"run.lock").open("w")
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    plan=read(WORK/"request.json")
    assert args.resume and args.epochs==plan["target_epochs"]==plan["initial_epochs"]+plan["additional_epochs"]==30
    cfg=config()
    assert cfg==plan["base_config"] and sha(SPLIT)==plan["split_sha256"]
    for relative,digest in plan["snapshots"].items():assert sha(HERE/"runs/epochs_10_snapshot"/relative)==digest
    cfg=dict(cfg,epochs=args.epochs)
    torch.set_num_threads(cfg["cpu_threads"]);torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True);torch.manual_seed(cfg["seed"])
    manifest=read(HERE/"data/manifest.json")
    if manifest["status"]!="complete":raise ValueError("Complete data preparation required")
    if manifest["split_sha256"]!=sha(SPLIT):raise ValueError("Split changed")
    if manifest["preparation_signature"]["config_sha256"]!=sha(HERE/"config.json"):raise ValueError("Configuration changed")
    if manifest["preparation_signature"]["encoder_sha256"]!=sha(HERE/"s01_state.py"):raise ValueError("Encoder changed")
    fingerprint=dict(manifest_sha256=sha(HERE/"data/manifest.json"),config_sha256=sha(HERE/"config.json"),
                     model_code_sha256=sha(HERE/"s03_model.py"),trainer_sha256=sha(HERE/"s04_train.py"))
    parent_fingerprint=dict(fingerprint)
    assert parent_fingerprint==plan["base_metadata"]["fingerprint"]
    fingerprint.update(continuation_trainer_sha256=sha(__file__),request_sha256=sha(WORK/"request.json"),effective_epochs=cfg["epochs"])
    model=ReductionSelector(manifest["feature_dim"],cfg)
    optimizer=torch.optim.AdamW(model.parameters(),lr=cfg["learning_rate"],weight_decay=cfg["weight_decay"])
    latest=HERE/"runs/latest.pt";epoch=0;group_start=0;history=[];updates=0;elapsed_previous=0
    partial=dict(loss_sum=0.0,correct=0,states=0,batches=0)
    if args.resume and latest.exists():
        saved=torch.load(latest,map_location="cpu",weights_only=False)
        if saved["fingerprint"]!=fingerprint:
            assert saved["fingerprint"]==parent_fingerprint,"Checkpoint provenance mismatch"
            assert sha(latest)==plan["initial_checkpoint_sha256"]
            assert saved["epoch"]==plan["initial_epochs"] and saved["next_group"]==0
            published=torch.load(HERE/"runs/epochs_10_snapshot/trained_model.pt",map_location="cpu",weights_only=False)
            assert all(torch.equal(t,published["model"][k]) for k,t in saved["model"].items())
        assert saved["optimizer"]["state"],"Optimizer state missing"
        assert plan["initial_epochs"]<=saved["epoch"]<=cfg["epochs"]
        model.load_state_dict(saved["model"]);optimizer.load_state_dict(saved["optimizer"])
        epoch=saved["epoch"];group_start=saved["next_group"];history=saved["history"]
        partial=saved["partial"];updates=saved["updates"];elapsed_previous=saved["elapsed_seconds"]
        torch.set_rng_state(saved["torch_rng"])
    else:raise RuntimeError("A saved optimizer checkpoint and --resume are required")
    if not (WORK/"preflight.json").exists():
        write_json(WORK/"preflight.json",dict(status="passed",resumed_epoch=epoch,next_group=group_start,
          optimizer_updates=updates,initial_model_sha256=plan["initial_model_sha256"],
          initial_checkpoint_sha256=plan["initial_checkpoint_sha256"],optimizer_state_preserved=True,
          data_preparation_unchanged=True,training_split_unchanged=True,target_epochs=cfg["epochs"],
          runner_sha256=sha(__file__),github_publication=False))
    started=time.time()
    def elapsed():return elapsed_previous+time.time()-started
    def save(ep,group,acc):
        atomic_torch(latest,dict(schema_version=1,model=model.state_dict(),optimizer=optimizer.state_dict(),
          epoch=ep,next_group=group,history=history,partial=acc,updates=updates,
          elapsed_seconds=elapsed(),fingerprint=fingerprint,torch_rng=torch.get_rng_state()))
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
            if gi%8==0:storage_guard()
        if partial["states"]!=manifest["counts"]["choice_states"]:raise ValueError("Epoch coverage mismatch")
        metric=dict(epoch=ep+1,choice_states=partial["states"],mean_cross_entropy=partial["loss_sum"]/partial["states"],
                    reference_top1=partial["correct"]/partial["states"],updates=partial["batches"],
                    cumulative_seconds=elapsed())
        history.append(metric);write_json(HERE/"runs/history.json",history);print(metric,flush=True)
        partial=dict(loss_sum=0.0,correct=0,states=0,batches=0);group_start=0
        save(ep+1,0,partial)
    assert len(history)==cfg["epochs"]==30
    assert history[:plan["initial_epochs"]]==plan["base_metadata"]["history"]
    assert [h["epoch"] for h in history]==list(range(1,cfg["epochs"]+1))
    assert all(h["choice_states"]==manifest["counts"]["choice_states"] for h in history)
    assert all(torch.isfinite(t).all() for t in model.state_dict().values())
    model.eval()
    payload=dict(schema_version=1,model=model.state_dict(),config=cfg,feature_dim=manifest["feature_dim"],
                 feature_names=manifest["feature_names"],fingerprint=fingerprint,
                 confidence_meaning="uncalibrated probability of the recorded next choice among supplied actions")
    atomic_torch(HERE/"trained_model.pt",payload)
    result=dict(status="trained_testing_deferred",epochs_completed=cfg["epochs"],parameter_count=sum(p.numel() for p in model.parameters()),
                choice_state_presentations=sum(h["choice_states"] for h in history),optimizer_updates=updates,
                counts=manifest["counts"],train_families=manifest["train_families"],
                held_out_families=manifest["held_out_families"],held_out_targets=manifest["held_out_targets"],
                history=history,elapsed_seconds=elapsed(),max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                model_sha256=sha(HERE/"trained_model.pt"),model_bytes=(HERE/"trained_model.pt").stat().st_size,
                fingerprint=fingerprint,test_data_used=False,calibration_performed=False,optimality_established=False,
                full_kira_integration=False)
    result["continuation"]=dict(initial_epochs=plan["initial_epochs"],additional_epochs=plan["additional_epochs"],
          initial_model_sha256=plan["initial_model_sha256"],base_commit=plan["base_commit"],
          runner_sha256=sha(__file__),request_sha256=sha(WORK/"request.json"),optimizer_state_preserved=True,
          published=False,previous_test_model="runs/epochs_10_snapshot/trained_model.pt")
    write_json(HERE/"trained_model.json",result)
    write_json(WORK/"status.json",dict(stage="complete",epochs_completed=cfg["epochs"],
        additional_epochs_completed=plan["additional_epochs"],model_sha256=result["model_sha256"],
        optimizer_updates=updates,testing_performed=False,github_publication=False))
    text=(HERE/"README.md").read_text(encoding="utf-8")
    text=text.replace("Continuation requested: twenty additional epochs, from ten to thirty total.",
                      "Continuation completed: twenty additional epochs, from ten to thirty total.")
    (HERE/"README.md").write_text(text,encoding="utf-8")
    (HERE/"runs/README.md").write_text(
        "# Reduction-model training run\n\nTraining completed thirty epochs on the existing training states. "
        "The additional twenty epochs continued both weights and optimizer from epochs_10_snapshot/. "
        "latest.pt retains the current optimizer, history.json contains all thirty epochs, and status.json gives progress. "
        "extra_20_epochs/ records the cluster-only continuation. Existing test results and the report describe the archived "
        "ten-epoch model. The continued model has not been tested or published to GitHub.\n",encoding="utf-8")
    status("complete",**{k:v for k,v in result.items() if k not in ("status","history","fingerprint")})
    print("Training complete",result["model_sha256"],flush=True)
if __name__=="__main__":
    try:main()
    except BaseException as e:
        write_json(WORK/"status.json",dict(stage="interrupted",type=type(e).__name__,message=str(e),
                                          checkpoint="../latest.pt",github_publication=False))
        raise
