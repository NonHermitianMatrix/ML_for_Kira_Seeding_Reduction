"""Continue saved weights and optimizer for twenty complete passes over expanded training data."""
import argparse,json,os,random,resource,time
import numpy as np
import torch
from s01_data import HERE,config,read,storage_guard
from s02_model import SeedSelector
from s12_prepare_features import sha,write
from s13_batch import collate,forward,verify
def savept(path,obj):
 tmp=path.with_name(path.name+".part");torch.save(obj,tmp)
 assert tmp.stat().st_size<8388608;os.replace(tmp,path)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--pilot",action="store_true");args=ap.parse_args()
 cfg=config();training_threads=cfg.get("training_cpu_threads",cfg["cpu_threads"])
 assert int(os.environ.get("NSLOTS","1"))>=training_threads
 torch.set_num_threads(training_threads);torch.set_num_interop_threads(1)
 torch.manual_seed(cfg["split_seed"]);torch.use_deterministic_algorithms(True)
 data=read(HERE/"data/manifest.json");assert data["status"]=="complete"
 assert data["split_sha256"]==sha(HERE/"split_manifest.json")
 warm=HERE/"runs/before_expansion_250/runs/all_loops_latest.pt"
 initial=torch.load(warm,map_location="cpu",weights_only=False)
 model=SeedSelector(cfg);model.load_state_dict(initial["model"])
 opt=torch.optim.AdamW(model.parameters(),lr=cfg["learning_rate"],weight_decay=cfg["weight_decay"]);opt.load_state_dict(initial["optimizer"])
 lineage=dict(checkpoint=str(warm.relative_to(HERE)),sha256=sha(warm),completed_prior_epochs=initial["epoch"],
  targets_in_prior_partial_epoch=initial.get("processed_in_epoch",0),prior_optimizer_steps=initial["optimizer_steps"],
  expanded_dataset_epochs=cfg["epochs"],previous_progress_preserved=True,prior_lineage=initial.get("lineage",{}))
 fingerprint=dict(manifest=sha(HERE/"data/manifest.json"),split=data["split_sha256"],config=sha(HERE/"config.json"),
  scripts={p.name:sha(p) for p in [HERE/"s02_model.py",HERE/"s12_prepare_features.py",HERE/"s13_batch.py",HERE/"s14_train_all_loops.py"]})
 checkpoint=HERE/"runs/all_loops_latest.pt";ep=0;next_family=0;history=[];updates=0;previous=0.
 partial=dict(targets=0,loss=0.,labels=0);started=time.time()
 if checkpoint.exists() and not args.pilot:
  saved=torch.load(checkpoint,map_location="cpu",weights_only=False);assert saved["fingerprint"]==fingerprint
  model.load_state_dict(saved["model"]);opt.load_state_dict(saved["optimizer"]);torch.set_rng_state(saved["torch_rng"])
  ep=saved["epoch"];next_family=saved["next_family"];partial=saved["partial"];history=saved["history"];updates=saved["optimizer_steps"];previous=saved["elapsed_seconds"]
 def elapsed():return previous+time.time()-started
 def payload(e,n):return dict(schema_version=3,status="training",config=cfg,model=model.state_dict(),optimizer=opt.state_dict(),
  epoch=e,next_family=n,partial=partial,history=history,optimizer_steps=updates,manifest_sha256=data["split_sha256"],
  fingerprint=fingerprint,lineage=lineage,elapsed_seconds=elapsed(),torch_rng=torch.get_rng_state(),test_targets_processed=0)
 checked=[]
 for item in [data["families"][0],data["families"][-1]]:
  with np.load(HERE/item["file"],allow_pickle=False) as archive:z={k:archive[k] for k in archive.files}
  checked.append(dict(family=item["family"],**verify(model,z)))
 write(HERE/"runs/batch_equivalence.json",dict(status="passed",checks=checked))
 if args.pilot:
  timings=[]
  for b in [8,16,32]:
   items=list(range(min(b,len(z["labels"]))));x,mask,shared,y=collate(z,items);t=time.time()
   for _ in range(10):
    opt.zero_grad(set_to_none=True);loss=torch.nn.functional.binary_cross_entropy_with_logits(forward(model,x,mask,shared),y)
    loss.backward();opt.step()
   timings.append(dict(batch=len(items),seconds_per_target=(time.time()-t)/(10*len(items))))
  write(HERE/"runs/batch_pilot.json",dict(timings=timings,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
  print(timings,flush=True);return
 for epoch in range(ep,cfg["epochs"]):
  order=list(range(len(data["families"])));random.Random(cfg["split_seed"]+epoch).shuffle(order)
  if epoch!=ep:next_family=0;partial=dict(targets=0,loss=0.,labels=0)
  model.train()
  for fi in range(next_family,len(order)):
   item=data["families"][order[fi]];path=HERE/item["file"];assert sha(path)==item["sha256"]
   with np.load(path,allow_pickle=False) as archive:z={k:archive[k] for k in archive.files}
   indices=list(range(len(z["labels"])));random.Random(cfg["split_seed"]+epoch*100003+fi).shuffle(indices)
   for start in range(0,len(indices),cfg["batch_targets"]):
    batch=indices[start:start+cfg["batch_targets"]];x,mask,shared,y=collate(z,batch)
    opt.zero_grad(set_to_none=True);logits=forward(model,x,mask,shared)
    loss=torch.nn.functional.binary_cross_entropy_with_logits(logits,y)
    if not torch.isfinite(loss):raise ValueError("Non-finite loss")
    loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),cfg["max_grad_norm"],error_if_nonfinite=True);opt.step()
    partial["targets"]+=len(batch);partial["loss"]+=float(loss.detach())*len(batch);partial["labels"]+=y.numel();updates+=1
   if fi%16==0 or fi+1==len(order):
    savept(checkpoint,payload(epoch,fi+1))
    write(HERE/"runs/training_status.json",dict(status="training",completed_epochs=epoch,configured_epochs=cfg["epochs"],
      targets_in_current_epoch=partial["targets"],training_targets_per_epoch=data["training_targets"],
      families_completed=fi+1,families_total=len(order),mean_training_loss=partial["loss"]/partial["targets"],
      elapsed_seconds=elapsed(),optimizer_steps=updates,test_targets_processed=0,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
  assert partial["targets"]==data["training_targets"]
  history.append(dict(epoch=epoch+1,targets=partial["targets"],mean_loss=partial["loss"]/partial["targets"],
       optimizer_steps=updates,elapsed_seconds=elapsed()))
  print(json.dumps(history[-1]),flush=True)
  partial=dict(targets=0,loss=0.,labels=0);savept(checkpoint,payload(epoch+1,0));write(HERE/"runs/all_loops_history.json",history)
  storage_guard()
 final=payload(cfg["epochs"],0);final["status"]="trained";savept(checkpoint,final)
 final.pop("optimizer");savept(HERE/"trained_model.pt",final)
 result=dict(status="trained_testing_deferred",epochs_completed=cfg["epochs"],model_sha256=sha(HERE/"trained_model.pt"),
  parameter_count=sum(p.numel() for p in model.parameters()),lineage=lineage,history=history,
  training_targets=data["training_targets"],training_families=data["training_families"],
  held_out_targets=data["held_out_targets"],held_out_families=data["held_out_families"],
  optimizer_steps=updates,elapsed_seconds=elapsed(),test_data_used=False,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
  training_cpu_threads=training_threads,inference_cpu_threads=cfg["cpu_threads"],
  batch_targets=cfg["batch_targets"],batch_execution="same architecture, features, ordered pairs and per-target BCE; masked batches",
  model_bytes=(HERE/"trained_model.pt").stat().st_size)
 write(HERE/"trained_model.json",result);write(HERE/"runs/training_status.json",dict(result,status="complete"))
 print("All-loop seed training complete",result["model_sha256"],flush=True)
if __name__=="__main__":main()
