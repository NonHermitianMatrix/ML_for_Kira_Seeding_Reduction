"""Train the seed model on the training split only; save resumable and final weights here."""
import argparse,hashlib,json,os,pathlib,subprocess,time
import torch
from s01_data import HERE,config,examples,read,storage_guard,verify_sources
from s02_model import SeedSelector,reference_loss

def atomic_json(path,value):
    temp=path.with_name(path.name+".part")
    temp.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    os.replace(str(temp),str(path))

def train(epochs=None,resume=False):
    cfg=config()
    if epochs is not None:cfg["epochs"]=epochs
    if not 1<=cfg["epochs"]<=100:raise ValueError("Epoch count must be within 1..100")
    torch.set_num_threads(cfg["cpu_threads"]);torch.manual_seed(cfg["split_seed"])
    storage_guard()
    manifest_hash=verify_sources(split="train")
    manifest=read(HERE/"split_manifest.json")
    selected=[m for m in manifest["families"] if m["split"]=="train"]
    expected_targets=sum(m["counts"]["targets"] for m in selected)
    assert expected_targets==168330 and len(selected)==693
    model=SeedSelector(cfg)
    optimizer=torch.optim.AdamW(model.parameters(),lr=cfg["learning_rate"],weight_decay=cfg["weight_decay"])
    out=HERE/"runs";out.mkdir(exist_ok=True)
    checkpoint=out/"latest.pt"
    steps,seen,start_epoch,skip,partial_loss=0,0,0,0,0.0
    previous_elapsed=0.0;history=[]
    source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=str(HERE),universal_newlines=True).strip()
    source_files={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in HERE.glob("*.py")}
    if checkpoint.exists():
        if not resume:raise FileExistsError("Use --resume to continue the existing run")
        saved=torch.load(str(checkpoint),map_location="cpu")
        if saved["manifest_sha256"]!=manifest_hash:raise ValueError("Checkpoint split changed")
        if any(saved["config"][k]!=v for k,v in cfg.items() if k!="epochs"):
            raise ValueError("Checkpoint configuration differs")
        if saved["source_files"]!=source_files:raise ValueError("Training source code changed")
        model.load_state_dict(saved["model"]);optimizer.load_state_dict(saved["optimizer"])
        steps,seen,start_epoch=saved["optimizer_steps"],saved["trained_targets"],saved["epoch"]
        skip=saved["processed_in_epoch"];partial_loss=saved["epoch_loss_sum"]
        previous_elapsed=saved["elapsed_seconds"];history=saved["history"]
        source_commit=saved["source_commit"]
    elif resume:raise FileNotFoundError(checkpoint)
    if start_epoch>=cfg["epochs"]:raise ValueError("Requested epochs already completed")
    started=time.monotonic()
    def elapsed():return previous_elapsed+time.monotonic()-started
    def status(completed,n,loss,finished=False):
        row=dict(status="trained" if finished else "training",completed_epochs=completed,
                 configured_epochs=cfg["epochs"],targets_in_current_epoch=n,
                 training_targets_per_epoch=expected_targets,training_families=len(selected),
                 targets_processed=seen,optimizer_steps=steps,elapsed_seconds=elapsed(),
                 mean_training_loss=loss/n if n else (history[-1]["mean_loss"] if history else None),
                 test_targets_processed=0,testing_performed=False,
                 checkpoint="ML_model_seed_selection/runs/latest.pt",
                 final_model="ML_model_seed_selection/trained_model.pt" if finished else None)
        atomic_json(out/"training_status.json",row)
        return row
    def save(completed,n,loss,finished=False):
        payload=dict(schema_version=2,status="trained" if finished else "training",config=cfg,
                     model=model.state_dict(),optimizer=optimizer.state_dict(),optimizer_steps=steps,
                     epoch=completed,processed_in_epoch=n,epoch_loss_sum=loss,
                     manifest_sha256=manifest_hash,trained_targets=seen,history=history,
                     elapsed_seconds=elapsed(),source_commit=source_commit,source_files=source_files,
                     training_families=[m["family"] for m in selected],test_targets_processed=0)
        temp=checkpoint.with_name("latest.pt.part")
        torch.save(payload,str(temp))
        if temp.stat().st_size>cfg["checkpoint_limit_bytes"]:
            temp.unlink();raise RuntimeError("Checkpoint exceeds its size limit")
        os.replace(str(temp),str(checkpoint))
        if finished:
            # A compact final model supports prediction while latest.pt retains optimizer state.
            final=dict(payload)
            final.pop("optimizer")
            temp=HERE/"trained_model.pt.part"
            torch.save(final,str(temp))
            os.replace(str(temp),str(HERE/"trained_model.pt"))
        history_file=out/"training.jsonl"
        tmp=out/"training.jsonl.part"
        tmp.write_text("".join(json.dumps(r)+"\n" for r in history),encoding="utf-8")
        os.replace(str(tmp),str(history_file))
        return status(completed,n,loss,finished)
    print(json.dumps(status(start_epoch,skip,partial_loss)),flush=True)
    try:
        for epoch in range(start_epoch,cfg["epochs"]):
            model.train();optimizer.zero_grad()
            pending=0
            n=skip if epoch==start_epoch else 0
            total_loss=partial_loss if epoch==start_epoch else 0.0
            def update(count):
                for p in model.parameters():
                    if p.grad is not None:p.grad.div_(count)
                torch.nn.utils.clip_grad_norm_(model.parameters(),cfg["max_grad_norm"])
                optimizer.step();optimizer.zero_grad()
            for target,x,y in examples("train",cfg,epoch,start=n):
                loss=reference_loss(model(x),y)
                if not torch.isfinite(loss):raise FloatingPointError(target["id"])
                loss.backward()
                pending+=1;n+=1;seen+=1;total_loss+=float(loss.detach())
                if pending==cfg["accumulate_targets"]:
                    update(pending);pending=0;steps+=1
                if n==100:
                    print(json.dumps(status(epoch,n,total_loss)),flush=True)
                if n==1000 or n%5000==0:
                    assert pending==0
                    print(json.dumps(save(epoch,n,total_loss)),flush=True)
                    storage_guard()
            if pending:update(pending);steps+=1
            if n!=expected_targets:raise ValueError("Training target count changed")
            history.append(dict(epoch=epoch+1,targets=n,mean_loss=total_loss/n,
                                optimizer_steps=steps,elapsed_seconds=elapsed()))
            row=save(epoch+1,0,0.0,epoch+1==cfg["epochs"])
            storage_guard();print(json.dumps(row),flush=True)
    except BaseException as error:
        # Preserve the last complete optimizer checkpoint; never label an interrupted run complete.
        atomic_json(out/"interruption.json",dict(type=type(error).__name__,message=str(error),
                    optimizer_steps=steps,targets_processed=seen,elapsed_seconds=elapsed()))
        raise

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--epochs",type=int);p.add_argument("--resume",action="store_true")
    args=p.parse_args();train(args.epochs,args.resume)
