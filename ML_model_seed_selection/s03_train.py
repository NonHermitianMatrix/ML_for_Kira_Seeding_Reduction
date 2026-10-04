"""Future training entry point. This script has not been run for the implementation task."""
import argparse, json, os, pathlib, time
import torch
from s01_data import HERE, config, examples, storage_guard, verify_sources
from s02_model import SeedSelector, reference_loss

def train(epochs=None,resume=False):
    cfg = config()
    if epochs is not None: cfg["epochs"] = epochs
    if not 1<=cfg["epochs"]<=100: raise ValueError("Epoch count must be within 1..100")
    torch.set_num_threads(cfg["cpu_threads"])
    torch.manual_seed(cfg["split_seed"])
    storage_guard()
    manifest_hash = verify_sources()
    model = SeedSelector(cfg)
    optimizer = torch.optim.AdamW(model.parameters(),lr=cfg["learning_rate"],weight_decay=cfg["weight_decay"])
    out = HERE/"runs"
    out.mkdir(exist_ok=True)
    checkpoint = out/"latest.pt"
    steps,seen,start_epoch = 0,0,0
    if checkpoint.exists():
        if not resume: raise FileExistsError("Use --resume to continue the existing run")
        saved=torch.load(str(checkpoint),map_location="cpu")
        if saved["manifest_sha256"]!=manifest_hash: raise ValueError("Checkpoint split changed")
        if any(saved["config"][k]!=v for k,v in cfg.items() if k!="epochs"):
            raise ValueError("Checkpoint configuration differs")
        model.load_state_dict(saved["model"]);optimizer.load_state_dict(saved["optimizer"])
        steps,seen,start_epoch=saved["optimizer_steps"],saved["trained_targets"],saved["epoch"]
    elif resume:
        raise FileNotFoundError(checkpoint)
    if start_epoch>=cfg["epochs"]: raise ValueError("Requested epochs already completed")
    start = time.monotonic()
    for epoch in range(start_epoch,cfg["epochs"]):
        model.train()
        optimizer.zero_grad()
        pending,total_loss,n = 0,0.0,0
        def update(count):
            # Average the gradients of the actual number of pending target examples.
            for p in model.parameters():
                if p.grad is not None: p.grad.div_(count)
            torch.nn.utils.clip_grad_norm_(model.parameters(),cfg["max_grad_norm"])
            optimizer.step()
            optimizer.zero_grad()
        for target,x,y in examples("train",cfg,epoch):
            loss = reference_loss(model(x),y)
            if not torch.isfinite(loss): raise FloatingPointError(target["id"])
            loss.backward()
            pending += 1; n += 1; seen += 1; total_loss += float(loss.detach())
            if pending==cfg["accumulate_targets"]:
                update(pending);pending=0;steps+=1
            if n%1000==0:
                print(json.dumps(dict(epoch=epoch+1,targets=n,mean_loss=total_loss/n)),flush=True)
            if n%5000==0: storage_guard()
        if pending: update(pending);steps+=1
        if not n: raise ValueError("Empty training split")
        record = dict(epoch=epoch+1,targets=n,mean_loss=total_loss/n,optimizer_steps=steps,
                      elapsed_seconds=time.monotonic()-start)
        with (out/"training.jsonl").open("a",encoding="utf-8") as f:
            f.write(json.dumps(record)+"\n")
        payload = dict(schema_version=1,status="trained",config=cfg,model=model.state_dict(),
                       optimizer=optimizer.state_dict(),optimizer_steps=steps,epoch=epoch+1,
                       manifest_sha256=manifest_hash,trained_targets=seen)
        tmp = out/"latest.pt.part"
        torch.save(payload,str(tmp))
        if tmp.stat().st_size>cfg["checkpoint_limit_bytes"]:
            tmp.unlink()
            raise RuntimeError("Checkpoint exceeds its size limit")
        os.replace(str(tmp),str(checkpoint))
        storage_guard()
        print(json.dumps(record),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--epochs",type=int)
    p.add_argument("--resume",action="store_true")
    args=p.parse_args()
    train(args.epochs,args.resume)
